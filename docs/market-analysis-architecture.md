# Full-Stack Architecture Document: Market Analysis Feature

## Executive Summary

This document provides a comprehensive full-stack architecture specification for the Market Analysis feature, building on the existing AI-powered stock portfolio application. The feature introduces autonomous market intelligence capabilities that allow users to ask natural language questions about economic conditions affecting their portfolio holdings. The architecture leverages the existing Agno workflow system and AG-UI streaming infrastructure while introducing new external API integrations (FRED and Exa) and enhanced frontend components.

**Key Architectural Decisions:**
- **Migration Path**: Transition from Agno Workflow v1 to v2 patterns for better maintainability
- **Streaming Architecture**: Leverage existing AG-UI EventEncoder patterns for real-time analysis delivery
- **API Integration**: Direct integration with FRED and Exa APIs following established error handling patterns
- **State Management**: Extend existing CopilotKit useCoAgent state management for market analysis data
- **Component Architecture**: Progressive disclosure UI components that match existing portfolio analysis patterns

## Current Implementation Analysis

### Existing Architecture Assessment

#### Backend Implementation (`agent/main.py` and `agent/stock_analysis.py`)

**Current Agno Workflow Pattern (v1):**
```python
stock_analysis_workflow = Workflow(
    name="Mixed Execution Pipeline",
    steps=[chat, simultion, cash_allocation, gather_insights],  # Function references
)
```

**Current Strengths:**
- ✅ **AG-UI Integration**: Proper use of EventEncoder for SSE streaming
- ✅ **State Management**: Comprehensive StateDeltaEvent usage for UI updates
- ✅ **Tool Logging**: Real-time progress feedback via tool_logs array
- ✅ **Error Handling**: Graceful failure handling with partial results
- ✅ **Performance Data**: Complex portfolio calculations with SPY benchmarking

**Areas for Improvement:**
- ⚠️ **Workflow Pattern**: Using v1 function-based steps vs recommended v2 Step objects
- ⚠️ **Agent Definition**: Missing explicit Agent definitions for workflow steps
- ⚠️ **Database Integration**: No persistence layer (SqliteDb) for session management
- ⚠️ **Streaming Optimization**: Limited use of available AG-UI event types

#### Frontend Implementation

**Current CopilotKit Integration:**
- Proper useCoAgent state management
- Well-structured tool call handling via useCopilotAction
- Progressive chart rendering with streaming data

**Streaming Patterns:**
- Effective use of AG-UI events for real-time updates
- Proper state synchronization between backend and frontend
- Good error state handling

## Recommended Architecture

### Hybrid Implementation Strategy: Agno v1 + v2 Coexistence

**CRITICAL**: To minimize risk and maintain stability, we recommend a hybrid approach that keeps existing Agno v1 code unchanged while implementing new Market Analysis features using Agno v2 patterns.

#### Directory Structure for Isolation

```
agent/
├── main.py                      # Modified router (handles both v1 and v2)
├── stock_analysis.py            # UNCHANGED (Agno v1 existing code)
├── market_analysis_v2/          # NEW (Agno v2 patterns)
│   ├── __init__.py
│   ├── workflow.py              # Agno v2 workflow with Steps
│   ├── agents.py                # Explicit Agent definitions
│   └── tools.py                 # FRED and Exa tool functions
└── shared/                      # Shared utilities
    ├── streaming.py             # Unified AG-UI event handling
    └── api_clients.py           # Shared API client instances
```

#### Dual Workflow Router Implementation

