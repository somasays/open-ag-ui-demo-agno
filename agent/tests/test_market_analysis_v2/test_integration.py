"""
Integration Tests for Market Analysis v2 Workflow

Comprehensive integration testing covering:
- Mocked integration tests (for fast CI/CD)
- Real API integration tests (when credentials available)
- Performance and timeout tests
- Edge case and boundary condition handling

This file complements test_validation.py which handles:
- Event sequence validation
- Semantic correctness validation
- End-to-end HTTP endpoint testing

Test sections:
1. Mocked Integration - Fast tests with mocked APIs for CI/CD
2. Real API Integration - Tests with actual API calls when INTEGRATION_TEST=true
3. Performance Tests - API response time and timeout handling
4. Edge Cases - Empty portfolios, large portfolios, malformed input
"""

import os
import pytest
import asyncio
from datetime import datetime
import json
import pandas as pd
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check if we should run real integration tests
SKIP_REAL_INTEGRATION = not os.getenv('INTEGRATION_TEST', '').lower() == 'true'
SKIP_REASON = "Set INTEGRATION_TEST=true and provide real API keys to run integration tests"

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agno.workflow.v2 import StepInput, StepOutput
from market_analysis_v2.workflow import (
    market_analysis_workflow,
    execute_query_analysis,
    execute_economic_data_step,
    execute_news_analysis_step,
    execute_impact_synthesis,
)
from market_analysis_v2.tools import FredDataTools, ExaSearchTools


# ============================================================================
# SECTION 1: MOCKED INTEGRATION TESTS (Always run - for CI/CD)
# ============================================================================

class TestMockedIntegration:
    """Integration tests with mocked external services for fast CI/CD testing."""

    @pytest.mark.asyncio
    async def test_workflow_data_flow_mocked(self):
        """Test that data flows correctly between workflow steps with mocked APIs."""

        with patch('market_analysis_v2.tools.Fred') as MockFred, \
             patch('market_analysis_v2.tools.Exa') as MockExa:

            # Setup mocks with traceable data
            mock_fred = MockFred.return_value
            # Return a pandas Series as expected by the code
            mock_fred.get_series.return_value = pd.Series(
                [5.5],
                index=[pd.Timestamp("2024-01-01")]
            )
            mock_fred.get_series_info.return_value = {
                'units': 'Percent',
                'title': 'Federal Funds Rate',
                'frequency': 'Monthly',
                'last_updated': '2024-01-15'
            }

            mock_exa = MockExa.return_value
            mock_result = MagicMock()
            mock_result.results = [
                MagicMock(
                    title="Fed Impact on Tech",
                    url="https://example.com",
                    text="Analysis of Federal Reserve impact on technology stocks",
                    published_date="2024-01-15"
                )
            ]
            mock_exa.search.return_value = mock_result

            # Test data flow through steps
            test_portfolio = ["AAPL", "MSFT"]
            test_query = "Fed impact on tech stocks"

            # Step 1: Query Analysis
            query_input = MagicMock(spec=StepInput)
            query_input.input = test_query
            query_input.additional_data = {
                "query": test_query,
                "portfolio": test_portfolio,
            }

            query_result = await execute_query_analysis(query_input)
            assert query_result.success
            assert test_portfolio == query_result.content["focus_tickers"][:2]

            # Step 2: Economic Data should use indicators from Step 1
            econ_input = MagicMock(spec=StepInput)
            econ_input.get_step_content = MagicMock(return_value=query_result.content)

            econ_result = await execute_economic_data_step(econ_input)
            assert econ_result.success

            # Verify FRED was called with correct indicators
            expected_indicators = query_result.content["economic_indicators"]
            assert mock_fred.get_series.call_count == len(expected_indicators)

            # Step 3: News Analysis should use keywords from Step 1
            news_input = MagicMock(spec=StepInput)
            news_input.input = test_query
            news_input.get_step_content = MagicMock(return_value=query_result.content)

            news_result = await execute_news_analysis_step(news_input)
            assert news_result.success

            # Step 4: Synthesis should combine all data
            synthesis_input = MagicMock(spec=StepInput)
            synthesis_input.input = test_query
            synthesis_input.additional_data = {"portfolio": test_portfolio}
            synthesis_input.get_step_content = MagicMock(side_effect=lambda x: {
                "economic_data": econ_result.content,
                "news_analysis": news_result.content,
            }.get(x, {}))

            synthesis_result = await execute_impact_synthesis(synthesis_input)
            assert synthesis_result.success
            assert synthesis_result.content["risk_level"] in ["HIGH", "MEDIUM", "LOW"]

    @pytest.mark.asyncio
    async def test_workflow_with_api_failures_mocked(self):
        """Test workflow resilience when external APIs fail."""

        with patch('market_analysis_v2.tools.Fred') as MockFred, \
             patch('market_analysis_v2.tools.Exa') as MockExa:

            # Setup APIs to fail
            MockFred.return_value.get_series.side_effect = Exception("FRED API Error")
            MockExa.return_value.search.side_effect = Exception("Exa API Error")

            # Step 1: Query Analysis (should succeed)
            query_input = MagicMock(spec=StepInput)
            query_input.input = "Market analysis"
            query_input.additional_data = {"query": "Market analysis", "portfolio": []}

            query_result = await execute_query_analysis(query_input)
            assert query_result.success

            # Step 2: Economic Data (should fail gracefully)
            econ_input = MagicMock(spec=StepInput)
            econ_input.get_step_content = MagicMock(return_value=query_result.content)

            econ_result = await execute_economic_data_step(econ_input)
            assert econ_result.success is False
            assert "error" in econ_result.content

            # Step 3: News Analysis (should handle failure)
            news_input = MagicMock(spec=StepInput)
            news_input.input = "Market analysis"
            news_input.get_step_content = MagicMock(return_value=query_result.content)

            news_result = await execute_news_analysis_step(news_input)
            assert news_result.success is True  # Returns success with empty data
            assert news_result.content["articles"] == []

            # Step 4: Synthesis (should produce degraded output)
            synthesis_input = MagicMock(spec=StepInput)
            synthesis_input.input = "Market analysis"
            synthesis_input.additional_data = {"portfolio": []}
            synthesis_input.get_step_content = MagicMock(side_effect=lambda x: {
                "economic_data": econ_result.content,
                "news_analysis": news_result.content,
            }.get(x, {}))

            synthesis_result = await execute_impact_synthesis(synthesis_input)
            assert synthesis_result.success
            assert "No economic data available" in synthesis_result.content["economic_impact"]


