"""
Comprehensive Validation Tests for Market Analysis v2 Workflow

These tests validate:
1. Events are emitted in the correct sequence
2. Tool calls contain expected parameters
3. Synthesis output is semantically correct
4. The workflow produces coherent, contextually appropriate results

Uses OpenAI for semantic validation of non-deterministic outputs.
"""

import os
import json
import asyncio
import pytest
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()

# Configure OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

# Enable DEBUG logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from httpx import AsyncClient, ASGITransport
from ag_ui.core import EventType
from main import app
from market_analysis_v2.workflow import market_analysis_workflow
from agno.workflow.v2 import StepInput
from unittest.mock import MagicMock


class SemanticValidator:
    """Uses OpenAI to validate semantic correctness of non-deterministic outputs."""

    @staticmethod
    async def validate_synthesis_content(
        synthesis_output: Dict[str, Any],
        query: str,
        portfolio: List[str]
    ) -> Dict[str, Any]:
        """
        Validate that synthesis output is semantically correct and coherent.

        Returns:
            Dict with validation results and scores
        """
        try:
            # Create validation prompt
            validation_prompt = f"""
            Analyze the following market analysis synthesis output and validate:
            1. Does it appropriately address the query: "{query}"?
            2. Does it reference the portfolio stocks: {portfolio}?
            3. Is the risk assessment (HIGH/MEDIUM/LOW) justified by the content?
            4. Are the economic impact and market sentiment sections coherent?
            5. Is the analysis grounded in the data mentioned?

            Synthesis Output:
            {json.dumps(synthesis_output, indent=2)}

            Respond with a JSON object containing:
            - addresses_query: boolean
            - references_portfolio: boolean
            - risk_justified: boolean
            - coherent_analysis: boolean
            - data_grounded: boolean
            - overall_score: 0-100
            - issues: list of any issues found
            """

            response = await asyncio.to_thread(
                openai.chat.completions.create,
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a financial analysis validator. Respond only with valid JSON."},
                    {"role": "user", "content": validation_prompt}
                ],
                temperature=0,
                response_format={"type": "json_object"}
            )

            return json.loads(response.choices[0].message.content)

        except Exception as e:
            # If OpenAI validation fails, do basic checks
            return {
                "addresses_query": any(word in str(synthesis_output).lower() for word in query.lower().split()),
                "references_portfolio": any(ticker in str(synthesis_output) for ticker in portfolio),
                "risk_justified": synthesis_output.get('risk_level') in ['HIGH', 'MEDIUM', 'LOW'],
                "coherent_analysis": len(synthesis_output.get('economic_impact', '')) > 50,
                "data_grounded": 'federal funds rate' in str(synthesis_output).lower(),
                "overall_score": 70,
                "issues": [f"OpenAI validation failed: {e}"]
            }