```python
# agent/main.py - Modified to support both Agno v1 and v2 patterns
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from stock_analysis import stock_analysis_workflow  # Agno v1 (unchanged)
from market_analysis_v2.workflow import market_analysis_workflow  # Agno v2 (new)
from shared.streaming import UnifiedEventEmitter

app = FastAPI()

def is_market_query(message_content: str) -> bool:
    """Detect if query is for market analysis"""
    market_keywords = ['market', 'economy', 'fed', 'inflation', 'news', 'sector']
    return any(keyword in message_content.lower() for keyword in market_keywords)

@app.post("/agno-agent")
async def agno_agent(input_data: RunAgentInput):
    # Route to appropriate workflow based on query type
    if is_market_query(input_data.messages[-1].content):
        return await handle_v2_workflow(input_data, market_analysis_workflow)
    else:
        return await handle_v1_workflow(input_data, stock_analysis_workflow)

async def handle_v1_workflow(input_data, workflow):
    """Existing v1 pattern - NO CHANGES to maintain stability"""
    async def event_generator():
        encoder = EventEncoder()
        event_queue = asyncio.Queue()

        def emit_event(event):
            event_queue.put_nowait(event)

        # Keep existing v1 implementation exactly as is
        agent_task = asyncio.create_task(
            workflow.arun(
                additional_data={
                    "messages": input_data.messages,
                    "emit_event": emit_event,
                    "available_cash": input_data.state["available_cash"],
                    "investment_portfolio": input_data.state["investment_portfolio"],
                    "tool_logs": []
                }
            )
        )
        # ... rest of existing v1 implementation

    return StreamingResponse(event_generator(), media_type="text/event-stream")

async def handle_v2_workflow(input_data, workflow):
    """New v2 pattern with compatibility wrapper"""
    async def event_generator():
        encoder = EventEncoder()
        emitter = UnifiedEventEmitter(encoder)

        # Agno v2 workflows have different execution pattern
        async for event in workflow.arun(
            message=input_data.messages[-1].content,
            stream=True,
            stream_intermediate_steps=True,
            context={
                "portfolio": input_data.state["investment_portfolio"],
                "cash": input_data.state["available_cash"]
            }
        ):
            # Convert Agno v2 events to AG-UI format
            ag_ui_event = emitter.convert_v2_event(event)
            yield ag_ui_event

    return StreamingResponse(event_generator(), media_type="text/event-stream")
```

### Backend Architecture (Enhanced Agno v2 Pattern)

#### 1. Market Analysis Workflow (`agent/market_analysis.py`)

**Recommended Agno v2 Implementation:**

```python
from agno.workflow.v2 import Step, Workflow, StepOutput
from agno.agent.agent import Agent
from agno.models.openai.chat import OpenAIChat
from agno.db.sqlite import SqliteDb

# Define specialized agents for each workflow step
query_parser_agent = Agent(
    name="Market Query Parser",
    model=OpenAIChat(id="gpt-4o-mini"),
    instructions="Parse natural language market questions and identify required data sources",
    tools=[parse_market_query_tool]
)

economic_analyst_agent = Agent(
    name="Economic Data Analyst",
    model=OpenAIChat(id="gpt-4o-mini"),
    instructions="Analyze FRED economic data and correlate with portfolio holdings",
    tools=[fred_data_tools]
)

news_analyst_agent = Agent(
    name="News & Sentiment Analyst",
    model=OpenAI Chat(id="gpt-4o-mini"),
    instructions="Search and analyze relevant news using Exa neural search",
    tools=[exa_search_tools]
)

impact_synthesizer_agent = Agent(
    name="Portfolio Impact Synthesizer",
    model=OpenAIChat(id="gpt-4o-mini"),
    instructions="Synthesize economic and news data into portfolio-specific insights",
    tools=[portfolio_impact_tools]
)

# Define workflow steps using Step objects
query_analysis_step = Step(
    name="Query Analysis",
    agent=query_parser_agent,
    description="Parse user query and identify required data sources"
)

economic_data_step = Step(
    name="Economic Data Gathering",
    agent=economic_analyst_agent,
    description="Fetch and analyze relevant FRED economic indicators"
)

news_analysis_step = Step(
    name="News Analysis",
    agent=news_analyst_agent,
    description="Search and analyze relevant market news via Exa"
)

impact_synthesis_step = Step(
    name="Impact Synthesis",
    agent=impact_synthesizer_agent,
    description="Synthesize data into portfolio-specific insights"
)

# Create workflow with proper Step objects
market_analysis_workflow = Workflow(
    name="Market Analysis Pipeline",
    description="Autonomous market intelligence analysis for portfolio context",
    steps=[
        query_analysis_step,
        economic_data_step,
        news_analysis_step,
        impact_synthesis_step
    ],
    db=SqliteDb(
        session_table="market_analysis_session",
        db_file="tmp/market_analysis.db"
    )
)
```

