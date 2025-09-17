"""
Market Analysis Tools using Agno v2 Pattern

This module implements API integrations as Agno v2 Tool classes
for FRED economic data and Exa news search.
"""

import os
import asyncio
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import logging
from fredapi import Fred
from exa_py import Exa
from agno.tools import Toolkit

# Configure logging
logger = logging.getLogger(__name__)


class FredDataTools(Toolkit):
    """FRED economic data integration with proper error handling using Agno v2 patterns."""

    def __init__(self, **kwargs):
        """Initialize FRED API client with environment variable for API key."""
        api_key = os.getenv('FRED_API_KEY')
        if not api_key:
            raise ValueError("FRED_API_KEY environment variable not set")

        self.fred = Fred(api_key=api_key)

        # Define the indicators we'll fetch
        self.indicators = {
            'DFF': 'federal_funds_rate',
            'CPIAUCSL': 'inflation_rate',
            'GDP': 'gdp_growth',
            'UNRATE': 'unemployment_rate'
        }

        # Register tool methods with Toolkit
        tools = [
            self.get_economic_indicators,
            self.get_single_indicator
        ]

        super().__init__(
            name="fred_data_tools",
            tools=tools,
            **kwargs
        )

    async def get_economic_indicators(self, indicator_list: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Fetch multiple economic indicators with parallel processing and error handling.

        Args:
            indicator_list: Optional list of indicator IDs to fetch.
                          If None, fetches all default indicators.

        Returns:
            Dictionary containing economic data, errors, and timestamp
        """
        results = {}
        errors = []

        # Use provided list or default indicators
        indicators_to_fetch = indicator_list or list(self.indicators.keys())

        async def fetch_indicator(indicator_id: str) -> None:
            """Fetch a single indicator with timeout and error handling."""
            try:
                # Use asyncio timeout for each API call (30 seconds)
                async with asyncio.timeout(30):
                    # Run blocking FRED API call in thread pool
                    data = await asyncio.to_thread(
                        self._fetch_fred_series,
                        indicator_id
                    )

                    # Map indicator ID to friendly name
                    series_name = self.indicators.get(indicator_id, indicator_id)
                    results[series_name] = {
                        'data': data,
                        'last_updated': datetime.now().isoformat(),
                        'source': f'FRED/{indicator_id}',
                        'indicator_id': indicator_id
                    }
                    logger.info(f"Successfully fetched {series_name} ({indicator_id})")

            except asyncio.TimeoutError:
                error_msg = f"FRED API timeout for {indicator_id}"
                errors.append(error_msg)
                logger.warning(error_msg)
            except Exception as e:
                error_msg = f"FRED API error for {indicator_id}: {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg)

        # Fetch all indicators in parallel
        tasks = [fetch_indicator(ind_id) for ind_id in indicators_to_fetch]
        await asyncio.gather(*tasks, return_exceptions=True)

        return {
            'economic_data': results,
            'errors': errors,
            'timestamp': datetime.now().isoformat(),
            'success': len(results) > 0
        }

    def _fetch_fred_series(self, series_id: str, limit: int = 12) -> Dict[str, Any]:
        """
        Synchronous helper to fetch FRED series data.

        Args:
            series_id: FRED series identifier
            limit: Number of most recent data points to fetch

        Returns:
            Dictionary with series data and metadata
        """
        try:
            # Get series data
            series_data = self.fred.get_series(series_id, limit=limit)

            # Get series info for metadata
            series_info = self.fred.get_series_info(series_id)

            # Convert pandas Series to list of dicts for JSON serialization
            data_points = []
            for date, value in series_data.items():
                data_points.append({
                    'date': date.isoformat() if hasattr(date, 'isoformat') else str(date),
                    'value': float(value) if value is not None else None
                })

            return {
                'values': data_points,
                'units': series_info.get('units', 'Unknown'),
                'title': series_info.get('title', series_id),
                'frequency': series_info.get('frequency', 'Unknown'),
                'last_updated': series_info.get('last_updated', 'Unknown')
            }
        except Exception as e:
            logger.error(f"Error fetching FRED series {series_id}: {e}")
            raise

    async def get_single_indicator(self, indicator_id: str) -> Dict[str, Any]:
        """
        Fetch a single economic indicator.

        Args:
            indicator_id: FRED series ID to fetch

        Returns:
            Dictionary with indicator data or error
        """
        return await self.get_economic_indicators([indicator_id])


class ExaSearchTools(Toolkit):
    """Exa neural search integration for portfolio-relevant news using Agno v2 patterns."""

    def __init__(self, **kwargs):
        """Initialize Exa API client with environment variable for API key."""
        api_key = os.getenv('EXA_API_KEY')
        if not api_key:
            raise ValueError("EXA_API_KEY environment variable not set")

        self.exa = Exa(api_key=api_key)

        # Trusted financial news domains
        self.trusted_domains = [
            'bloomberg.com',
            'reuters.com',
            'wsj.com',
            'cnbc.com',
            'ft.com',
            'marketwatch.com',
            'yahoo.com/finance',
            'investing.com'
        ]

        # Register tool methods with Toolkit
        tools = [
            self.search_portfolio_news,
            self.search_general_market_news
        ]

        super().__init__(
            name="exa_search_tools",
            tools=tools,
            **kwargs
        )

    async def search_portfolio_news(
        self,
        query: str,
        portfolio_tickers: List[str],
        num_results: int = 5
    ) -> Dict[str, Any]:
        """
        Search for news relevant to portfolio holdings with error handling.

        Args:
            query: User's market analysis query
            portfolio_tickers: List of stock tickers in the portfolio
            num_results: Number of results to return (default: 5)

        Returns:
            Dictionary containing news results, query used, and metadata
        """
        try:
            # Enhance query with portfolio context
            ticker_context = ' OR '.join(portfolio_tickers[:5])  # Limit to top 5 tickers
            enhanced_query = f"{query} ({ticker_context}) market analysis financial news"

            logger.info(f"Searching Exa with query: {enhanced_query[:100]}...")

            # Execute search with timeout
            async with asyncio.timeout(30):
                results = await asyncio.to_thread(
                    self._perform_exa_search,
                    enhanced_query,
                    num_results
                )

            # Process and score results
            processed_results = []
            for result in results:
                processed_results.append({
                    'title': result.get('title', 'No title'),
                    'url': result.get('url', ''),
                    'snippet': self._extract_snippet(result.get('text', ''), 500),
                    'published_date': result.get('published_date', None),
                    'author': result.get('author', None),
                    'score': result.get('score', 0),
                    'portfolio_relevance': self._assess_portfolio_relevance(
                        result.get('text', ''),
                        portfolio_tickers
                    )
                })

            # Sort by relevance score
            processed_results.sort(key=lambda x: x['score'], reverse=True)

            return {
                'news_results': processed_results,
                'query_used': enhanced_query,
                'timestamp': datetime.now().isoformat(),
                'total_results': len(processed_results),
                'success': True
            }

        except asyncio.TimeoutError:
            logger.warning("Exa search timed out")
            return {
                'error': 'News search timed out after 30 seconds',
                'news_results': [],
                'timestamp': datetime.now().isoformat(),
                'success': False
            }
        except Exception as e:
            logger.error(f"Exa search failed: {str(e)}")
            return {
                'error': f'News search failed: {str(e)}',
                'news_results': [],
                'timestamp': datetime.now().isoformat(),
                'success': False
            }

    def _perform_exa_search(self, query: str, num_results: int) -> List[Dict]:
        """
        Synchronous helper to perform Exa search.

        Args:
            query: Enhanced search query
            num_results: Number of results to fetch

        Returns:
            List of search results
        """
        try:
            # Perform search with Exa
            # Note: Domain filtering is currently disabled as it's too restrictive
            # and returns no results for many queries
            search_response = self.exa.search(
                query,
                num_results=num_results,
                # include_domains=self.trusted_domains,  # Temporarily disabled
                use_autoprompt=True,  # Let Exa optimize the query
                type="neural"  # Use neural search for better relevance
            )

            # Extract results
            results = []
            if hasattr(search_response, 'results'):
                for result in search_response.results:
                    results.append({
                        'title': getattr(result, 'title', ''),
                        'url': getattr(result, 'url', ''),
                        'text': getattr(result, 'text', ''),
                        'score': getattr(result, 'score', 0),
                        'published_date': getattr(result, 'published_date', None),
                        'author': getattr(result, 'author', None)
                    })

            return results

        except Exception as e:
            logger.error(f"Exa search error: {e}")
            raise

    def _extract_snippet(self, text: str, max_length: int) -> str:
        """
        Extract a snippet from the text.

        Args:
            text: Full text content
            max_length: Maximum snippet length

        Returns:
            Truncated snippet
        """
        if not text:
            return ""

        # Clean and truncate
        cleaned = text.strip()
        if len(cleaned) <= max_length:
            return cleaned

        # Try to break at sentence boundary
        truncated = cleaned[:max_length]
        last_period = truncated.rfind('.')
        if last_period > max_length * 0.8:  # If we have a period near the end
            return truncated[:last_period + 1]

        return truncated + "..."

    def _assess_portfolio_relevance(self, text: str, tickers: List[str]) -> str:
        """
        Assess how relevant news is to portfolio holdings.

        Args:
            text: News article text
            tickers: List of portfolio tickers

        Returns:
            Relevance level: 'high', 'medium', or 'low'
        """
        if not text:
            return 'low'

        text_lower = text.lower()
        ticker_mentions = 0

        for ticker in tickers:
            # Look for ticker mentions (case insensitive)
            ticker_lower = ticker.lower()
            if ticker_lower in text_lower:
                ticker_mentions += 1

            # Also check for company name patterns (simplified)
            # This could be enhanced with a ticker-to-company-name mapping
            if f" {ticker_lower} " in text_lower or f"({ticker_lower})" in text_lower:
                ticker_mentions += 1

        # Determine relevance based on mentions
        if ticker_mentions >= 3:
            return 'high'
        elif ticker_mentions >= 1:
            return 'medium'
        else:
            return 'low'

    async def search_general_market_news(self, query: str, num_results: int = 5) -> Dict[str, Any]:
        """
        Search for general market news without portfolio context.

        Args:
            query: Search query
            num_results: Number of results to return

        Returns:
            Dictionary containing news results
        """
        # Use empty portfolio list for general search
        return await self.search_portfolio_news(query, [], num_results)


# Simple retry decorator for resilience
def retry_with_backoff(max_attempts: int = 3, initial_delay: float = 1.0):
    """
    Decorator to retry a function with exponential backoff.

    Args:
        max_attempts: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            delay = initial_delay
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                        await asyncio.sleep(delay)
                        delay *= 2  # Exponential backoff
                    else:
                        logger.error(f"All {max_attempts} attempts failed")

            raise last_exception

        return wrapper
    return decorator