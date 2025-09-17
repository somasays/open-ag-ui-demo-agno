"""
Unit tests for Market Analysis v2 Agents

Tests Agent definitions and configurations.
"""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock

# Set test environment variables
os.environ['OPENAI_API_KEY'] = 'test-openai-key'

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from market_analysis_v2.agents import (
    query_parser_agent,
    economic_analyst_agent,
    news_analyst_agent,
    impact_synthesizer_agent,
    get_agent_for_step,
)


class TestAgentDefinitions:
    """Test agent creation and configuration."""

    def test_query_parser_agent_configuration(self):
        """Test Query Parser Agent configuration."""
        assert query_parser_agent is not None
        assert query_parser_agent.name == "Market Query Parser"
        assert query_parser_agent.model is not None
        assert query_parser_agent.model.id == "gpt-4o-mini"
        assert query_parser_agent.model.temperature == 0.7
        assert query_parser_agent.markdown is True
        assert query_parser_agent.add_datetime_to_instructions is True
        assert query_parser_agent.tools == []  # No tools for parsing

        # Check instructions contain key elements
        instructions = query_parser_agent.instructions
        assert "parsing market analysis questions" in instructions
        assert "economic indicators" in instructions
        assert "news topics" in instructions
        assert "portfolio context" in instructions

    def test_economic_analyst_agent_configuration(self):
        """Test Economic Analyst Agent configuration."""
        assert economic_analyst_agent is not None
        assert economic_analyst_agent.name == "Economic Data Analyst"
        assert economic_analyst_agent.model.id == "gpt-4o-mini"
        assert economic_analyst_agent.markdown is True
        assert economic_analyst_agent.tools == []  # Tools provided by workflow

        # Check instructions contain key economic terms
        instructions = economic_analyst_agent.instructions
        assert "Federal Reserve data" in instructions
        assert "interest rates" in instructions
        assert "inflation" in instructions
        assert "GDP" in instructions
        assert "unemployment" in instructions
        assert "equity markets" in instructions

    def test_news_analyst_agent_configuration(self):
        """Test News Analyst Agent configuration."""
        assert news_analyst_agent is not None
        assert news_analyst_agent.name == "News & Sentiment Analyst"
        assert news_analyst_agent.model.id == "gpt-4o-mini"
        assert news_analyst_agent.markdown is True

        # Check instructions contain news analysis elements
        instructions = news_analyst_agent.instructions
        assert "financial news" in instructions
        assert "market sentiment" in instructions
        assert "portfolio holdings" in instructions
        assert "bullish, bearish, neutral" in instructions
        assert "source credibility" in instructions

    def test_impact_synthesizer_agent_configuration(self):
        """Test Impact Synthesizer Agent configuration."""
        assert impact_synthesizer_agent is not None
        assert impact_synthesizer_agent.name == "Portfolio Impact Synthesizer"
        assert impact_synthesizer_agent.model.id == "gpt-4o-mini"
        assert impact_synthesizer_agent.markdown is True
        assert impact_synthesizer_agent.show_tool_calls is True

        # Check instructions contain synthesis elements
        instructions = impact_synthesizer_agent.instructions
        assert "synthesizing economic data" in instructions
        assert "portfolio insights" in instructions
        assert "risk levels" in instructions
        assert "confidence scores" in instructions
        assert "not investment advice" in instructions.lower()
        assert "Executive Summary" in instructions
        assert "Risk Assessment" in instructions

    def test_all_agents_share_model_instance(self):
        """Test that all agents use the same model configuration."""
        # All agents should use gpt-4o-mini with temperature 0.7
        agents = [
            query_parser_agent,
            economic_analyst_agent,
            news_analyst_agent,
            impact_synthesizer_agent,
        ]

        for agent in agents:
            assert agent.model.id == "gpt-4o-mini"
            assert agent.model.temperature == 0.7