#### 2. Enhanced API Integration Architecture

**FRED API Integration (`agent/tools/fred_tools.py`):**

```python
from fredapi import Fred
from agno.tools import Tool
import asyncio
from datetime import datetime, timedelta

class FredDataTools(Tool):
    """FRED economic data integration with proper error handling"""

    def __init__(self):
        self.fred = Fred(api_key=os.getenv('FRED_API_KEY'))
        super().__init__(
            name="FRED Economic Data",
            description="Fetch Federal Reserve economic data with error recovery"
        )

    async def get_economic_indicators(self, indicators: List[str]) -> Dict:
        """Fetch multiple economic indicators with parallel processing"""
        results = {}
        errors = []

        async def fetch_indicator(indicator_id: str, series_name: str):
            try:
                # Use asyncio timeout for each API call
                async with asyncio.timeout(30):
                    data = await asyncio.to_thread(
                        self.fred.get_series,
                        indicator_id,
                        limit=12  # Last 12 data points
                    )
                    results[series_name] = {
                        'data': data,
                        'last_updated': datetime.now().isoformat(),
                        'source': f'FRED/{indicator_id}'
                    }
            except asyncio.TimeoutError:
                errors.append(f"FRED API timeout for {series_name}")
            except Exception as e:
                errors.append(f"FRED API error for {series_name}: {str(e)}")

        # Parallel fetching of indicators
        tasks = [
            fetch_indicator('DFF', 'federal_funds_rate'),
            fetch_indicator('CPIAUCSL', 'inflation_rate'),
            fetch_indicator('GDP', 'gdp_growth'),
            fetch_indicator('UNRATE', 'unemployment_rate')
        ]

        await asyncio.gather(*tasks, return_exceptions=True)

        return {
            'economic_data': results,
            'errors': errors,
            'timestamp': datetime.now().isoformat()
        }
```

**Exa API Integration (`agent/tools/exa_tools.py`):**

```python
from exa_py import Exa
from agno.tools import Tool
import asyncio
from typing import List, Dict

class ExaSearchTools(Tool):
    """Exa neural search integration for portfolio-relevant news"""

    def __init__(self):
        self.exa = Exa(api_key=os.getenv('EXA_API_KEY'))
        super().__init__(
            name="Exa News Search",
            description="Neural search for portfolio-relevant market news"
        )

    async def search_portfolio_news(self, query: str, portfolio_tickers: List[str]) -> Dict:
        """Search for news relevant to portfolio holdings"""
        try:
            # Enhance query with portfolio context
            enhanced_query = f"{query} {' OR '.join(portfolio_tickers)} market analysis"

            async with asyncio.timeout(30):
                results = await asyncio.to_thread(
                    self.exa.search,
                    enhanced_query,
                    num_results=5,
                    include_domains=['bloomberg.com', 'reuters.com', 'wsj.com', 'cnbc.com'],
                    use_autoprompt=True
                )

                processed_results = []
                for result in results.results:
                    processed_results.append({
                        'title': result.title,
                        'url': result.url,
                        'snippet': result.text[:500] if result.text else '',
                        'relevance_score': result.score,
                        'published_date': result.published_date,
                        'portfolio_relevance': self._assess_portfolio_relevance(
                            result.text, portfolio_tickers
                        )
                    })

                return {
                    'news_results': processed_results,
                    'query_used': enhanced_query,
                    'timestamp': datetime.now().isoformat(),
                    'total_results': len(processed_results)
                }

        except asyncio.TimeoutError:
            return {
                'error': 'Exa search timed out',
                'news_results': [],
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'error': f'Exa search failed: {str(e)}',
                'news_results': [],
                'timestamp': datetime.now().isoformat()
            }

    def _assess_portfolio_relevance(self, text: str, tickers: List[str]) -> str:
        """Assess how relevant news is to portfolio holdings"""
        if not text:
            return 'low'

        text_lower = text.lower()
        ticker_mentions = sum(1 for ticker in tickers if ticker.lower() in text_lower)

        if ticker_mentions >= 2:
            return 'high'
        elif ticker_mentions == 1:
            return 'medium'
        else:
            return 'low'
```

