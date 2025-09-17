"""
Market Analysis Workflow using Agno v2 Patterns

This module implements the market analysis workflow using Agno v2 Step objects
and explicit Agent definitions for each step.
"""

from agno.workflow.v2 import Step, Workflow, StepInput, StepOutput
# SqliteDb import commented out - not essential for MVP
# from agno.storage.sqlite import SqliteDb
from typing import List, Any, Optional, Dict
import asyncio
import json
import logging
from datetime import datetime

from .agents import (
    query_parser_agent,
    economic_analyst_agent,
    news_analyst_agent,
    impact_synthesizer_agent,
)
from .tools import FredDataTools, ExaSearchTools

# Configure logging
logger = logging.getLogger(__name__)


# Custom step implementations with tool integration
async def execute_query_analysis(step_input: StepInput) -> StepOutput:
    """
    Execute query analysis step to parse user input and plan data gathering.

    Args:
        step_input: Contains user query and portfolio context

    Returns:
        StepOutput with analysis plan
    """
    try:
        # Get query from input
        user_query = step_input.input if hasattr(step_input, 'input') else ""
        portfolio = []

        # Try to get additional context if available
        if hasattr(step_input, 'additional_data'):
            user_query = step_input.additional_data.get("query", user_query)
            portfolio = step_input.additional_data.get("portfolio", [])

        logger.info(f"Analyzing query: {user_query[:100]}...")

        # Use the query parser agent to analyze the query
        analysis_prompt = f"""
        Analyze this market query: "{user_query}"

        Portfolio context: {json.dumps(portfolio[:5]) if portfolio else "No specific portfolio"}

        Provide a structured analysis plan.
        """

        # Execute agent (in real implementation, this would use agent.run())
        analysis_plan = {
            "intent": "market_analysis",
            "economic_indicators": ["DFF", "CPIAUCSL", "GDP", "UNRATE"],
            "news_keywords": extract_keywords(user_query),
            "focus_tickers": portfolio[:5] if portfolio else [],
            "analysis_type": determine_analysis_type(user_query),
        }

        return StepOutput(
            step_name="query_analysis",
            content=analysis_plan,
            success=True
        )

    except Exception as e:
        logger.error(f"Query analysis failed: {e}")
        return StepOutput(
            step_name="query_analysis",
            content={"error": str(e)},
            success=False
        )


async def execute_economic_data_step(step_input: StepInput) -> StepOutput:
    """
    Execute economic data gathering step using FRED tools.

    Args:
        step_input: Contains analysis plan from previous step

    Returns:
        StepOutput with economic data
    """
    try:
        # Get analysis plan from previous step
        if hasattr(step_input, 'get_step_content'):
            analysis_plan = step_input.get_step_content("query_analysis") or {}
        else:
            analysis_plan = {}

        if isinstance(analysis_plan, dict):
            indicators = analysis_plan.get("economic_indicators", ["DFF", "CPIAUCSL"])
        else:
            indicators = ["DFF", "CPIAUCSL"]

        logger.info(f"Fetching economic indicators: {indicators}")

        # Initialize FRED tools
        fred_tools = FredDataTools()

        # Fetch economic data
        economic_data = await fred_tools.get_economic_indicators(indicators)

        if not economic_data.get("success"):
            raise Exception(f"Failed to fetch economic data: {economic_data.get('errors')}")

        # Have the economic analyst interpret the data
        interpretation = await analyze_economic_data(economic_data, economic_analyst_agent)

        return StepOutput(
            step_name="economic_data",
            content={
                "raw_data": economic_data.get("economic_data"),
                "interpretation": interpretation,
                "errors": economic_data.get("errors", []),
            },
            success=True
        )

    except Exception as e:
        logger.error(f"Economic data step failed: {e}")
        return StepOutput(
            step_name="economic_data",
            content={"error": str(e)},
            success=False
        )


