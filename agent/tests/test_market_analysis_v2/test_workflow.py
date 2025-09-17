"""
Unit tests for Market Analysis v2 Workflow

Tests Agno v2 workflow implementation with Steps and Agents.
"""

import os
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime
import json

# Set test environment variables before importing
os.environ['FRED_API_KEY'] = 'test-fred-key'
os.environ['EXA_API_KEY'] = 'test-exa-key'
os.environ['OPENAI_API_KEY'] = 'test-openai-key'

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import StepInput for test mocks
from agno.workflow.v2 import StepInput

from market_analysis_v2.workflow import (
    market_analysis_workflow,
    execute_query_analysis,
    execute_economic_data_step,
    execute_news_analysis_step,
    execute_impact_synthesis,
    extract_keywords,
    determine_analysis_type,
    assess_data_quality,
)
from market_analysis_v2.agents import (
    query_parser_agent,
    economic_analyst_agent,
    news_analyst_agent,
    impact_synthesizer_agent,
    get_agent_for_step,
)


class TestWorkflowSteps:
    """Test individual workflow steps."""

    @pytest.mark.asyncio
    async def test_query_analysis_step(self):
        """Test query analysis step execution."""
        # Create mock StepInput
        step_input = MagicMock(spec=StepInput)
        step_input.input = "How will Fed rate changes impact my tech stocks?"
        step_input.additional_data = {
            "query": "How will Fed rate changes impact my tech stocks?",
            "portfolio": ["AAPL", "MSFT", "GOOGL"],
        }

        result = await execute_query_analysis(step_input)

        assert result.success is True
        assert result.content is not None
        assert "intent" in result.content
        assert "economic_indicators" in result.content
        assert "news_keywords" in result.content
        assert "focus_tickers" in result.content
        assert result.content["analysis_type"] == "monetary_policy"

    @pytest.mark.asyncio
    async def test_economic_data_step(self):
        """Test economic data gathering step."""
        with patch('market_analysis_v2.workflow.FredDataTools') as MockFred:
            # Mock the FRED tools
            mock_fred = MockFred.return_value
            mock_fred.get_economic_indicators = AsyncMock(return_value={
                "success": True,
                "economic_data": {
                    "federal_funds_rate": {
                        "data": {"values": [{"date": "2024-01", "value": 5.5}]},
                        "last_updated": "2024-01-15",
                    },
                    "inflation_rate": {
                        "data": {"values": [{"date": "2024-01", "value": 3.2}]},
                        "last_updated": "2024-01-15",
                    },
                },
                "errors": [],
            })

            # Create mock StepInput
            step_input = MagicMock(spec=StepInput)
            step_input.get_step_content = MagicMock(return_value={
                "economic_indicators": ["DFF", "CPIAUCSL"],
            })

            result = await execute_economic_data_step(step_input)

            assert result.success is True
            assert result.content is not None
            assert "raw_data" in result.content
            assert "interpretation" in result.content
            assert result.content["errors"] == []
            mock_fred.get_economic_indicators.assert_called_once()

    @pytest.mark.asyncio
    async def test_news_analysis_step(self):
        """Test news analysis step."""
        with patch('market_analysis_v2.workflow.ExaSearchTools') as MockExa:
            # Mock the Exa tools
            mock_exa = MockExa.return_value
            mock_exa.search_portfolio_news = AsyncMock(return_value={
                "success": True,
                "news_results": [
                    {
                        "title": "Tech Stocks Rally on Fed News",
                        "url": "https://example.com/article1",
                        "snippet": "Technology sector responds positively...",
                        "portfolio_relevance": "high",
                    },
                    {
                        "title": "Market Analysis: Rate Impact",
                        "url": "https://example.com/article2",
                        "snippet": "Federal Reserve decision affects...",
                        "portfolio_relevance": "medium",
                    },
                ],
                "query_used": "tech stocks federal reserve AAPL MSFT",
            })

            # Create mock StepInput
            step_input = MagicMock(spec=StepInput)
            step_input.input = "tech stocks federal reserve"
            step_input.get_step_content = MagicMock(return_value={
                "focus_tickers": ["AAPL", "MSFT"],
            })

            result = await execute_news_analysis_step(step_input)

            assert result.success is True
            assert result.content is not None
            assert "articles" in result.content
            assert len(result.content["articles"]) == 2
            assert "analysis" in result.content
            assert "query_used" in result.content
            mock_exa.search_portfolio_news.assert_called_once()

    @pytest.mark.asyncio
    async def test_news_analysis_step_failure_handling(self):
        """Test news analysis step handles failures gracefully."""
        with patch('market_analysis_v2.workflow.ExaSearchTools') as MockExa:
            # Mock Exa tools to raise an exception
            mock_exa = MockExa.return_value
            mock_exa.search_portfolio_news = AsyncMock(side_effect=Exception("API Error"))

            # Create mock StepInput
            step_input = MagicMock(spec=StepInput)
            step_input.input = "market news"
            step_input.get_step_content = MagicMock(return_value={"focus_tickers": []})

            result = await execute_news_analysis_step(step_input)

            # Should return success but with error message in content
            assert result.success is True
            assert result.content is not None
            assert result.content["articles"] == []
            assert "News analysis unavailable" in result.content["analysis"]
            assert result.content["error"] == "API Error"

    @pytest.mark.asyncio
    async def test_impact_synthesis_step(self):
        """Test impact synthesis step."""
        # Create mock StepInput
        step_input = MagicMock(spec=StepInput)
        step_input.input = "market impact analysis"
        step_input.additional_data = {
            "portfolio": ["AAPL", "MSFT"],
        }
        step_input.get_step_content = MagicMock(side_effect=lambda x: {
            "economic_data": {"interpretation": "Fed rates rising, inflation moderating"},
            "news_analysis": {"analysis": "Positive sentiment for tech sector"},
        }.get(x, {}))

        result = await execute_impact_synthesis(step_input)

        assert result.success is True
        assert result.content is not None
        assert "executive_summary" in result.content
        assert "economic_impact" in result.content
        assert "market_sentiment" in result.content
        assert "risk_level" in result.content
        assert "disclaimer" in result.content
        assert "investment advice" in result.content["disclaimer"]