#### 3. Enhanced Streaming Architecture

**Optimized Event Streaming (`agent/main.py` enhancements):**

```python
# Enhanced event streaming for Market Analysis
@app.post("/market-analysis-agent")
async def market_analysis_agent(input_data: RunAgentInput):
    async def event_generator():
        encoder = EventEncoder()
        event_queue = asyncio.Queue()

        def emit_event(event):
            event_queue.put_nowait(event)

        # Enhanced progress tracking with multiple event types
        yield encoder.encode(RunStartedEvent(
            type=EventType.RUN_STARTED,
            thread_id=input_data.thread_id,
            run_id=input_data.run_id
        ))

        # Initial state with market analysis structure
        yield encoder.encode(StateSnapshotEvent(
            type=EventType.STATE_SNAPSHOT,
            snapshot={
                "available_cash": input_data.state["available_cash"],
                "investment_portfolio": input_data.state["investment_portfolio"],
                "market_analysis": {
                    "economic_data": None,
                    "news_analysis": None,
                    "portfolio_impact": None,
                    "analysis_status": "starting"
                },
                "tool_logs": []
            }
        ))

        # Run enhanced market analysis workflow
        analysis_task = asyncio.create_task(
            market_analysis_workflow.arun(
                additional_data={
                    "tools": input_data.tools,
                    "messages": input_data.messages,
                    "emit_event": emit_event,
                    "portfolio_holdings": input_data.state["investment_portfolio"],
                    "market_query": input_data.messages[-1].content,
                    "tool_logs": []
                }
            )
        )

        # Stream events with enhanced progress reporting
        while True:
            try:
                event = await asyncio.wait_for(event_queue.get(), timeout=0.1)
                yield encoder.encode(event)
            except asyncio.TimeoutError:
                if analysis_task.done():
                    break

        # Stream final results with multiple response types
        result = analysis_task.result()
        final_message = result.step_responses[-1].content['messages'][-1]

        if final_message.tool_calls:
            # Handle market analysis tool calls
            for tool_call in final_message.tool_calls:
                yield encoder.encode(ToolCallStartEvent(
                    type=EventType.TOOL_CALL_START,
                    tool_call_id=tool_call.id,
                    toolCallName=tool_call.function.name
                ))

                yield encoder.encode(ToolCallArgsEvent(
                    type=EventType.TOOL_CALL_ARGS,
                    tool_call_id=tool_call.id,
                    delta=tool_call.function.arguments
                ))

                yield encoder.encode(ToolCallEndEvent(
                    type=EventType.TOOL_CALL_END,
                    tool_call_id=tool_call.id
                ))

        yield encoder.encode(RunFinishedEvent(
            type=EventType.RUN_FINISHED,
            thread_id=input_data.thread_id,
            run_id=input_data.run_id
        ))

    return StreamingResponse(event_generator(), media_type="text/event-stream")
```

### Frontend Architecture (Enhanced Components)

#### 1. Market Analysis State Management

**Enhanced useCoAgent Integration:**

```typescript
// Extended state interface for market analysis
interface MarketAnalysisState {
  available_cash: number;
  investment_portfolio: PortfolioHolding[];
  market_analysis: {
    economic_data: EconomicData | null;
    news_analysis: NewsAnalysis | null;
    portfolio_impact: PortfolioImpact | null;
    analysis_status: 'idle' | 'analyzing' | 'complete' | 'error';
    query_history: MarketQuery[];
  };
  tool_logs: ToolLog[];
}

// Market analysis types
interface EconomicData {
  federal_funds_rate: EconomicIndicator;
  inflation_rate: EconomicIndicator;
  gdp_growth: EconomicIndicator;
  unemployment_rate: EconomicIndicator;
  data_freshness: string;
  source_citations: SourceCitation[];
}

interface NewsAnalysis {
  relevant_articles: NewsArticle[];
  sentiment_summary: SentimentAnalysis;
  portfolio_relevance: RelevanceScore;
  search_metadata: SearchMetadata;
}

interface PortfolioImpact {
  holdings_impact: HoldingImpact[];
  overall_risk_assessment: RiskLevel;
  recommended_actions: RecommendedAction[];
  confidence_scores: ConfidenceScores;
}
```

