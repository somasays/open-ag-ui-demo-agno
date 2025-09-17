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
from pydantic import BaseModel, Field

from .agents import (
    query_parser_agent,
    economic_analyst_agent,
    news_analyst_agent,
    impact_synthesizer_agent,
)
from .tools import FredDataTools, ExaSearchTools

# Configure logging
logger = logging.getLogger(__name__)


# Pydantic models for structured output
class PortfolioInsights(BaseModel):
    """Structured output for portfolio insights."""
    executive_summary: str = Field(description="2-3 key takeaways from the analysis")
    economic_impact: str = Field(description="How macro factors affect the portfolio")
    market_sentiment: str = Field(description="Current news narrative and its implications")
    holdings_analysis: str = Field(description="Specific impact on each major holding")
    risk_assessment: str = Field(description="Detailed risk analysis")
    risk_level: str = Field(description="Overall portfolio risk level (HIGH/MEDIUM/LOW)")
    recommendations: str = Field(description="Suggested areas for further research")
    confidence_score: float = Field(description="Confidence score between 0 and 1")
    portfolio_holdings: List[str] = Field(description="List of portfolio holdings analyzed")
    timestamp: str = Field(description="ISO timestamp of analysis")
    disclaimer: str = Field(description="Required disclaimer for informational purposes only")


class HoldingImpact(BaseModel):
    """Individual holding impact analysis."""
    symbol: str = Field(description="Stock symbol")
    impact_analysis: str = Field(description="Specific impact on this holding")
    risk_level: str = Field(description="Risk level for this holding (HIGH/MEDIUM/LOW)")
    confidence_score: float = Field(description="Confidence in analysis 0-1")


class MarketAnalysisResponse(BaseModel):
    """Complete market analysis response."""
    user_query: str = Field(description="Original user query")
    portfolio_insights: PortfolioInsights = Field(description="Complete portfolio analysis")
    holding_impacts: List[HoldingImpact] = Field(description="Individual holding analyses")
    data_quality: str = Field(description="Quality assessment of source data")
    processing_time: Optional[float] = Field(description="Time taken for analysis in seconds")


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
        logger.info(f"Portfolio from additional_data: {portfolio}")

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
        logger.info(f"Portfolio for synthesis: {portfolio}")

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
    try:
        # Create detailed prompt for the synthesizer agent
        portfolio_holdings = context.get("portfolio_holdings", [])
        user_query = context.get("user_query", "")
        economic_analysis = context.get("economic_analysis", "No economic data available")
        news_sentiment = context.get("news_sentiment", "No news analysis available")

        # Format portfolio holdings for the prompt
        portfolio_text = ", ".join(portfolio_holdings) if portfolio_holdings else "No specific portfolio provided"

        logger.info(f"Creating portfolio insights for holdings: {portfolio_holdings}")
        logger.info(f"Portfolio text for prompt: {portfolio_text}")

        prompt = f"""
        Synthesize the following market analysis into portfolio insights:

        USER QUERY: {user_query}
        PORTFOLIO HOLDINGS: {portfolio_text}
        ECONOMIC ANALYSIS: {economic_analysis}
        NEWS SENTIMENT: {news_sentiment}

        Please provide a comprehensive analysis following your instructions, including specific insights for each portfolio holding, risk assessment, and recommendations.
        """

        # Use the synthesizer agent to generate insights
        result = await asyncio.to_thread(
            agent.run,
            prompt
        )

        # Extract structured content from agent result
        if hasattr(result, 'content') and hasattr(result.content, 'dict'):
            # This is a Pydantic model - extract structured data
            structured_response = result.content
            return {
                "executive_summary": structured_response.executive_summary,
                "economic_impact": structured_response.economic_impact,
                "market_sentiment": structured_response.market_sentiment,
                "holdings_analysis": [holding.model_dump() for holding in structured_response.holdings_analysis],
                "risk_level": structured_response.risk_level,
                "recommendations": structured_response.recommendations,
                "disclaimer": structured_response.disclaimer,
                "timestamp": datetime.now().isoformat(),
                "structured_output": True,
            }
        elif hasattr(result, 'content'):
            # Fallback: parse text content using existing methods
            insights_content = result.content
            risk_assessment_text = extract_section(insights_content, ["Risk Assessment"])
            return {
                "executive_summary": extract_section(insights_content, ["Executive Summary", "Summary"]),
                "economic_impact": extract_section(insights_content, ["Economic Impact"]),
                "market_sentiment": extract_section(insights_content, ["Market Sentiment"]),
                "holdings_analysis": extract_section(insights_content, ["Holdings Analysis", "Portfolio Analysis"]),
                "risk_assessment": risk_assessment_text,
                "risk_level": extract_risk_level(risk_assessment_text),
                "recommendations": extract_section(insights_content, ["Recommendations"]),
                "full_analysis": insights_content,
                "confidence_score": extract_confidence_score(insights_content),
                "disclaimer": "*This analysis is for informational purposes only and should not be construed as investment advice. Always conduct thorough research or consult with a financial advisor before making investment decisions.*",
                "timestamp": datetime.now().isoformat(),
                "structured_output": False,
            }
        elif isinstance(result, dict):
            # Handle dictionary result
            insights_content = result.get('content', str(result))
            risk_assessment_text = extract_section(insights_content, ["Risk Assessment"])
            return {
                "executive_summary": extract_section(insights_content, ["Executive Summary", "Summary"]),
                "economic_impact": extract_section(insights_content, ["Economic Impact"]),
                "market_sentiment": extract_section(insights_content, ["Market Sentiment"]),
                "holdings_analysis": extract_section(insights_content, ["Holdings Analysis", "Portfolio Analysis"]),
                "risk_assessment": risk_assessment_text,
                "risk_level": extract_risk_level(risk_assessment_text),
                "recommendations": extract_section(insights_content, ["Recommendations"]),
                "full_analysis": insights_content,
                "confidence_score": extract_confidence_score(insights_content),
                "disclaimer": "*This analysis is for informational purposes only and should not be construed as investment advice. Always conduct thorough research or consult with a financial advisor before making investment decisions.*",
                "timestamp": datetime.now().isoformat(),
                "structured_output": False,
            }
        else:
            # Handle unexpected result type
            insights_content = str(result)
            return {
                "executive_summary": "Analysis unavailable",
                "economic_impact": "Economic impact analysis unavailable",
                "market_sentiment": "Market sentiment analysis unavailable",
                "holdings_analysis": "Holdings analysis unavailable",
                "risk_level": "MEDIUM",
                "recommendations": ["Further research recommended"],
                "disclaimer": "*This analysis is for informational purposes only and should not be construed as investment advice. Always conduct thorough research or consult with a financial advisor before making investment decisions.*",
                "timestamp": datetime.now().isoformat(),
                "error": f"Unexpected result type: {type(result)}",
                "structured_output": False,
            }

    except Exception as e:
        logger.error(f"Error creating portfolio insights: {e}")
        # Fallback to basic structure if agent fails
        fallback_portfolio = context.get("portfolio_holdings", [])
        return {
            "executive_summary": "Analysis completed with limited data",
            "economic_impact": context.get("economic_analysis", "Analysis pending"),
            "market_sentiment": context.get("news_sentiment", "Sentiment analysis pending"),
            "holdings_analysis": f"Portfolio holdings: {', '.join(fallback_portfolio) if fallback_portfolio else 'No specific holdings'}",
            "risk_assessment": "Risk assessment pending detailed analysis",
            "risk_level": "MEDIUM",
            "recommendations": "Further research recommended",
            "full_analysis": f"Based on available economic and news data for portfolio: {', '.join(fallback_portfolio) if fallback_portfolio else 'general market'}",
            "confidence_score": 0.5,
            "disclaimer": "*This analysis is for informational purposes only and should not be construed as investment advice.*",
            "timestamp": datetime.now().isoformat(),
        }