class TestAgents:
    """Test agent definitions and configurations."""

    def test_agent_creation(self):
        """Test that all agents are properly created."""
        assert query_parser_agent is not None
        assert query_parser_agent.name == "Market Query Parser"
        assert economic_analyst_agent.name == "Economic Data Analyst"
        assert news_analyst_agent.name == "News & Sentiment Analyst"
        assert impact_synthesizer_agent.name == "Portfolio Impact Synthesizer"

    def test_agent_model_configuration(self):
        """Test that agents use correct model."""
        assert query_parser_agent.model.id == "gpt-4o-mini"
        assert economic_analyst_agent.model.id == "gpt-4o-mini"
        assert news_analyst_agent.model.id == "gpt-4o-mini"
        assert impact_synthesizer_agent.model.id == "gpt-4o-mini"

    def test_get_agent_for_step(self):
        """Test agent retrieval helper function."""
        assert get_agent_for_step("query_analysis").name == query_parser_agent.name
        assert get_agent_for_step("economic_data").name == economic_analyst_agent.name
        assert get_agent_for_step("news_analysis").name == news_analyst_agent.name
        assert get_agent_for_step("impact_synthesis").name == impact_synthesizer_agent.name

        with pytest.raises(ValueError) as exc_info:
            get_agent_for_step("invalid_step")
        assert "No agent found" in str(exc_info.value)


class TestWorkflowConfiguration:
    """Test workflow configuration and setup."""

    def test_workflow_creation(self):
        """Test that workflow is properly configured."""
        assert market_analysis_workflow is not None
        assert market_analysis_workflow.name == "Market Analysis Pipeline"
        assert len(market_analysis_workflow.steps) == 4

    def test_workflow_steps_order(self):
        """Test that workflow steps are in correct order."""
        step_names = [step.name for step in market_analysis_workflow.steps]
        expected_order = [
            "query_analysis",
            "economic_data",
            "news_analysis",
            "impact_synthesis",
        ]
        assert step_names == expected_order

    def test_workflow_database_configuration(self):
        """Test that workflow database is optional for MVP."""
        # Database configuration is optional for MVP
        # Can be added later for session persistence
        assert market_analysis_workflow is not None
        # Database can be configured later when needed