#### 2. Market Analysis Components

**Main Market Analysis Panel:**

```typescript
// components/MarketAnalysisPanel.tsx
import { useState, useCallback } from 'react';
import { useCoAgent } from '@copilotkit/react-core';
import { MarketQueryInput } from './MarketQueryInput';
import { AnalysisResults } from './AnalysisResults';
import { AnalysisProgressTracker } from './AnalysisProgressTracker';

export function MarketAnalysisPanel() {
  const { state, setState } = useCoAgent<MarketAnalysisState>();
  const [currentQuery, setCurrentQuery] = useState<string>('');
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);

  const handleQuerySubmit = useCallback(async (query: string) => {
    setIsAnalyzing(true);
    setCurrentQuery(query);

    // Update state to show analysis starting
    setState(prev => ({
      ...prev,
      market_analysis: {
        ...prev.market_analysis,
        analysis_status: 'analyzing'
      }
    }));

    // Query will be handled by CopilotKit streaming
  }, [setState]);

  const handleAbortAnalysis = useCallback(() => {
    setIsAnalyzing(false);
    setState(prev => ({
      ...prev,
      market_analysis: {
        ...prev.market_analysis,
        analysis_status: 'idle'
      }
    }));
  }, [setState]);

  return (
    <div className="market-analysis-panel">
      <div className="analysis-header">
        <h2>Market Analysis</h2>
        <p>Ask questions about market conditions affecting your portfolio</p>
      </div>

      <MarketQueryInput
        onSubmit={handleQuerySubmit}
        isAnalyzing={isAnalyzing}
        portfolioContext={state.investment_portfolio}
      />

      {isAnalyzing && (
        <AnalysisProgressTracker
          toolLogs={state.tool_logs}
          onAbort={handleAbortAnalysis}
          estimatedTimeRemaining={120}
        />
      )}

      <AnalysisResults
        economicData={state.market_analysis.economic_data}
        newsAnalysis={state.market_analysis.news_analysis}
        portfolioImpact={state.market_analysis.portfolio_impact}
        analysisStatus={state.market_analysis.analysis_status}
      />
    </div>
  );
}
```

**Analysis Progress Component:**

```typescript
// components/AnalysisProgressTracker.tsx
interface AnalysisProgressTrackerProps {
  toolLogs: ToolLog[];
  onAbort: () => void;
  estimatedTimeRemaining: number;
}

export function AnalysisProgressTracker({
  toolLogs,
  onAbort,
  estimatedTimeRemaining
}: AnalysisProgressTrackerProps) {
  const completedSteps = toolLogs.filter(log => log.status === 'completed').length;
  const totalSteps = 4; // query_analysis, economic_data, news_analysis, impact_synthesis
  const progressPercent = (completedSteps / totalSteps) * 100;

  return (
    <div className="analysis-progress-tracker">
      <div className="progress-header">
        <h3>Analyzing Market Conditions</h3>
        <button
          onClick={onAbort}
          className="abort-button"
          aria-label="Abort analysis"
        >
          Cancel
        </button>
      </div>

      <div className="progress-bar-container">
        <div
          className="progress-bar"
          style={{ width: `${progressPercent}%` }}
          role="progressbar"
          aria-valuenow={progressPercent}
          aria-valuemin={0}
          aria-valuemax={100}
        />
      </div>

      <div className="progress-steps">
        {toolLogs.map((log, index) => (
          <div
            key={log.id}
            className={`progress-step ${log.status}`}
          >
            <div className="step-indicator">
              {log.status === 'completed' && <CheckIcon />}
              {log.status === 'processing' && <SpinnerIcon />}
              {log.status === 'pending' && <PendingIcon />}
            </div>
            <span className="step-label">{log.message}</span>
          </div>
        ))}
      </div>

      <div className="time-estimate">
        Estimated time remaining: {estimatedTimeRemaining}s
      </div>
    </div>
  );
}
```

