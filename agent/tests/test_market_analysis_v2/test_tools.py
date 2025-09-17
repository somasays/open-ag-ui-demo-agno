"""
Unit tests for Market Analysis v2 API Tools

Tests FRED and Exa API integrations with mocked responses,
error handling, timeouts, and retry logic.
"""

import os
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime
import pandas as pd

# Set test environment variables before importing tools
os.environ['FRED_API_KEY'] = 'test-fred-key'
os.environ['EXA_API_KEY'] = 'test-exa-key'

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from market_analysis_v2.tools import FredDataTools, ExaSearchTools


class TestFredDataTools:
    """Test suite for FRED API integration."""

    @pytest.fixture
    def fred_tools(self):
        """Create FredDataTools instance with mocked client."""
        with patch('market_analysis_v2.tools.Fred') as mock_fred_class, \
             patch('market_analysis_v2.tools.Toolkit.__init__', return_value=None):
            mock_fred = Mock()
            mock_fred_class.return_value = mock_fred
            tools = FredDataTools()
            tools.fred = mock_fred
            yield tools

    @pytest.mark.asyncio
    async def test_get_economic_indicators_success(self, fred_tools):
        """Test successful fetching of all economic indicators."""
        # Mock FRED responses
        mock_series_data = pd.Series({
            pd.Timestamp('2024-01-01'): 5.25,
            pd.Timestamp('2024-02-01'): 5.30,
            pd.Timestamp('2024-03-01'): 5.35
        })

        mock_series_info = {
            'units': 'Percent',
            'title': 'Federal Funds Effective Rate',
            'frequency': 'Monthly',
            'last_updated': '2024-03-15'
        }

        fred_tools.fred.get_series.return_value = mock_series_data
        fred_tools.fred.get_series_info.return_value = mock_series_info

        # Execute
        result = await fred_tools.get_economic_indicators()

        # Assert
        assert result['success'] is True
        assert 'economic_data' in result
        assert len(result['economic_data']) == 4  # All 4 indicators
        assert result['errors'] == []

        # Check data structure
        for key in result['economic_data'].values():
            assert 'data' in key
            assert 'last_updated' in key
            assert 'source' in key
            assert 'indicator_id' in key

    @pytest.mark.asyncio
    async def test_get_economic_indicators_partial_failure(self, fred_tools):
        """Test handling of partial API failures."""
        # Mock mixed responses
        def side_effect(series_id, *args, **kwargs):
            if series_id == 'DFF':
                return pd.Series({pd.Timestamp('2024-01-01'): 5.25})
            else:
                raise Exception(f"API error for {series_id}")

        fred_tools.fred.get_series.side_effect = side_effect
        fred_tools.fred.get_series_info.return_value = {'units': 'Percent'}

        # Execute
        result = await fred_tools.get_economic_indicators(['DFF', 'GDP'])

        # Assert
        assert result['success'] is True  # Partial success
        assert len(result['economic_data']) == 1  # Only DFF succeeded
        assert len(result['errors']) == 1  # GDP failed
        assert 'GDP' in result['errors'][0]

    @pytest.mark.asyncio
    async def test_get_economic_indicators_timeout(self, fred_tools):
        """Test timeout handling for slow API calls."""
        # Mock the timeout context manager to raise TimeoutError immediately
        with patch('market_analysis_v2.tools.asyncio.timeout') as mock_timeout:
            # Make the context manager raise TimeoutError
            mock_timeout.return_value.__aenter__.side_effect = asyncio.TimeoutError()

            # Execute
            result = await fred_tools.get_economic_indicators(['DFF'])

            # Assert
            assert result['success'] is False
            assert len(result['errors']) == 1
            assert 'timeout' in result['errors'][0].lower()

    @pytest.mark.asyncio
    async def test_get_single_indicator(self, fred_tools):
        """Test fetching a single economic indicator."""
        # Mock response
        fred_tools.fred.get_series.return_value = pd.Series({
            pd.Timestamp('2024-01-01'): 3.5
        })
        fred_tools.fred.get_series_info.return_value = {
            'units': 'Percent',
            'title': 'Unemployment Rate'
        }

        # Execute
        result = await fred_tools.get_single_indicator('UNRATE')

        # Assert
        assert result['success'] is True
        assert len(result['economic_data']) == 1

    def test_init_without_api_key(self):
        """Test initialization fails without API key."""
        # Remove API key
        original = os.environ.pop('FRED_API_KEY', None)

        try:
            # Should raise ValueError
            with pytest.raises(ValueError) as exc_info:
                FredDataTools()
            assert "FRED_API_KEY" in str(exc_info.value)
        finally:
            # Restore API key
            if original:
                os.environ['FRED_API_KEY'] = original