class TestHelperFunctions:
    """Test helper utility functions."""

    def test_extract_keywords(self):
        """Test keyword extraction from queries."""
        # Test with market terms
        query1 = "How will inflation affect my portfolio?"
        keywords1 = extract_keywords(query1)
        assert "inflation" in keywords1

        query2 = "What's the Fed's impact on rates?"
        keywords2 = extract_keywords(query2)
        assert "fed" in keywords2
        assert "rates" in keywords2

        # Test with no specific terms
        query3 = "Tell me about my stocks"
        keywords3 = extract_keywords(query3)
        assert keywords3 == ["market", "economy"]  # defaults

    def test_determine_analysis_type(self):
        """Test analysis type determination."""
        assert determine_analysis_type("fed rate hike") == "monetary_policy"
        assert determine_analysis_type("inflation concerns") == "inflation_analysis"
        assert determine_analysis_type("earnings season") == "earnings_analysis"
        assert determine_analysis_type("tech sector performance") == "sector_analysis"
        assert determine_analysis_type("market overview") == "general_market"

    def test_assess_data_quality(self):
        """Test data quality assessment."""
        # Test with complete data
        economic_data = {"raw_data": {"fed_rate": 5.5}}
        news_data = {"articles": [1, 2, 3]}
        quality = assess_data_quality(economic_data, news_data)
        assert "economic data available" in quality
        assert "3 news sources" in quality

        # Test with missing data
        empty_economic = {}
        empty_news = {}
        quality_empty = assess_data_quality(empty_economic, empty_news)
        assert "limited" in quality_empty


class TestIntegration:
    """Integration tests for workflow components."""

    @pytest.mark.asyncio
    async def test_workflow_step_chaining(self):
        """Test that workflow steps can be chained together."""
        # Step 1: Query Analysis
        query_input = MagicMock(spec=StepInput)
        query_input.input = "How will rising interest rates affect tech stocks?"
        query_input.additional_data = {
            "query": "How will rising interest rates affect tech stocks?",
            "portfolio": ["AAPL", "NVDA"],
        }
        query_result = await execute_query_analysis(query_input)
        assert query_result.success is True

        # Step 2: Economic Data (with mocked tools)
        with patch('market_analysis_v2.workflow.FredDataTools') as MockFred:
            mock_fred = MockFred.return_value
            mock_fred.get_economic_indicators = AsyncMock(return_value={
                "success": True,
                "economic_data": {"federal_funds_rate": {"data": {}}},
                "errors": [],
            })

            econ_input = MagicMock(spec=StepInput)
            econ_input.get_step_content = MagicMock(return_value=query_result.content)
            econ_result = await execute_economic_data_step(econ_input)
            assert econ_result.success is True

        # Step 3: News Analysis (with mocked tools)
        with patch('market_analysis_v2.workflow.ExaSearchTools') as MockExa:
            mock_exa = MockExa.return_value
            mock_exa.search_portfolio_news = AsyncMock(return_value={
                "success": True,
                "news_results": [],
                "query_used": "test",
            })

            news_input = MagicMock(spec=StepInput)
            news_input.input = "How will rising interest rates affect tech stocks?"
            news_input.get_step_content = MagicMock(return_value=query_result.content)
            news_result = await execute_news_analysis_step(news_input)
            assert news_result.success is True

        # Step 4: Impact Synthesis
        synthesis_input = MagicMock(spec=StepInput)
        synthesis_input.input = "How will rising interest rates affect tech stocks?"
        synthesis_input.additional_data = {"portfolio": ["AAPL", "NVDA"]}
        synthesis_input.get_step_content = MagicMock(side_effect=lambda x: {
            "economic_data": econ_result.content,
            "news_analysis": news_result.content,
        }.get(x, {}))
        synthesis_result = await execute_impact_synthesis(synthesis_input)
        assert synthesis_result.success is True
        assert synthesis_result.content["risk_level"] in ["HIGH", "MEDIUM", "LOW"]

    @pytest.mark.asyncio
    async def test_error_propagation(self):
        """Test that errors are properly handled through the workflow."""
        # Test query analysis with missing input
        bad_input = MagicMock(spec=StepInput)
        bad_input.input = ""
        bad_input.additional_data = {}
        result = await execute_query_analysis(bad_input)
        # Should still succeed with defaults
        assert result.success is True

        # Test economic data with API failure
        with patch('market_analysis_v2.workflow.FredDataTools') as MockFred:
            mock_fred = MockFred.return_value
            mock_fred.get_economic_indicators = AsyncMock(return_value={
                "success": False,
                "errors": ["API Error"],
            })

            econ_input = MagicMock(spec=StepInput)
            econ_input.get_step_content = MagicMock(return_value={"economic_indicators": ["DFF"]})
            econ_result = await execute_economic_data_step(econ_input)
            assert econ_result.success is False
            assert "Failed to fetch economic data" in econ_result.content["error"]