#### 3. Enhanced CopilotKit Actions

**Market Analysis Tool Integration:**

```typescript
// Enhanced CopilotKit action for market analysis results
useCopilotAction({
  name: "render_market_analysis",
  description: "Render comprehensive market analysis results",
  parameters: [
    {
      name: "analysis_results",
      type: "object",
      description: "Complete market analysis results",
      properties: {
        economic_data: {
          type: "object",
          description: "FRED economic indicators analysis"
        },
        news_analysis: {
          type: "object",
          description: "Exa news search results and sentiment"
        },
        portfolio_impact: {
          type: "object",
          description: "Portfolio-specific impact analysis"
        }
      }
    }
  ],
  handler: async ({ analysis_results }) => {
    // Update state with comprehensive market analysis
    setState(prev => ({
      ...prev,
      market_analysis: {
        ...prev.market_analysis,
        economic_data: analysis_results.economic_data,
        news_analysis: analysis_results.news_analysis,
        portfolio_impact: analysis_results.portfolio_impact,
        analysis_status: 'complete'
      }
    }));

    // Trigger UI updates for chart rendering
    if (analysis_results.portfolio_impact) {
      renderPortfolioImpactCharts(analysis_results.portfolio_impact);
    }
  }
});
```

## Migration Strategy

### Gradual Migration Approach: Maintaining Stability

**IMPORTANT**: The migration strategy prioritizes stability and zero regression risk. We maintain complete separation between existing v1 code and new v2 implementations.

#### Migration Principles
1. **No Breaking Changes**: Existing stock_analysis.py remains untouched
2. **Isolated Implementation**: New features in separate directories
3. **Shared Infrastructure**: Reuse AG-UI streaming and state management
4. **Incremental Adoption**: Optional migration of old features post-MVP
5. **Risk Mitigation**: Each phase independently deployable and rollbackable

#### Phase 0: Pre-Migration Setup (MVP Approach)
```python
# Keep existing patterns for MVP - add market analysis using v1 style
# agent/market_analysis_mvp.py
async def market_analysis_mvp():
    """MVP implementation matching existing patterns"""
    return Workflow(
        name="Market Analysis Pipeline",
        steps=[
            parse_market_query,    # Function (v1 style)
            gather_market_data,    # Function (v1 style)
            analyze_impact,        # Function (v1 style)
            generate_insights      # Function (v1 style)
        ]
    )
```

## Implementation Examples

### V1 Pattern (Current stock_analysis.py)
```python
# Function-based step definition
async def parse_request(step_input):
    user_query = step_input.get("query")
    # Process query
    return {"parsed": parsed_result}

# Workflow assembly
workflow = Workflow(
    name="Stock Analysis",
    steps=[parse_request, analyze_stocks, generate_insights]
)
```

### V2 Pattern (New market_analysis_v2/)
```python
# Step class with explicit Agent
class MarketAnalysisStep(Step):
    def __init__(self):
        self.agent = Agent(
            name="market_analyst",
            system_prompt="You are a market analysis expert...",
            tools=[fred_tool, exa_tool]
        )

    async def execute(self, context):
        # Step logic with agent
        result = await self.agent.run(context.query)
        return result

# Workflow with Step objects
market_workflow = Workflow(
    name="Market Analysis V2",
    steps=[
        MarketAnalysisStep(),
        DataGatheringStep(),
        InsightGenerationStep()
    ]
)
```

### Router Implementation Detail
```python
# main.py
from agent.stock_analysis import stock_analysis_workflow  # v1
from agent.market_analysis_v2 import market_workflow      # v2

def is_market_query(message: str) -> bool:
    """Detect market analysis queries"""
    market_keywords = [
        "market", "economic", "fed", "inflation",
        "news", "sector", "macro", "indicators"
    ]
    return any(keyword in message.lower() for keyword in market_keywords)

async def handle_v1_workflow(input_data, workflow):
    """Process v1 workflows with function-based steps"""
    # Existing v1 processing logic
    return await process_workflow_v1(workflow, input_data)

async def handle_v2_workflow(input_data, workflow):
    """Process v2 workflows with Step/Agent pattern"""
    # New v2 processing with better error handling
    context = WorkflowContext(
        query=input_data.messages[-1].content,
        state=input_data.state
    )
    return await workflow.run(context)
```