# ============================================================================
# SECTION 2: REAL API INTEGRATION TESTS (Requires credentials)
# ============================================================================

@pytest.mark.skipif(SKIP_REAL_INTEGRATION, reason=SKIP_REASON)
class TestRealAPIIntegration:
    """Integration tests with real API calls for thorough validation."""

    @pytest.mark.asyncio
    async def test_fred_api_direct(self):
        """Test direct FRED API integration."""
        if not os.getenv('FRED_API_KEY') or len(os.getenv('FRED_API_KEY', '')) != 32:
            pytest.skip("Valid FRED_API_KEY required")

        fred_tools = FredDataTools()

        # Test with real indicator
        result = await fred_tools.get_economic_indicators(["DFF"])

        assert result["success"] is True
        assert "economic_data" in result
        assert "federal_funds_rate" in result["economic_data"]

        # Verify data structure
        fed_data = result["economic_data"]["federal_funds_rate"]
        assert "data" in fed_data or "values" in fed_data
        assert "last_updated" in fed_data

    @pytest.mark.asyncio
    async def test_exa_api_direct(self):
        """Test direct Exa API integration."""
        if not os.getenv('EXA_API_KEY'):
            pytest.skip("Valid EXA_API_KEY required")

        exa_tools = ExaSearchTools()

        # Test with real search
        result = await exa_tools.search_portfolio_news(
            query="Federal Reserve interest rates",
            portfolio_tickers=["AAPL"],
            num_results=2
        )

        assert result["success"] is True
        assert "news_results" in result

        # Should have results (after domain filter fix)
        if len(result["news_results"]) > 0:
            first_article = result["news_results"][0]
            assert "title" in first_article
            assert "url" in first_article
            assert "snippet" in first_article

    @pytest.mark.asyncio
    async def test_complete_workflow_real_apis(self):
        """Test the entire workflow with real API calls."""
        if not (os.getenv('FRED_API_KEY') and os.getenv('EXA_API_KEY')):
            pytest.skip("Both FRED and EXA API keys required")

        test_query = "What is the current Federal Reserve interest rate impact on tech?"
        test_portfolio = ["AAPL", "MSFT"]

        # Run complete workflow
        test_input = MagicMock(spec=StepInput)
        test_input.input = test_query
        test_input.additional_data = {
            "query": test_query,
            "portfolio": test_portfolio,
        }

        # Execute all steps
        query_result = await execute_query_analysis(test_input)
        assert query_result.success

        econ_input = MagicMock(spec=StepInput)
        econ_input.get_step_content = MagicMock(return_value=query_result.content)
        econ_result = await execute_economic_data_step(econ_input)
        assert econ_result.success

        news_input = MagicMock(spec=StepInput)
        news_input.input = test_query
        news_input.get_step_content = MagicMock(return_value=query_result.content)
        news_result = await execute_news_analysis_step(news_input)
        assert news_result.success

        synthesis_input = MagicMock(spec=StepInput)
        synthesis_input.input = test_query
        synthesis_input.additional_data = {"portfolio": test_portfolio}
        synthesis_input.get_step_content = MagicMock(side_effect=lambda x: {
            "economic_data": econ_result.content,
            "news_analysis": news_result.content,
        }.get(x, {}))

        synthesis_result = await execute_impact_synthesis(synthesis_input)
        assert synthesis_result.success
        assert synthesis_result.content["risk_level"] in ["HIGH", "MEDIUM", "LOW"]

        print(f"✅ Real Integration Complete:")
        print(f"   - Economic indicators: {len(econ_result.content.get('raw_data', {}))}")
        print(f"   - News articles: {len(news_result.content.get('articles', []))}")
        print(f"   - Risk level: {synthesis_result.content['risk_level']}")