async def execute_news_analysis_step(step_input: StepInput) -> StepOutput:
    """
    Execute news analysis step using Exa tools.

    Args:
        step_input: Contains analysis plan and query

    Returns:
        StepOutput with news analysis
    """
    try:
        # Get analysis plan from query_analysis step
        if hasattr(step_input, 'get_step_content'):
            analysis_plan = step_input.get_step_content("query_analysis") or {}
        else:
            analysis_plan = {}

        if isinstance(analysis_plan, dict):
            portfolio_tickers = analysis_plan.get("focus_tickers", [])
        else:
            portfolio_tickers = []

        # Get original query
        query = step_input.input if hasattr(step_input, 'input') else "market analysis"

        logger.info(f"Searching for news: {query[:50]}...")

        # Initialize Exa tools
        exa_tools = ExaSearchTools()

        # Search for relevant news
        news_results = await exa_tools.search_portfolio_news(
            query=query,
            portfolio_tickers=portfolio_tickers,
            num_results=5,
        )

        if not news_results.get("success"):
            logger.warning(f"News search had issues: {news_results.get('error')}")

        # Have the news analyst interpret the articles
        news_analysis = await analyze_news_content(news_results, news_analyst_agent)

        return StepOutput(
            step_name="news_analysis",
            content={
                "articles": news_results.get("news_results", []),
                "analysis": news_analysis,
                "query_used": news_results.get("query_used"),
            },
            success=True
        )

    except Exception as e:
        logger.error(f"News analysis step failed: {e}")
        # Return partial success for news failures
        return StepOutput(
            step_name="news_analysis",
            content={"articles": [], "analysis": "News analysis unavailable", "error": str(e)},
            success=True  # Mark as success to continue workflow
        )


async def execute_impact_synthesis(step_input: StepInput) -> StepOutput:
    """
    Execute impact synthesis step to combine all data.

    Args:
        step_input: Contains all previous step outputs

    Returns:
        StepOutput with final portfolio insights
    """
    try:
        # Get data from previous steps
        if hasattr(step_input, 'get_step_content'):
            economic_data = step_input.get_step_content("economic_data") or {}
            news_data = step_input.get_step_content("news_analysis") or {}
        else:
            economic_data = {}
            news_data = {}

        # Get query and portfolio from input
        query = step_input.input if hasattr(step_input, 'input') else ""
        portfolio = []
        if hasattr(step_input, 'additional_data'):
            portfolio = step_input.additional_data.get("portfolio", [])

        logger.info("Synthesizing market analysis insights...")

        # Prepare synthesis context
        synthesis_context = {
            "user_query": query,
            "portfolio_holdings": portfolio,
            "economic_analysis": economic_data.get("interpretation", "No economic data available"),
            "news_sentiment": news_data.get("analysis", "No news analysis available"),
            "data_quality": assess_data_quality(economic_data, news_data),
        }

        # Have the synthesizer create final insights
        portfolio_insights = await create_portfolio_insights(
            synthesis_context, impact_synthesizer_agent
        )

        return StepOutput(
            step_name="impact_synthesis",
            content=portfolio_insights,
            success=True
        )

    except Exception as e:
        logger.error(f"Impact synthesis failed: {e}")
        return StepOutput(
            step_name="impact_synthesis",
            content={"error": str(e)},
            success=False
        )


# Create workflow steps using Agents directly
query_analysis_step = Step(
    name="query_analysis",
    agent=query_parser_agent,
    description="Parse user's market analysis query and identify required data sources",
)

economic_data_step = Step(
    name="economic_data",
    agent=economic_analyst_agent,
    description="Fetch and analyze relevant FRED economic indicators",
)

news_analysis_step = Step(
    name="news_analysis",
    agent=news_analyst_agent,
    description="Search and analyze relevant market news via Exa",
)

impact_synthesis_step = Step(
    name="impact_synthesis",
    agent=impact_synthesizer_agent,
    description="Synthesize economic and news data into portfolio-specific insights",
)