## Testing Strategy

Maintain separate test suites for v1 and v2 implementations:
- `test_stock_analysis.py` for v1 workflows
- `test_market_analysis_v2.py` for v2 workflows
- `test_router.py` for routing logic
- Integration tests covering both patterns

### Test Examples

```python
# test_router.py
import pytest
from agent.main import is_market_query, route_request

class TestWorkflowRouting:
    def test_market_queries_route_to_v2(self):
        queries = [
            "What economic headwinds affect my portfolio?",
            "Show me market indicators",
            "How will fed rates impact tech stocks?"
        ]
        for query in queries:
            assert is_market_query(query) == True

    def test_stock_queries_route_to_v1(self):
        queries = [
            "Buy 100 shares of AAPL",
            "Show my portfolio performance",
            "What's my cash balance?"
        ]
        for query in queries:
            assert is_market_query(query) == False

    async def test_v1_v2_isolation(self):
        # Ensure v1 workflow unaffected by v2 additions
        v1_result = await route_request("Buy AAPL shares")
        assert v1_result.workflow_version == "v1"

        v2_result = await route_request("Analyze market conditions")
        assert v2_result.workflow_version == "v2"
```

## Monitoring & Rollback Plan

### Health Checks
```python
@app.get("/health/workflows")
async def workflow_health():
    return {
        "v1_workflows": {
            "status": "active",
            "last_execution": v1_last_run,
            "error_rate": v1_error_rate
        },
        "v2_workflows": {
            "status": "active",
            "last_execution": v2_last_run,
            "error_rate": v2_error_rate
        }
    }
```

### Feature Toggle
```python
# Environment-based feature flag
USE_V2_FOR_ALL = os.getenv("AGNO_V2_ENABLED", "false") == "true"

if USE_V2_FOR_ALL:
    # Route all requests to v2 (future state)
    workflow_handler = handle_v2_workflow
else:
    # Use hybrid routing (current state)
    workflow_handler = hybrid_router
```

### Phase 1: Backend Foundation (Weeks 1-2)

**1.1 Hybrid Workflow Implementation**
- Migrate from v1 function-based steps to v2 Step objects
- Define specialized Agent instances for each workflow step
- Add SqliteDb integration for session persistence
- Enhance error handling with partial result support

**1.2 API Integration Setup**
- Implement FRED API tools with async timeout handling
- Implement Exa API tools with neural search optimization
- Add comprehensive error recovery for API failures
- Create tool testing suite with mock data

**1.3 Enhanced Streaming**
- Optimize AG-UI event usage for better UX
- Add more granular progress reporting events
- Implement analysis abortion capability
- Enhance state synchronization patterns

### Phase 2: Frontend Enhancement (Weeks 2-3)

**2.1 Component Architecture**
- Create MarketAnalysisPanel with progressive disclosure
- Implement AnalysisProgressTracker with real-time updates
- Build responsive MarketQueryInput with portfolio context
- Create modular AnalysisResults display components

**2.2 State Management Enhancement**
- Extend useCoAgent state for market analysis data
- Implement query history and caching
- Add optimistic UI updates for better responsiveness
- Create proper loading and error states

**2.3 Accessibility & Performance**
- Ensure WCAG 2.1 AA compliance for new components
- Implement proper keyboard navigation
- Optimize streaming performance for large datasets
- Add screen reader support for analysis results

### Phase 3: Integration & Testing (Weeks 3-4)

**3.1 End-to-End Integration**
- Connect all workflow steps with proper event streaming
- Implement comprehensive error scenarios testing
- Validate performance targets (120s analysis completion)
- Test abortion and retry mechanisms

**3.2 User Experience Validation**
- Conduct usability testing with target personas
- Validate source citation workflow
- Test mobile responsive experience
- Gather feedback on analysis quality and relevance

