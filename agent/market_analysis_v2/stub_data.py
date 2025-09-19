"""
Market Analysis V2 - Stub Data Generator
Generates realistic mock data for market analysis features to support frontend development
"""

import random
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import uuid

class MarketAnalysisStubData:
    """Generate realistic stub data for market analysis workflow"""

    def __init__(self):
        # Sample economic indicators (realistic values as of 2024)
        self.economic_base_values = {
            "federal_funds_rate": 5.33,
            "inflation_rate": 3.1,
            "gdp_growth": 2.8,
            "unemployment_rate": 3.7
        }

        # Sample news sources for realistic articles
        self.news_sources = [
            "Reuters", "Bloomberg", "Wall Street Journal", "CNBC",
            "MarketWatch", "Financial Times", "Yahoo Finance"
        ]

        # Sample portfolio tickers for context
        self.common_tickers = [
            "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA",
            "JPM", "JNJ", "PG", "V", "UNH", "HD", "DIS", "MA"
        ]

        # Market analysis templates for realistic insights
        self.economic_insights = {
            "fed_rate_high": "Rising interest rates typically pressure growth stocks while benefiting financial sector holdings.",
            "inflation_moderate": "Current inflation levels suggest continued monetary policy vigilance affecting rate-sensitive investments.",
            "gdp_growth_stable": "Steady GDP growth supports overall market sentiment with sector rotation opportunities.",
            "unemployment_low": "Low unemployment indicates economic strength but may pressure wage costs for labor-intensive companies."
        }

        self.news_templates = [
            {
                "title_template": "Fed Signals {action} in {timeframe} as {indicator} {trend}",
                "snippet_template": "Federal Reserve officials indicated potential {action} following recent {indicator} data showing {trend}..."
            },
            {
                "title_template": "{sector} Stocks {movement} on {catalyst} Concerns",
                "snippet_template": "Technology sector experienced {movement} following {catalyst} developments that could impact growth prospects..."
            },
            {
                "title_template": "Market Outlook: {sentiment} Signals from {source} Data",
                "snippet_template": "Recent {source} indicators suggest {sentiment} market conditions with implications for risk assets..."
            }
        ]

    def generate_economic_data(self, delay_simulation: bool = True) -> Dict[str, Any]:
        """Generate realistic economic data resembling FRED API responses"""

        if delay_simulation:
            # Simulate FRED API call delay
            time.sleep(random.uniform(2, 5))

        current_date = datetime.now()

        economic_data = {
            "federal_funds_rate": {
                "value": round(self.economic_base_values["federal_funds_rate"] + random.uniform(-0.5, 0.5), 2),
                "change": round(random.uniform(-0.25, 0.25), 2),
                "date": current_date.strftime("%Y-%m-%d"),
                "trend": random.choice(["up", "down", "stable"]),
                "confidence": round(random.uniform(0.7, 0.95), 2)
            },
            "inflation_rate": {
                "value": round(self.economic_base_values["inflation_rate"] + random.uniform(-0.3, 0.3), 1),
                "change": round(random.uniform(-0.2, 0.2), 1),
                "date": (current_date - timedelta(days=30)).strftime("%Y-%m-%d"),
                "trend": random.choice(["up", "down", "stable"]),
                "confidence": round(random.uniform(0.8, 0.9), 2)
            },
            "gdp_growth": {
                "value": round(self.economic_base_values["gdp_growth"] + random.uniform(-0.5, 0.5), 1),
                "change": round(random.uniform(-0.3, 0.3), 1),
                "date": (current_date - timedelta(days=90)).strftime("%Y-Q4"),
                "trend": random.choice(["up", "down", "stable"]),
                "confidence": round(random.uniform(0.75, 0.85), 2)
            },
            "unemployment_rate": {
                "value": round(self.economic_base_values["unemployment_rate"] + random.uniform(-0.2, 0.2), 1),
                "change": round(random.uniform(-0.1, 0.1), 1),
                "date": (current_date - timedelta(days=30)).strftime("%Y-%m-%d"),
                "trend": random.choice(["up", "down", "stable"]),
                "confidence": round(random.uniform(0.85, 0.95), 2)
            },
            "data_freshness": current_date.isoformat(),
            "source_citations": [
                {
                    "source": "FRED",
                    "url": "https://fred.stlouisfed.org/series/DFF",
                    "description": "Federal Funds Effective Rate",
                    "accessed_at": current_date.isoformat()
                },
                {
                    "source": "FRED",
                    "url": "https://fred.stlouisfed.org/series/CPIAUCSL",
                    "description": "Consumer Price Index for All Urban Consumers",
                    "accessed_at": current_date.isoformat()
                }
            ]
        }

        return economic_data

    def generate_news_analysis(self, portfolio_tickers: List[str], query: str = "", delay_simulation: bool = True) -> Dict[str, Any]:
        """Generate realistic news analysis resembling Exa API responses"""

        if delay_simulation:
            # Simulate Exa search delay
            time.sleep(random.uniform(3, 7))

        # Use provided tickers or fallback to sample
        tickers = portfolio_tickers if portfolio_tickers else random.sample(self.common_tickers, 3)

        articles = []
        for i in range(random.randint(3, 5)):
            template = random.choice(self.news_templates)

            article = {
                "title": self._generate_news_title(template["title_template"]),
                "source": random.choice(self.news_sources),
                "url": f"https://example.com/article-{uuid.uuid4().hex[:8]}",
                "snippet": self._generate_news_snippet(template["snippet_template"]),
                "relevance_score": round(random.uniform(0.6, 0.95), 2),
                "published_date": (datetime.now() - timedelta(days=random.randint(0, 7))).isoformat(),
                "portfolio_tickers": random.sample(tickers, random.randint(1, min(3, len(tickers)))),
                "sentiment": random.choice(["positive", "negative", "neutral"])
            }
            articles.append(article)

        # Calculate sentiment distribution
        sentiment_counts = {"positive": 0, "neutral": 0, "negative": 0}
        for article in articles:
            sentiment_counts[article["sentiment"]] += 1

        total_articles = len(articles)
        sentiment_percentages = {
            k: round((v / total_articles) * 100) for k, v in sentiment_counts.items()
        }

        news_analysis = {
            "articles": articles,
            "sentiment_summary": {
                **sentiment_percentages,
                "overall_tone": self._determine_overall_tone(sentiment_percentages)
            },
            "portfolio_relevance": {
                "high": sum(1 for a in articles if a["relevance_score"] > 0.8),
                "medium": sum(1 for a in articles if 0.6 <= a["relevance_score"] <= 0.8),
                "low": sum(1 for a in articles if a["relevance_score"] < 0.6),
                "coverage_score": round(random.uniform(0.6, 0.9), 2)
            },
            "search_metadata": {
                "query_used": f"{query} {' '.join(tickers)} market analysis",
                "total_results": len(articles),
                "search_time_ms": random.randint(800, 2500),
                "filters_applied": ["financial_news", "last_7_days", "english"]
            }
        }

        return news_analysis

    def generate_portfolio_impact(self, portfolio_tickers: List[str], economic_data: Dict, news_data: Dict, delay_simulation: bool = True) -> Dict[str, Any]:
        """Generate portfolio impact analysis based on economic and news data"""

        if delay_simulation:
            # Simulate analysis processing delay
            time.sleep(random.uniform(4, 8))

        holdings_impact = []

        for ticker in portfolio_tickers:
            impact = {
                "ticker": ticker,
                "impact_level": random.choice(["high", "medium", "low"]),
                "impact_score": round(random.uniform(0.3, 0.9), 2),
                "reasoning": self._generate_impact_reasoning(ticker, economic_data),
                "recommended_action": random.choice(["buy", "sell", "hold", "watch"]),
                "confidence": round(random.uniform(0.6, 0.9), 2),
                "factors": self._generate_impact_factors(ticker, economic_data, news_data)
            }
            holdings_impact.append(impact)

        portfolio_impact = {
            "holdings_impact": holdings_impact,
            "overall_risk_assessment": {
                "level": random.choice(["low", "medium", "high"]),
                "score": round(random.uniform(0.2, 0.8), 2),
                "description": "Current market conditions present moderate opportunities with manageable risks.",
                "time_horizon": "medium-term"
            },
            "recommended_actions": [
                {
                    "action_type": random.choice(["rebalance", "hedge", "monitor", "research"]),
                    "priority": random.choice(["urgent", "important", "normal"]),
                    "description": "Consider rebalancing tech exposure given rate environment.",
                    "affected_tickers": random.sample(portfolio_tickers, min(2, len(portfolio_tickers))),
                    "estimated_impact": "2-5% portfolio adjustment"
                }
            ],
            "confidence_scores": {
                "economic_analysis": round(random.uniform(0.7, 0.9), 2),
                "news_sentiment": round(random.uniform(0.6, 0.8), 2),
                "portfolio_impact": round(random.uniform(0.65, 0.85), 2),
                "overall_assessment": round(random.uniform(0.7, 0.85), 2)
            },
            "market_outlook": {
                "short_term": random.choice(["bullish", "bearish", "neutral"]),
                "medium_term": random.choice(["bullish", "bearish", "neutral"]),
                "key_drivers": ["Federal Reserve policy", "Inflation trends", "Corporate earnings"],
                "major_risks": ["Geopolitical tensions", "Rate volatility", "Market liquidity"]
            }
        }

        return portfolio_impact

    def _generate_news_title(self, template: str) -> str:
        """Generate realistic news title from template"""
        replacements = {
            "{action}": random.choice(["rate cuts", "policy shifts", "dovish stance"]),
            "{timeframe}": random.choice(["Q2 2024", "next quarter", "coming months"]),
            "{indicator}": random.choice(["employment", "inflation", "GDP"]),
            "{trend}": random.choice(["rises", "falls", "stabilizes"]),
            "{sector}": random.choice(["Technology", "Financial", "Energy", "Healthcare"]),
            "{movement}": random.choice(["rally", "decline", "mixed trading"]),
            "{catalyst}": random.choice(["earnings", "regulation", "market sentiment"]),
            "{sentiment}": random.choice(["positive", "cautious", "mixed"]),
            "{source}": random.choice(["employment", "retail sales", "manufacturing"])
        }

        result = template
        for placeholder, value in replacements.items():
            result = result.replace(placeholder, value)
        return result

    def _generate_news_snippet(self, template: str) -> str:
        """Generate realistic news snippet from template"""
        replacements = {
            "{action}": random.choice(["policy accommodation", "rate adjustments", "market intervention"]),
            "{indicator}": random.choice(["employment data", "inflation metrics", "GDP figures"]),
            "{trend}": random.choice(["improvement", "deterioration", "stabilization"]),
            "{movement}": random.choice(["strong gains", "notable declines", "sideways movement"]),
            "{catalyst}": random.choice(["regulatory changes", "earnings results", "economic data"]),
            "{sentiment}": random.choice(["optimistic", "cautious", "neutral"]),
            "{source}": random.choice(["economic indicators", "market data", "policy signals"])
        }

        result = template
        for placeholder, value in replacements.items():
            result = result.replace(placeholder, value)
        return result[:200] + "..."

    def _determine_overall_tone(self, sentiment_percentages: Dict[str, int]) -> str:
        """Determine overall market tone from sentiment distribution"""
        if sentiment_percentages["positive"] > 50:
            return "bullish"
        elif sentiment_percentages["negative"] > 50:
            return "bearish"
        else:
            return "neutral"

    def _generate_impact_reasoning(self, ticker: str, economic_data: Dict) -> str:
        """Generate reasoning for portfolio impact"""
        sector_map = {
            "AAPL": "Technology companies may face pressure from rising rates affecting growth valuations.",
            "MSFT": "Enterprise software benefits from economic resilience but faces rate sensitivity.",
            "JPM": "Financial institutions typically benefit from rising interest rate environments.",
            "JNJ": "Healthcare remains defensive with stable demand regardless of economic conditions.",
            "TSLA": "Growth companies face headwinds from higher discount rates on future cash flows."
        }

        return sector_map.get(ticker, f"{ticker} positioning reflects current economic environment impacts.")

    def _generate_impact_factors(self, ticker: str, economic_data: Dict, news_data: Dict) -> List[str]:
        """Generate contributing factors for impact assessment"""
        base_factors = [
            "Interest rate environment",
            "Sector rotation trends",
            "Earnings expectations",
            "Market sentiment"
        ]

        # Add specific factors based on economic data
        if economic_data.get("federal_funds_rate", {}).get("trend") == "up":
            base_factors.append("Rising rate pressure")

        return random.sample(base_factors, random.randint(3, 4))

    def generate_complete_analysis(self, portfolio_tickers: List[str], query: str = "", enable_delays: bool = True) -> Dict[str, Any]:
        """Generate complete market analysis with all components"""

        print(f"🔍 Starting market analysis for query: '{query}'")
        print(f"📊 Portfolio context: {portfolio_tickers}")

        # Step 1: Economic Data
        print("📈 Fetching economic indicators...")
        economic_data = self.generate_economic_data(delay_simulation=enable_delays)

        # Step 2: News Analysis
        print("📰 Searching relevant news...")
        news_analysis = self.generate_news_analysis(portfolio_tickers, query, delay_simulation=enable_delays)

        # Step 3: Portfolio Impact
        print("🎯 Analyzing portfolio impact...")
        portfolio_impact = self.generate_portfolio_impact(portfolio_tickers, economic_data, news_analysis, delay_simulation=enable_delays)

        print("✅ Market analysis complete!")

        return {
            "status": "success",
            "economic_data": economic_data,
            "news_analysis": news_analysis,
            "portfolio_impact": portfolio_impact,
            "processing_time_ms": random.randint(45000, 90000),  # 45-90 seconds
            "timestamp": datetime.now().isoformat()
        }

    def simulate_streaming_events(self, portfolio_tickers: List[str], query: str = "") -> List[Dict[str, Any]]:
        """Generate AG-UI compatible streaming events for realistic frontend testing"""

        events = []

        # Run started event
        events.append({
            "type": "RUN_STARTED",
            "thread_id": str(uuid.uuid4()),
            "run_id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat()
        })

        # Initial state snapshot
        events.append({
            "type": "STATE_SNAPSHOT",
            "snapshot": {
                "market_analysis": {
                    "analysis_status": "analyzing",
                    "economic_data": None,
                    "news_analysis": None,
                    "portfolio_impact": None,
                    "query_history": []
                }
            }
        })

        # Economic data step
        events.append({
            "type": "STATE_DELTA",
            "delta": {
                "tool_logs": [{
                    "id": "econ-1",
                    "message": "Fetching Federal Reserve economic data...",
                    "status": "processing"
                }]
            }
        })

        # Economic data complete
        economic_data = self.generate_economic_data(delay_simulation=False)
        events.append({
            "type": "STATE_DELTA",
            "delta": {
                "market_analysis": {
                    "economic_data": economic_data
                },
                "tool_logs": [{
                    "id": "econ-1",
                    "message": "Economic indicators retrieved successfully",
                    "status": "completed"
                }]
            }
        })

        # News analysis step
        events.append({
            "type": "STATE_DELTA",
            "delta": {
                "tool_logs": [{
                    "id": "news-1",
                    "message": "Searching relevant market news...",
                    "status": "processing"
                }]
            }
        })

        # News analysis complete
        news_analysis = self.generate_news_analysis(portfolio_tickers, query, delay_simulation=False)
        events.append({
            "type": "STATE_DELTA",
            "delta": {
                "market_analysis": {
                    "news_analysis": news_analysis
                },
                "tool_logs": [{
                    "id": "news-1",
                    "message": "Market news analysis complete",
                    "status": "completed"
                }]
            }
        })

        # Portfolio impact step
        events.append({
            "type": "STATE_DELTA",
            "delta": {
                "tool_logs": [{
                    "id": "impact-1",
                    "message": "Analyzing portfolio impact...",
                    "status": "processing"
                }]
            }
        })

        # Portfolio impact complete
        portfolio_impact = self.generate_portfolio_impact(portfolio_tickers, economic_data, news_analysis, delay_simulation=False)
        events.append({
            "type": "STATE_DELTA",
            "delta": {
                "market_analysis": {
                    "portfolio_impact": portfolio_impact,
                    "analysis_status": "complete"
                },
                "tool_logs": [{
                    "id": "impact-1",
                    "message": "Portfolio impact analysis complete",
                    "status": "completed"
                }]
            }
        })

        # Run finished event
        events.append({
            "type": "RUN_FINISHED",
            "thread_id": events[0]["thread_id"],
            "run_id": events[0]["run_id"],
            "timestamp": datetime.now().isoformat()
        })

        return events


# Example usage and testing
if __name__ == "__main__":
    stub_generator = MarketAnalysisStubData()

    # Test with sample portfolio
    sample_portfolio = ["AAPL", "MSFT", "GOOGL"]
    sample_query = "How will Fed rate changes impact my tech stocks?"

    # Generate complete analysis
    result = stub_generator.generate_complete_analysis(
        portfolio_tickers=sample_portfolio,
        query=sample_query,
        enable_delays=False  # Disable delays for testing
    )

    print("\n" + "="*50)
    print("STUB DATA GENERATION TEST")
    print("="*50)
    print(json.dumps(result, indent=2, default=str))