class TestAgentRetrieval:
    """Test agent retrieval and mapping functions."""

    def test_get_agent_for_valid_steps(self):
        """Test retrieving agents for valid workflow steps."""
        # Test each valid step name
        assert get_agent_for_step("query_analysis") == query_parser_agent
        assert get_agent_for_step("economic_data") == economic_analyst_agent
        assert get_agent_for_step("news_analysis") == news_analyst_agent
        assert get_agent_for_step("impact_synthesis") == impact_synthesizer_agent

    def test_get_agent_for_invalid_step(self):
        """Test error handling for invalid step names."""
        with pytest.raises(ValueError) as exc_info:
            get_agent_for_step("invalid_step")
        assert "No agent found for step: invalid_step" in str(exc_info.value)

        with pytest.raises(ValueError) as exc_info:
            get_agent_for_step("")
        assert "No agent found for step:" in str(exc_info.value)

        with pytest.raises(ValueError) as exc_info:
            get_agent_for_step(None)
        assert "No agent found for step:" in str(exc_info.value)


class TestAgentInstructions:
    """Test agent instruction quality and completeness."""

    def test_query_parser_instructions_completeness(self):
        """Test Query Parser has complete instructions."""
        instructions = query_parser_agent.instructions

        # Should mention all required outputs
        required_outputs = [
            "intent",
            "economic_indicators",
            "news_keywords",
            "focus_tickers",
            "analysis_type",
        ]

        for output in required_outputs:
            assert output in instructions, f"Missing required output: {output}"

    def test_economic_analyst_instructions_objectivity(self):
        """Test Economic Analyst maintains objectivity."""
        instructions = economic_analyst_agent.instructions

        # Should emphasize objectivity and data separation
        assert "separate raw data from interpretation" in instructions.lower()
        assert "maintain objectivity" in instructions.lower()
        assert "trend" in instructions.lower()
        assert "historical" in instructions.lower()

    def test_news_analyst_instructions_balance(self):
        """Test News Analyst provides balanced analysis."""
        instructions = news_analyst_agent.instructions

        # Should emphasize balanced reporting
        assert "balanced view" in instructions.lower()
        assert "factual reporting" in instructions.lower()
        assert "speculation" in instructions.lower()
        assert "credibility" in instructions.lower()

    def test_synthesizer_includes_disclaimer(self):
        """Test Impact Synthesizer includes proper disclaimers."""
        instructions = impact_synthesizer_agent.instructions

        # Must include investment advice disclaimer
        assert "not investment advice" in instructions.lower()
        assert "analysis" in instructions.lower()
        assert "disclaimer" in instructions.lower()


class TestAgentIntegration:
    """Test agent integration with workflow components."""

    def test_agents_have_no_tools_directly(self):
        """Test that agents don't have tools directly attached."""
        # Tools should be provided by workflow, not attached to agents
        agents = [
            query_parser_agent,
            economic_analyst_agent,
            news_analyst_agent,
            impact_synthesizer_agent,
        ]

        for agent in agents:
            assert agent.tools == [], f"Agent {agent.name} should not have tools directly"

    @patch('market_analysis_v2.agents.OpenAIChat')
    def test_model_initialization(self, mock_openai):
        """Test that model is properly initialized."""
        # The module should create a single model instance
        from importlib import reload
        import market_analysis_v2.agents

        # Reload module to trigger initialization
        reload(market_analysis_v2.agents)

        # Should have called OpenAIChat once during module init
        mock_openai.assert_called_with(id="gpt-4o-mini", temperature=0.7)

    def test_agent_names_match_workflow_expectations(self):
        """Test agent names match what workflow expects."""
        # These names should match what's used in workflow.py
        assert query_parser_agent.name == "Market Query Parser"
        assert economic_analyst_agent.name == "Economic Data Analyst"
        assert news_analyst_agent.name == "News & Sentiment Analyst"
        assert impact_synthesizer_agent.name == "Portfolio Impact Synthesizer"

    def test_agents_are_properly_exported(self):
        """Test that all agents are properly exported."""
        from market_analysis_v2 import agents

        # Check __all__ exports
        assert "query_parser_agent" in agents.__all__
        assert "economic_analyst_agent" in agents.__all__
        assert "news_analyst_agent" in agents.__all__
        assert "impact_synthesizer_agent" in agents.__all__
        assert "get_agent_for_step" in agents.__all__

        # Check actual exports
        assert hasattr(agents, "query_parser_agent")
        assert hasattr(agents, "economic_analyst_agent")
        assert hasattr(agents, "news_analyst_agent")
        assert hasattr(agents, "impact_synthesizer_agent")
        assert hasattr(agents, "get_agent_for_step")