class TestExaSearchTools:
    """Test suite for Exa API integration."""

    @pytest.fixture
    def exa_tools(self):
        """Create ExaSearchTools instance with mocked client."""
        with patch('market_analysis_v2.tools.Exa') as mock_exa_class, \
             patch('market_analysis_v2.tools.Toolkit.__init__', return_value=None):
            mock_exa = Mock()
            mock_exa_class.return_value = mock_exa
            tools = ExaSearchTools()
            tools.exa = mock_exa
            yield tools

    @pytest.mark.asyncio
    async def test_search_portfolio_news_success(self, exa_tools):
        """Test successful news search with portfolio context."""
        # Mock Exa response
        mock_result = Mock()
        mock_result.title = "Apple Reports Strong Q4 Earnings"
        mock_result.url = "https://bloomberg.com/apple-earnings"
        mock_result.text = "Apple Inc. reported record revenue in Q4..."
        mock_result.score = 0.95
        mock_result.published_date = "2024-03-15"
        mock_result.author = "John Doe"

        mock_response = Mock()
        mock_response.results = [mock_result]

        exa_tools.exa.search.return_value = mock_response

        # Execute
        result = await exa_tools.search_portfolio_news(
            query="tech earnings",
            portfolio_tickers=["AAPL", "MSFT", "GOOGL"],
            num_results=3
        )

        # Assert
        assert result['success'] is True
        assert len(result['news_results']) == 1
        assert result['news_results'][0]['title'] == "Apple Reports Strong Q4 Earnings"
        assert result['news_results'][0]['portfolio_relevance'] in ['high', 'medium', 'low']
        assert 'query_used' in result
        assert 'AAPL' in result['query_used']

    @pytest.mark.asyncio
    async def test_search_portfolio_news_timeout(self, exa_tools):
        """Test timeout handling for slow Exa API."""
        # Mock the timeout context manager to raise TimeoutError
        with patch('market_analysis_v2.tools.asyncio.timeout') as mock_timeout:
            mock_timeout.return_value.__aenter__.side_effect = asyncio.TimeoutError()

            # Execute
            result = await exa_tools.search_portfolio_news(
                query="market news",
                portfolio_tickers=["AAPL"],
                num_results=5
            )

            # Assert
            assert result['success'] is False
            assert 'error' in result
            assert 'timed out' in result['error'].lower()
            assert result['news_results'] == []

    @pytest.mark.asyncio
    async def test_search_portfolio_news_api_error(self, exa_tools):
        """Test error handling for API failures."""
        # Mock API error
        exa_tools.exa.search.side_effect = Exception("API rate limit exceeded")

        # Execute
        result = await exa_tools.search_portfolio_news(
            query="market analysis",
            portfolio_tickers=["TSLA"],
            num_results=5
        )

        # Assert
        assert result['success'] is False
        assert 'error' in result
        assert 'rate limit' in result['error'].lower()

    def test_assess_portfolio_relevance(self, exa_tools):
        """Test portfolio relevance scoring."""
        # Test high relevance
        text_high = "Apple (AAPL) and Microsoft (MSFT) announced partnership. GOOGL also involved."
        relevance = exa_tools._assess_portfolio_relevance(
            text_high,
            ["AAPL", "MSFT", "GOOGL"]
        )
        assert relevance == 'high'

        # Test medium relevance (requires ticker mention)
        text_medium = "AAPL announced new product launch affecting market."
        relevance = exa_tools._assess_portfolio_relevance(
            text_medium,
            ["AAPL", "MSFT"]
        )
        assert relevance == 'medium'

        # Test low relevance
        text_low = "General market news about inflation."
        relevance = exa_tools._assess_portfolio_relevance(
            text_low,
            ["AAPL", "MSFT"]
        )
        assert relevance == 'low'

    def test_extract_snippet(self, exa_tools):
        """Test snippet extraction."""
        # Test short text
        short_text = "This is short."
        snippet = exa_tools._extract_snippet(short_text, 100)
        assert snippet == short_text

        # Test truncation
        long_text = "A" * 600
        snippet = exa_tools._extract_snippet(long_text, 500)
        assert len(snippet) <= 503  # 500 + "..."
        assert snippet.endswith("...")

        # Test sentence boundary
        text_with_periods = "First sentence. " * 30
        snippet = exa_tools._extract_snippet(text_with_periods, 100)
        assert snippet.endswith(".")

    @pytest.mark.asyncio
    async def test_search_general_market_news(self, exa_tools):
        """Test general market news search without portfolio context."""
        # Mock response
        mock_response = Mock()
        mock_response.results = []
        exa_tools.exa.search.return_value = mock_response

        # Execute
        result = await exa_tools.search_general_market_news(
            query="federal reserve policy",
            num_results=5
        )

        # Assert
        assert 'news_results' in result
        # Should not have ticker context in query
        call_args = exa_tools.exa.search.call_args
        assert call_args[0][0]  # Query should exist
        # Portfolio context should be empty