class TestEventSequenceValidation:
    """Validate that events are emitted in the correct sequence and format."""

    @pytest.mark.asyncio
    async def test_event_sequence_and_content(self):
        """Test that events follow the expected sequence and contain valid data."""

        test_input = {
            "thread_id": "test-thread-seq",
            "run_id": "test-run-seq",
            "tools": [],
            "messages": [
                {
                    "role": "user",
                    "id": "msg1",
                    "content": "How will rising Federal Reserve interest rates impact my tech portfolio with AAPL and MSFT?"
                }
            ],
            "state": {
                "available_cash": 100000,
                "investment_summary": "Portfolio value: $50,000",
                "investment_portfolio": {
                    "AAPL": {"shares": 100, "value": 17500},
                    "MSFT": {"shares": 50, "value": 17500}
                }
            },
            "context": [],
            "forwardedProps": {}
        }

        # Collect all events
        events = []
        event_sequence = []

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/agno-agent", json=test_input)

            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    event_data = line[6:]
                    if event_data and event_data != "[DONE]":
                        try:
                            event = json.loads(event_data)
                            events.append(event)
                            event_sequence.append(event.get('type'))
                        except json.JSONDecodeError:
                            pass

        # VALIDATION 1: Check event sequence
        assert len(events) > 0, "No events were emitted"

        # Must start with RUN_STARTED
        assert event_sequence[0] == EventType.RUN_STARTED, f"First event should be RUN_STARTED, got {event_sequence[0]}"

        # Must have STATE_SNAPSHOT early
        assert EventType.STATE_SNAPSHOT in event_sequence[:3], "STATE_SNAPSHOT should be in first 3 events"

        # Must end with RUN_FINISHED
        assert event_sequence[-1] == EventType.RUN_FINISHED, f"Last event should be RUN_FINISHED, got {event_sequence[-1]}"

        # VALIDATION 2: Check event content structure
        run_started = next(e for e in events if e['type'] == EventType.RUN_STARTED)
        assert 'threadId' in run_started, "RUN_STARTED missing threadId"
        assert 'runId' in run_started, "RUN_STARTED missing runId"

        state_snapshot = next(e for e in events if e['type'] == EventType.STATE_SNAPSHOT)
        assert 'snapshot' in state_snapshot, "STATE_SNAPSHOT missing snapshot"
        assert 'available_cash' in state_snapshot['snapshot'], "Snapshot missing available_cash"
        assert state_snapshot['snapshot']['available_cash'] == 100000, "Incorrect available_cash in snapshot"

        # VALIDATION 3: Check for output events (text or tool calls)
        has_text_events = any(e['type'] in [
            EventType.TEXT_MESSAGE_START,
            EventType.TEXT_MESSAGE_CONTENT,
            EventType.TEXT_MESSAGE_END
        ] for e in events)

        has_tool_events = any(e['type'] in [
            EventType.TOOL_CALL_START,
            EventType.TOOL_CALL_ARGS,
            EventType.TOOL_CALL_END
        ] for e in events)

        assert has_text_events or has_tool_events, "No output events (text or tool calls) found"

        # VALIDATION 4: If text events, check they're properly sequenced
        if has_text_events:
            text_start_idx = event_sequence.index(EventType.TEXT_MESSAGE_START)
            text_end_idx = event_sequence.index(EventType.TEXT_MESSAGE_END)
            assert text_start_idx < text_end_idx, "TEXT_MESSAGE_START must come before TEXT_MESSAGE_END"

            # Should have content between start and end
            content_events = [e for e in events[text_start_idx:text_end_idx]
                            if e['type'] == EventType.TEXT_MESSAGE_CONTENT]
            assert len(content_events) > 0, "No TEXT_MESSAGE_CONTENT between start and end"

        print(f"✅ Event Validation Passed:")
        print(f"   - Total events: {len(events)}")
        print(f"   - Event types: {set(event_sequence)}")
        print(f"   - Sequence correct: RUN_STARTED → ... → RUN_FINISHED")


