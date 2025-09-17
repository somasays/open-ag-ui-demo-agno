"""
Market Analysis Agents using Agno v2 Patterns

This module defines specialized Agent instances for each step of the
market analysis workflow, following Agno v2 architecture.
"""

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from typing import Dict, List, Any, Optional
import json
import logging
from pydantic import BaseModel, Field

# Configure logging
logger = logging.getLogger(__name__)

# Initialize the model for all agents
model = OpenAIChat(id="gpt-4o-mini", temperature=0.7)


class HoldingImpact(BaseModel):
    """Analysis of a specific portfolio holding."""
    ticker: str = Field(..., description="Stock ticker symbol")
    impact: str = Field(..., description="How economic factors affect this holding")
    risk_level: str = Field(..., description="Risk level: HIGH, MEDIUM, or LOW")
    confidence_score: float = Field(..., description="Confidence in analysis (0.0-1.0)")


class MarketAnalysisResponse(BaseModel):
    """Structured market analysis response."""
    executive_summary: str = Field(..., description="2-3 key takeaways from the analysis")
    economic_impact: str = Field(..., description="How macro factors affect the portfolio")
    market_sentiment: str = Field(..., description="Current news narrative and implications")
    holdings_analysis: List[HoldingImpact] = Field(..., description="Analysis of each portfolio holding")
    risk_level: str = Field(..., description="Overall portfolio risk level: HIGH, MEDIUM, or LOW")
    recommendations: List[str] = Field(..., description="Areas for further research (NOT investment advice)")
    disclaimer: str = Field(..., description="Required disclaimer about analysis vs investment advice")


# Query Parser Agent - Understands user intent and plans data gathering
query_parser_agent = Agent(
    name="Market Query Parser",
    model=model,
    instructions="""You are an expert at parsing market analysis questions and identifying required data sources.

    Your role is to:
    1. Understand the user's market analysis question
    2. Identify which economic indicators are relevant
    3. Determine what news topics to search for
    4. Extract portfolio context from the query

    Output a structured analysis plan with:
    - intent: The main goal of the query
    - economic_indicators: List of FRED indicators needed (DFF, CPIAUCSL, GDP, UNRATE)
    - news_keywords: Keywords for news search
    - focus_tickers: Specific tickers mentioned or implied
    - analysis_type: Type of analysis (market_conditions, sector_analysis, economic_impact, etc.)
    """,
    tools=[],  # No tools needed for parsing
    markdown=True,
    add_datetime_to_instructions=True,
)


# Economic Analyst Agent - Interprets FRED data for portfolio impact
economic_analyst_agent = Agent(
    name="Economic Data Analyst",
    model=model,
    instructions="""You are an expert economic analyst specializing in interpreting Federal Reserve data
    and its impact on investment portfolios.

    Your role is to:
    1. Analyze FRED economic indicators (interest rates, inflation, GDP, unemployment)
    2. Identify trends and significant changes
    3. Assess potential impact on different market sectors
    4. Provide context for the current economic environment

    When analyzing data:
    - Compare current values to historical averages
    - Identify trend directions (rising, falling, stable)
    - Explain implications for equity markets
    - Consider both short-term and long-term impacts

    Always separate raw data from interpretation and maintain objectivity.
    """,
    tools=[],  # Will use FredDataTools through workflow
    markdown=True,
    add_datetime_to_instructions=True,
)


# News Analyst Agent - Processes and synthesizes news for relevance
news_analyst_agent = Agent(
    name="News & Sentiment Analyst",
    model=model,
    instructions="""You are an expert at analyzing financial news and extracting market sentiment.

    Your role is to:
    1. Process news articles from trusted financial sources
    2. Identify key themes and market narratives
    3. Assess sentiment (bullish, bearish, neutral)
    4. Determine relevance to specific portfolio holdings
    5. Highlight potential market-moving events

    When analyzing news:
    - Focus on factual reporting over speculation
    - Identify consensus views vs contrarian perspectives
    - Note any major announcements or policy changes
    - Consider source credibility and potential bias

    Provide a balanced view of market sentiment with supporting evidence.
    """,
    tools=[],  # Will use ExaSearchTools through workflow
    markdown=True,
    add_datetime_to_instructions=True,
)


# Impact Synthesizer Agent - Combines all data into portfolio insights
impact_synthesizer_agent = Agent(
    name="Portfolio Impact Synthesizer",
    model=model,
    instructions="""You are an expert at synthesizing economic data and market news into
    actionable portfolio insights.

    Your role is to:
    1. Combine economic indicators and news analysis
    2. Generate specific insights for portfolio holdings
    3. Assess risk levels (High/Medium/Low) for each position
    4. Provide clear, actionable recommendations
    5. Highlight both opportunities and risks

    When creating insights:
    - Be specific about which holdings are affected and why
    - Provide confidence scores for predictions (0.0-1.0)
    - Separate facts from analysis
    - Include both bull and bear scenarios
    - Always include disclaimers that this is analysis, not investment advice

    Format output as:
    - Executive Summary: 2-3 key takeaways
    - Economic Impact: How macro factors affect the portfolio
    - Market Sentiment: Current news narrative and its implications
    - Holdings Analysis: Specific impact on each major holding with risk levels and confidence scores
    - Risk Assessment: Overall portfolio risk level (HIGH, MEDIUM, or LOW)
    - Recommendations: Areas for further research (NOT investment advice)
    - Disclaimer: Required disclaimer about analysis vs investment advice
    """,
    tools=[],  # Synthesis only, no external tools
    markdown=True,
    add_datetime_to_instructions=True,
    show_tool_calls=True,
    response_model=MarketAnalysisResponse,
)


def get_agent_for_step(step_name: str) -> Agent:
    """
    Helper function to get the appropriate agent for a workflow step.

    Args:
        step_name: Name of the workflow step

    Returns:
        The corresponding Agent instance
    """
    agents_map = {
        "query_analysis": query_parser_agent,
        "economic_data": economic_analyst_agent,
        "news_analysis": news_analyst_agent,
        "impact_synthesis": impact_synthesizer_agent,
    }

    agent = agents_map.get(step_name)
    if not agent:
        raise ValueError(f"No agent found for step: {step_name}")

    return agent


# Export all agents, models, and helper
__all__ = [
    "query_parser_agent",
    "economic_analyst_agent",
    "news_analyst_agent",
    "impact_synthesizer_agent",
    "get_agent_for_step",
    "HoldingImpact",
    "MarketAnalysisResponse",
]