class TestRetryMechanism:
    """Test retry with exponential backoff decorator."""

    @pytest.mark.asyncio
    async def test_retry_success_after_failures(self):
        """Test retry succeeds after initial failures."""
        from market_analysis_v2.tools import retry_with_backoff

        call_count = 0

        @retry_with_backoff(max_attempts=3, initial_delay=0.01)
        async def flaky_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary failure")
            return "success"

        # Execute
        result = await flaky_function()

        # Assert
        assert result == "success"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_retry_all_attempts_fail(self):
        """Test retry fails after all attempts."""
        from market_analysis_v2.tools import retry_with_backoff

        @retry_with_backoff(max_attempts=3, initial_delay=0.01)
        async def always_fails():
            raise Exception("Permanent failure")

        # Execute and assert
        with pytest.raises(Exception) as exc_info:
            await always_fails()
        assert "Permanent failure" in str(exc_info.value)


# Integration test with both tools
class TestIntegration:
    """Integration tests for combined tool usage."""

    @pytest.mark.asyncio
    async def test_parallel_api_calls(self):
        """Test parallel execution of FRED and Exa calls."""
        with patch('market_analysis_v2.tools.Fred'), \
             patch('market_analysis_v2.tools.Exa'), \
             patch('market_analysis_v2.tools.Toolkit.__init__', return_value=None):

            fred_tools = FredDataTools()
            exa_tools = ExaSearchTools()

            # Mock responses
            with patch.object(fred_tools, 'get_economic_indicators') as mock_fred, \
                 patch.object(exa_tools, 'search_portfolio_news') as mock_exa:

                mock_fred.return_value = {
                    'success': True,
                    'economic_data': {'federal_funds_rate': {}}
                }
                mock_exa.return_value = {
                    'success': True,
                    'news_results': []
                }

                # Execute in parallel
                fred_task = fred_tools.get_economic_indicators()
                exa_task = exa_tools.search_portfolio_news(
                    "test query",
                    ["AAPL"],
                    5
                )

                results = await asyncio.gather(fred_task, exa_task)

                # Assert both completed
                assert len(results) == 2
                assert results[0]['success'] is True
                assert results[1]['success'] is True