# ============================================================================
# SECTION 3: PERFORMANCE TESTS
# ============================================================================

@pytest.mark.skipif(SKIP_REAL_INTEGRATION, reason=SKIP_REASON)
class TestAPIPerformance:
    """Test API performance and timeout handling."""

    @pytest.mark.asyncio
    async def test_fred_api_performance(self):
        """Measure FRED API response time."""
        if not os.getenv('FRED_API_KEY'):
            pytest.skip("FRED_API_KEY required")

        fred_tools = FredDataTools()
        indicators = ["DFF", "CPIAUCSL", "GDP", "UNRATE"]

        start_time = datetime.now()
        result = await fred_tools.get_economic_indicators(indicators)
        duration = (datetime.now() - start_time).total_seconds()

        assert result["success"] is True
        assert duration < 30, f"FRED API too slow: {duration}s"

        print(f"✅ FRED API Performance: {duration:.2f}s for {len(indicators)} indicators")

    @pytest.mark.asyncio
    async def test_exa_api_performance(self):
        """Measure Exa API response time."""
        if not os.getenv('EXA_API_KEY'):
            pytest.skip("EXA_API_KEY required")

        exa_tools = ExaSearchTools()

        start_time = datetime.now()
        result = await exa_tools.search_portfolio_news(
            query="stock market analysis",
            portfolio_tickers=["AAPL", "GOOGL", "MSFT"],
            num_results=10
        )
        duration = (datetime.now() - start_time).total_seconds()

        assert result["success"] is True
        assert duration < 30, f"Exa API too slow: {duration}s"

        print(f"✅ Exa API Performance: {duration:.2f}s for 10 results")

    @pytest.mark.asyncio
    async def test_tool_timeout_handling(self):
        """Test that tools handle timeouts correctly."""

        with patch('market_analysis_v2.tools.Fred') as MockFred:
            # Simulate slow API
            async def slow_operation(*args, **kwargs):
                await asyncio.sleep(35)  # Longer than 30s timeout
                return []

            mock_fred = MockFred.return_value
            mock_fred.get_series = slow_operation

            fred_tools = FredDataTools()

            # Should timeout and return partial results
            with patch('asyncio.wait_for', side_effect=asyncio.TimeoutError):
                result = await fred_tools.get_economic_indicators(["DFF"])

                assert result["success"] is True  # Partial success
                assert len(result["errors"]) > 0
                assert "timeout" in result["errors"][0].lower()