## Performance Considerations

### Backend Optimizations

**1. Parallel API Processing:**
- Execute FRED and Exa API calls concurrently
- Implement circuit breaker pattern for API reliability
- Use connection pooling for multiple API requests
- Add retry logic with exponential backoff

**2. Streaming Efficiency:**
- Minimize event payload sizes
- Use delta updates for large state changes
- Implement event batching for high-frequency updates
- Optimize JSON serialization for SSE events

### Frontend Optimizations

**1. Progressive Loading:**
- Render analysis sections as data arrives
- Implement skeleton loading states
- Use intersection observers for lazy component loading
- Cache analysis results client-side for 15 minutes

**2. State Management:**
- Implement state normalization for complex analysis data
- Use React.memo for expensive component renders
- Add debouncing for query input validation
- Optimize re-render cycles with proper dependency arrays

## Security & Compliance

### API Security
- Store all API keys in environment variables
- Implement API key rotation capabilities
- Add rate limiting protection for external API calls
- Use HTTPS for all external API communications

### Data Privacy
- No persistent storage of sensitive market analysis
- Clear session data after user logout
- Implement proper CORS policies for API endpoints
- Add request/response logging for audit purposes

### Compliance Considerations
- Add prominent "Not investment advice" disclaimers
- Implement clear data source attribution requirements
- Ensure all analysis includes confidence scores
- Document data retention and deletion policies

## Monitoring & Observability

### Backend Monitoring
- Track API response times and failure rates
- Monitor workflow execution times and bottlenecks
- Log all error scenarios with proper context
- Implement health check endpoints for dependencies

### Frontend Monitoring
- Track user interaction patterns with market analysis
- Monitor analysis completion rates and abandonment
- Measure time-to-first-insight and user satisfaction
- Log client-side errors with user context

### Performance Metrics
- Analysis completion time (target: 90-120s)
- First insight delivery (target: <15s)
- API success rates (target: >95%)
- User engagement with source citations (target: 60%+)

## Deployment Architecture

### Development Environment
- Local development with mock API responses
- Hot reload for both frontend and backend changes
- Comprehensive test data sets for all analysis scenarios
- Local SQLite for session management testing

### Production Environment
- Containerized backend deployment with auto-scaling
- CDN integration for frontend static assets
- Database replication for session data persistence
- Monitoring and alerting for all critical dependencies

### CI/CD Pipeline
- Automated testing for both API integrations and UI components
- Performance regression testing for analysis workflows
- Accessibility compliance testing in CI pipeline
- Automated deployment with proper rollback capabilities

## Future Enhancements

### Phase 4+ Roadmap
- **Advanced Analytics**: Technical indicators and momentum analysis
- **Proactive Alerts**: Automated notifications when market conditions change
- **Historical Comparisons**: "What would have happened in 2008?" scenarios
- **Multi-Asset Support**: Bonds, commodities, international markets
- **Collaborative Features**: Shared analysis for investment clubs
- **API Marketplace**: Integration with additional data providers

### Scalability Considerations
- **Microservices Architecture**: Split analysis types into dedicated services
- **Caching Layer**: Redis for frequently accessed market data
- **Queue System**: Background processing for complex analyses
- **Load Balancing**: Distribute analysis workload across multiple instances

---

## Summary

This architecture document provides a comprehensive roadmap for implementing the Market Analysis feature while maintaining compatibility with existing systems and following established best practices. The approach prioritizes:

1. **Incremental Migration** from current v1 Agno patterns to recommended v2 patterns
2. **Robust Error Handling** for external API dependencies
3. **Enhanced User Experience** through optimized streaming and progressive disclosure
4. **Performance Optimization** to meet the 120-second analysis completion target
5. **Future Scalability** through modular architecture and proper abstractions

The implementation follows the project brief's emphasis on transparency, portfolio-contextual analysis, and trust-building through proper source attribution while providing a solid foundation for future enhancements.

**Document Status**: Ready for Implementation
**Version**: 1.0
**Last Updated**: 2025-01-16
**Author**: Claude Code Architecture Analysis