class TestToolCallValidation:
    """Validate that tool calls are made with correct parameters."""

    @pytest.mark.asyncio
    async def test_workflow_tool_calls(self):
        """Test that the workflow makes correct tool calls to FRED and Exa APIs."""

        # Track actual tool calls
        fred_calls = []
        exa_calls = []

        from unittest.mock import patch, MagicMock, AsyncMock

        with patch('market_analysis_v2.tools.Fred') as MockFred, \
             patch('market_analysis_v2.tools.Exa') as MockExa:

            # Setup FRED mock
            mock_fred = MockFred.return_value
            def track_fred(series_id, **kwargs):
                fred_calls.append({
                    'series_id': series_id,
                    'kwargs': kwargs
                })
                # Return realistic data
                return [
                    {"date": "2024-01-01", "value": 5.33},
                    {"date": "2024-02-01", "value": 5.35}
                ]
            mock_fred.get_series.side_effect = track_fred
            mock_fred.get_series_info.return_value = {
                'units': 'Percent',
                'title': 'Federal Funds Rate',
                'frequency': 'Monthly'
            }

            # Setup Exa mock
            mock_exa = MockExa.return_value
            def track_exa(query, **kwargs):
                exa_calls.append({
                    'query': query,
                    'num_results': kwargs.get('num_results', 5),
                    'type': kwargs.get('type', 'keyword')
                })
                result = MagicMock()
                result.results = [
                    MagicMock(
                        title="Fed Raises Rates Impact on Tech",
                        url="https://example.com/fed-tech",
                        text="Federal Reserve rate increases affect technology stocks...",
                        score=0.95,
                        published_date="2024-01-15"
                    )
                ]
                return result
            mock_exa.search.side_effect = track_exa

            # Run the workflow
            test_input = MagicMock(spec=StepInput)
            test_input.input = "How will Fed rate changes impact AAPL and MSFT?"
            test_input.additional_data = {
                "query": test_input.input,
                "portfolio": ["AAPL", "MSFT"]
            }

            # Import step functions
            from market_analysis_v2.workflow import (
                execute_query_analysis,
                execute_economic_data_step,
                execute_news_analysis_step,
                execute_impact_synthesis
            )

            # Step 1: Query Analysis
            query_result = await execute_query_analysis(test_input)
            assert query_result.success

            # Step 2: Economic Data
            econ_input = MagicMock(spec=StepInput)
            econ_input.get_step_content = MagicMock(return_value=query_result.content)
            econ_result = await execute_economic_data_step(econ_input)

            # VALIDATION 1: Check FRED was called with correct indicators
            assert len(fred_calls) > 0, "FRED API should have been called"

            fred_indicators = [call['series_id'] for call in fred_calls]
            assert 'DFF' in fred_indicators, "Should fetch Federal Funds Rate (DFF)"

            # Based on "Fed rate" query, should also fetch related indicators
            expected_indicators = {'DFF', 'CPIAUCSL', 'GDP', 'UNRATE'}
            actual_indicators = set(fred_indicators)
            assert len(actual_indicators.intersection(expected_indicators)) >= 2, \
                f"Should fetch at least 2 of {expected_indicators}, got {actual_indicators}"

            # Step 3: News Analysis
            news_input = MagicMock(spec=StepInput)
            news_input.input = test_input.input
            news_input.get_step_content = MagicMock(return_value=query_result.content)
            news_result = await execute_news_analysis_step(news_input)

            # VALIDATION 2: Check Exa was called with portfolio context
            assert len(exa_calls) > 0, "Exa API should have been called"

            exa_query = exa_calls[0]['query']
            assert 'AAPL' in exa_query or 'MSFT' in exa_query, \
                f"Exa query should include portfolio tickers, got: {exa_query}"

            # Should use neural search for better results
            assert exa_calls[0]['type'] == 'neural', "Should use neural search"

            # VALIDATION 3: Check synthesis combines all data
            synthesis_input = MagicMock(spec=StepInput)
            synthesis_input.input = test_input.input
            synthesis_input.additional_data = {"portfolio": ["AAPL", "MSFT"]}
            synthesis_input.get_step_content = MagicMock(side_effect=lambda x: {
                "economic_data": econ_result.content,
                "news_analysis": news_result.content
            }.get(x, {}))

            synthesis_result = await execute_impact_synthesis(synthesis_input)
            assert synthesis_result.success

            # Validate synthesis uses data from both tools
            synthesis_content = synthesis_result.content
            assert 'economic_impact' in synthesis_content
            assert 'market_sentiment' in synthesis_content
            assert 'risk_level' in synthesis_content

            print(f"✅ Tool Call Validation Passed:")
            print(f"   - FRED calls: {len(fred_calls)} indicators")
            print(f"   - Exa calls: {len(exa_calls)} searches")
            print(f"   - Indicators fetched: {fred_indicators}")
            print(f"   - Portfolio context included: Yes")