# ============================================================================
# SECTION 4: EDGE CASES AND SPECIAL SCENARIOS
# ============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    @pytest.mark.asyncio
    async def test_empty_portfolio(self):
        """Test workflow with no portfolio holdings."""
        query_input = MagicMock(spec=StepInput)
        query_input.input = "General market analysis"
        query_input.additional_data = {
            "query": "General market analysis",
            "portfolio": [],  # Empty portfolio
        }

        result = await execute_query_analysis(query_input)
        assert result.success
        assert result.content["focus_tickers"] == []
        assert result.content["analysis_type"] == "general_market"

    @pytest.mark.asyncio
    async def test_large_portfolio(self):
        """Test workflow with a very large portfolio."""
        large_portfolio = [f"STOCK{i}" for i in range(100)]

        query_input = MagicMock(spec=StepInput)
        query_input.input = "Portfolio analysis"
        query_input.additional_data = {
            "query": "Portfolio analysis",
            "portfolio": large_portfolio,
        }

        result = await execute_query_analysis(query_input)
        assert result.success
        # Should limit to first 5 tickers
        assert len(result.content["focus_tickers"]) == 5
        assert result.content["focus_tickers"] == large_portfolio[:5]

    @pytest.mark.asyncio
    async def test_malformed_input_handling(self):
        """Test workflow with malformed or missing input."""
        # Test with missing input attribute
        bad_input = MagicMock(spec=StepInput)
        bad_input.additional_data = {}
        # Don't set input attribute

        result = await execute_query_analysis(bad_input)
        assert result.success  # Should handle gracefully
        assert result.content["analysis_type"] == "general_market"  # Uses defaults

    @pytest.mark.asyncio
    async def test_different_query_types(self):
        """Test workflow with various types of market queries."""
        test_cases = [
            {
                "query": "What's the inflation outlook?",
                "expected_type": "inflation_analysis",
                "expected_indicators": ["CPIAUCSL"]
            },
            {
                "query": "unemployment rate analysis",  # More explicit query
                "expected_type": "employment",
                "expected_indicators": ["UNRATE"]
            },
            {
                "query": "GDP growth analysis",  # More explicit query
                "expected_type": "gdp_analysis",
                "expected_indicators": ["GDP"]
            },
            {
                "query": "General market conditions",
                "expected_type": "general_market",
                "expected_indicators": ["DFF", "CPIAUCSL", "GDP", "UNRATE"]
            }
        ]

        for test_case in test_cases:
            query_input = MagicMock(spec=StepInput)
            query_input.input = test_case["query"]
            query_input.additional_data = {
                "query": test_case["query"],
                "portfolio": []
            }

            result = await execute_query_analysis(query_input)
            assert result.success
            assert result.content["analysis_type"] == test_case["expected_type"]

            # Check that appropriate indicators are selected
            for indicator in test_case["expected_indicators"]:
                assert indicator in result.content["economic_indicators"], \
                    f"Expected {indicator} for {test_case['query']}"


# ============================================================================
# TEST UTILITIES
# ============================================================================

def print_test_summary():
    """Print test organization summary."""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                INTEGRATION TEST SUITE                             ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                   ║
║  1. MOCKED TESTS (Always run - for CI/CD):                      ║
║     pytest test_integration.py::TestMockedIntegration            ║
║                                                                   ║
║  2. REAL API TESTS (Requires credentials):                      ║
║     export INTEGRATION_TEST=true                                 ║
║     export FRED_API_KEY="your-key"                              ║
║     export EXA_API_KEY="your-key"                               ║
║     pytest test_integration.py::TestRealAPIIntegration           ║
║                                                                   ║
║  3. PERFORMANCE TESTS:                                          ║
║     pytest test_integration.py::TestAPIPerformance               ║
║                                                                   ║
║  4. EDGE CASE TESTS:                                            ║
║     pytest test_integration.py::TestEdgeCases                    ║
║                                                                   ║
║  Run all tests:                                                 ║
║     pytest test_integration.py -v                                ║
║                                                                   ║
╚══════════════════════════════════════════════════════════════════╝
    """)


if __name__ == "__main__":
    print_test_summary()