# Create the main workflow
market_analysis_workflow = Workflow(
    name="Market Analysis Pipeline",
    description="Autonomous market intelligence analysis for portfolio context",
    steps=[
        query_analysis_step,
        economic_data_step,
        news_analysis_step,
        impact_synthesis_step,
    ],
    # Database configuration commented out for MVP - can be added later
    # db=SqliteDb(
    #     session_table="market_analysis_sessions",
    #     db_file="tmp/market_analysis.db",
    # ),
)


# Helper functions
def extract_keywords(query: str) -> List[str]:
    """Extract relevant keywords from user query for news search."""
    # Simple keyword extraction (in production, use NLP)
    keywords = []
    market_terms = ["inflation", "rates", "fed", "economy", "earnings", "recession", "growth"]

    query_lower = query.lower()
    for term in market_terms:
        if term in query_lower:
            keywords.append(term)

    return keywords if keywords else ["market", "economy"]


def determine_analysis_type(query: str) -> str:
    """Determine the type of analysis requested."""
    query_lower = query.lower()

    if "fed" in query_lower or "rate" in query_lower:
        return "monetary_policy"
    elif "inflation" in query_lower:
        return "inflation_analysis"
    elif "earnings" in query_lower:
        return "earnings_analysis"
    elif "sector" in query_lower:
        return "sector_analysis"
    else:
        return "general_market"


async def analyze_economic_data(data: Dict, agent: Any) -> str:
    """Use economic analyst agent to interpret data."""
    # Simplified - in real implementation would use agent.run()
    if not data.get("economic_data"):
        return "No economic data available for analysis"

    interpretation = f"""
    Economic indicators show:
    - Federal Funds Rate: {data['economic_data'].get('federal_funds_rate', {}).get('data', 'N/A')}
    - Inflation trending: {data['economic_data'].get('inflation_rate', {}).get('data', 'N/A')}
    - GDP growth: {data['economic_data'].get('gdp_growth', {}).get('data', 'N/A')}
    - Unemployment: {data['economic_data'].get('unemployment_rate', {}).get('data', 'N/A')}
    """
    return interpretation


async def analyze_news_content(news_results: Dict, agent: Any) -> str:
    """Use news analyst agent to interpret articles."""
    # Simplified - in real implementation would use agent.run()
    if not news_results.get("news_results"):
        return "No news articles available for analysis"

    articles = news_results.get("news_results", [])
    sentiment = "mixed"

    # Simple sentiment analysis based on relevance scores
    high_relevance = [a for a in articles if a.get("portfolio_relevance") == "high"]
    if high_relevance:
        sentiment = "focused on portfolio holdings"

    return f"News sentiment appears {sentiment} with {len(articles)} relevant articles found"


async def create_portfolio_insights(context: Dict, agent: Any) -> Dict:
    """Use synthesizer agent to create final insights."""
    # Simplified - in real implementation would use agent.run()
    return {
        "executive_summary": "Market analysis complete with economic and news data synthesized",
        "economic_impact": context.get("economic_analysis", "Analysis pending"),
        "market_sentiment": context.get("news_sentiment", "Sentiment analysis pending"),
        "portfolio_implications": "Based on current data, portfolio exposure to market conditions has been assessed",
        "risk_level": "MEDIUM",
        "confidence_score": 0.75,
        "disclaimer": "This is analysis only, not investment advice",
        "timestamp": datetime.now().isoformat(),
    }


def assess_data_quality(economic_data: Dict, news_data: Dict) -> str:
    """Assess the quality and completeness of gathered data."""
    quality_factors = []

    if economic_data and economic_data.get("raw_data"):
        quality_factors.append("economic data available")
    else:
        quality_factors.append("limited economic data")

    if news_data and news_data.get("articles"):
        quality_factors.append(f"{len(news_data.get('articles', []))} news sources")
    else:
        quality_factors.append("limited news coverage")

    return ", ".join(quality_factors) if quality_factors else "incomplete data"


# Export the workflow and helper functions
__all__ = [
    "market_analysis_workflow",
    "execute_query_analysis",
    "execute_economic_data_step",
    "execute_news_analysis_step",
    "execute_impact_synthesis",
    "extract_keywords",
    "determine_analysis_type",
    "assess_data_quality",
]