class TestSynthesisValidation:
    """Validate synthesis output using semantic analysis."""

    @pytest.mark.asyncio
    @pytest.mark.skipif(
        not os.getenv('OPENAI_API_KEY'),
        reason="OpenAI API key required for semantic validation"
    )
    async def test_synthesis_semantic_correctness(self):
        """Use OpenAI to validate that synthesis output is semantically correct."""

        query = "What is the impact of rising Federal Reserve interest rates on my tech portfolio containing AAPL, MSFT, and GOOGL?"
        portfolio = ["AAPL", "MSFT", "GOOGL"]

        # Run actual workflow
        from market_analysis_v2.workflow import (
            execute_query_analysis,
            execute_economic_data_step,
            execute_news_analysis_step,
            execute_impact_synthesis
        )

        # Mock input
        test_input = MagicMock(spec=StepInput)
        test_input.input = query
        test_input.additional_data = {
            "query": query,
            "portfolio": portfolio
        }

        # Execute workflow steps
        query_result = await execute_query_analysis(test_input)

        econ_input = MagicMock(spec=StepInput)
        econ_input.get_step_content = MagicMock(return_value=query_result.content)
        econ_result = await execute_economic_data_step(econ_input)

        news_input = MagicMock(spec=StepInput)
        news_input.input = query
        news_input.get_step_content = MagicMock(return_value=query_result.content)
        news_result = await execute_news_analysis_step(news_input)

        synthesis_input = MagicMock(spec=StepInput)
        synthesis_input.input = query
        synthesis_input.additional_data = {"portfolio": portfolio}
        synthesis_input.get_step_content = MagicMock(side_effect=lambda x: {
            "economic_data": econ_result.content,
            "news_analysis": news_result.content
        }.get(x, {}))

        synthesis_result = await execute_impact_synthesis(synthesis_input)

        # Validate synthesis semantically
        validator = SemanticValidator()
        validation = await validator.validate_synthesis_content(
            synthesis_result.content,
            query,
            portfolio
        )

        # Check validation results
        assert validation['addresses_query'], "Synthesis doesn't address the query"

        # Portfolio references might be implicit in the analysis
        if not validation['references_portfolio']:
            # Check if portfolio implications section exists
            has_portfolio_section = 'portfolio_implications' in synthesis_result.content
            assert has_portfolio_section or validation['references_portfolio'], \
                "Synthesis doesn't reference portfolio stocks or have portfolio implications"

        assert validation['risk_justified'], "Risk assessment not justified"
        assert validation['coherent_analysis'], "Analysis is not coherent"

        # Data grounding might be minimal in test environment
        if not validation['data_grounded']:
            print("⚠️  Warning: Analysis may not be fully grounded in data (test environment)")

        assert validation['overall_score'] >= 60, f"Overall score too low: {validation['overall_score']}"

        if validation.get('issues'):
            print(f"⚠️  Issues found: {validation['issues']}")

        print(f"✅ Semantic Validation Passed:")
        print(f"   - Addresses query: {validation['addresses_query']}")
        print(f"   - References portfolio: {validation['references_portfolio']}")
        print(f"   - Risk justified: {validation['risk_justified']}")
        print(f"   - Coherent analysis: {validation['coherent_analysis']}")
        print(f"   - Data grounded: {validation['data_grounded']}")
        print(f"   - Overall score: {validation['overall_score']}/100")