def extract_section(content: str, section_headers: List[str]) -> str:
    """Extract a specific section from markdown content."""
    content_lower = content.lower()

    for header in section_headers:
        header_lower = header.lower()
        if header_lower in content_lower:
            # Find the section start
            start_idx = content_lower.find(header_lower)
            if start_idx != -1:
                # Find the next section or end of content
                next_section_idx = len(content)
                for next_header in ["executive summary", "economic impact", "market sentiment", "holdings analysis", "portfolio analysis", "risk assessment", "recommendations", "disclaimer"]:
                    if next_header.lower() != header_lower and next_header.lower() in content_lower[start_idx + len(header):]:
                        next_idx = content_lower.find(next_header.lower(), start_idx + len(header))
                        if next_idx != -1 and next_idx < next_section_idx:
                            next_section_idx = next_idx

                # Extract the section content
                section = content[start_idx:next_section_idx].strip()
                # Remove the header line
                lines = section.split('\n')
                if len(lines) > 1:
                    return '\n'.join(lines[1:]).strip()
                return section

    return "Section not found"


def extract_risk_level(risk_assessment: str) -> str:
    """Extract risk level from risk assessment text."""
    risk_assessment_lower = risk_assessment.lower()

    # Look for explicit risk level mentions
    if "high risk" in risk_assessment_lower or "risk: high" in risk_assessment_lower:
        return "HIGH"
    elif "medium risk" in risk_assessment_lower or "risk: medium" in risk_assessment_lower:
        return "MEDIUM"
    elif "low risk" in risk_assessment_lower or "risk: low" in risk_assessment_lower:
        return "LOW"
    else:
        # Estimate based on language
        if any(term in risk_assessment_lower for term in ["significant", "substantial", "major", "severe"]):
            return "HIGH"
        elif any(term in risk_assessment_lower for term in ["moderate", "some", "potential", "possible"]):
            return "MEDIUM"
        else:
            return "MEDIUM"  # Default fallback


def extract_confidence_score(content: str) -> float:
    """Extract confidence score from content or estimate based on completeness."""
    content_lower = content.lower()

    # Look for explicit confidence mentions
    if "confidence" in content_lower:
        # Try to find percentage or decimal scores
        import re
        confidence_patterns = [
            r'confidence[:\s]*(\d+)%',
            r'confidence[:\s]*0?\.(\d+)',
            r'confidence[:\s]*(\d+)/(100|10)'
        ]

        for pattern in confidence_patterns:
            matches = re.findall(pattern, content_lower)
            if matches:
                try:
                    if len(matches[0]) == 2:  # For x/y format
                        score = float(matches[0][0]) / float(matches[0][1])
                    else:
                        score = float(matches[0][0]) / 100 if float(matches[0][0]) > 1 else float(matches[0][0])
                    return min(1.0, max(0.0, score))
                except (ValueError, IndexError):
                    continue

    # Estimate based on content completeness
    completeness_factors = 0
    if "economic" in content_lower:
        completeness_factors += 0.25
    if "market" in content_lower:
        completeness_factors += 0.25
    if "portfolio" in content_lower or "holdings" in content_lower:
        completeness_factors += 0.25
    if "risk" in content_lower:
        completeness_factors += 0.25

    return completeness_factors


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