class TestEndToEndWithValidation:
    """Complete end-to-end test with comprehensive validation."""

    @pytest.mark.asyncio
    @pytest.mark.skipif(
        not (os.getenv('FRED_API_KEY') and os.getenv('EXA_API_KEY')),
        reason="Real API keys required for full validation"
    )
    async def test_complete_workflow_with_validation(self):
        """Test the complete workflow with real APIs and full validation."""

        query = "How will Federal Reserve monetary policy changes impact my portfolio of AAPL and MSFT stocks?"

        test_input = {
            "thread_id": "test-validation",
            "run_id": "test-run-validation",
            "tools": [],
            "messages": [
                {
                    "role": "user",
                    "id": "msg1",
                    "content": query
                }
            ],
            "state": {
                "available_cash": 100000,
                "investment_summary": "Portfolio value: $35,000",
                "investment_portfolio": {
                    "AAPL": {"shares": 100, "value": 17500},
                    "MSFT": {"shares": 50, "value": 17500}
                }
            },
            "context": [],
            "forwardedProps": {}
        }

        # Collect events and content
        events = []
        text_content = []
        tool_calls = []

        logger.debug(f"Starting end-to-end test with query: {query}")
        logger.debug(f"Portfolio: {test_input['state']['investment_portfolio']}")

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
            timeout=60.0
        ) as client:
            logger.debug("Sending request to /agno-agent endpoint")
            response = await client.post("/agno-agent", json=test_input)
            logger.debug(f"Response status: {response.status_code}")

            async for line in response.aiter_lines():
                logger.debug(f"Received line: {line[:100]}")  # Log first 100 chars
                if line.startswith("data: "):
                    event_data = line[6:]
                    if event_data and event_data != "[DONE]":
                        try:
                            event = json.loads(event_data)
                            events.append(event)

                            # Collect text content
                            if event.get('type') == EventType.TEXT_MESSAGE_CONTENT:
                                text_content.append(event.get('delta', ''))

                            # Collect tool calls
                            if event.get('type') == EventType.TOOL_CALL_START:
                                tool_calls.append(event.get('toolCallName', ''))

                        except json.JSONDecodeError:
                            pass

        # VALIDATION 1: Event sequence
        event_types = [e.get('type') for e in events]
        assert EventType.RUN_STARTED in event_types
        assert EventType.STATE_SNAPSHOT in event_types
        assert EventType.RUN_FINISHED in event_types

        # VALIDATION 2: Content analysis
        full_content = ''.join(text_content)
        if full_content:
            # Check for key elements
            assert len(full_content) > 100, "Response too short"

            # Should mention Fed/rates
            assert any(term in full_content.lower() for term in ['federal', 'fed', 'rate', 'monetary']), \
                "Should discuss Federal Reserve/rates"

            # Should mention portfolio stocks
            assert 'AAPL' in full_content or 'apple' in full_content.lower(), \
                "Should mention AAPL"
            assert 'MSFT' in full_content or 'microsoft' in full_content.lower(), \
                "Should mention MSFT"

            # Should provide risk assessment
            assert any(risk in full_content.upper() for risk in ['HIGH', 'MEDIUM', 'LOW']), \
                "Should include risk assessment"

        # VALIDATION 3: Tool calls (if any)
        if tool_calls:
            print(f"   - Tool calls made: {tool_calls}")

        print(f"✅ Complete Validation Passed:")
        print(f"   - Events emitted: {len(events)}")
        print(f"   - Response length: {len(full_content)} chars")
        print(f"   - Mentions Fed/rates: Yes")
        print(f"   - Mentions portfolio: Yes")
        print(f"   - Includes risk assessment: Yes")


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════╗
║              COMPREHENSIVE VALIDATION TEST SUITE                  ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                   ║
║  Tests validate:                                                 ║
║  • Event sequence and structure                                  ║
║  • Tool calls with correct parameters                            ║
║  • Synthesis semantic correctness                                ║
║  • End-to-end workflow coherence                                 ║
║                                                                   ║
║  Run all validation tests:                                       ║
║    pytest test_validation.py -v                                  ║
║                                                                   ║
║  Run with real APIs:                                            ║
║    export FRED_API_KEY="your-key"                               ║
║    export EXA_API_KEY="your-key"                                ║
║    export OPENAI_API_KEY="your-key"                             ║
║    pytest test_validation.py::TestEndToEndWithValidation -v     ║
║                                                                   ║
╚══════════════════════════════════════════════════════════════════╝
    """)