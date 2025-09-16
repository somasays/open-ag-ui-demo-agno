# Market Analysis Feature Brownfield Enhancement PRD

## Intro Project Analysis and Context

### Existing Project Overview

#### Analysis Source
- Market Analysis Project Brief available at: `/docs/market-analysis-brief.md`
- UI/UX Specification available at: `/docs/front-end-spec.md`
- IDE-based analysis of current codebase (agent/ and frontend/ directories)

#### Current Project State
The project is an AI-powered stock portfolio analysis application using a decoupled architecture:
- **Frontend**: Next.js 15 with TypeScript, CopilotKit for AI chat integration
- **Backend**: FastAPI Python agent using Agno framework for workflow orchestration
- **Current Capabilities**: Portfolio tracking, stock investment analysis, bull/bear insights generation
- **Communication**: HTTP streaming via AG-UI protocol for real-time agent responses

### Available Documentation Analysis

#### Available Documentation
- [x] Tech Stack Documentation (CLAUDE.md)
- [x] Source Tree/Architecture (analyzed from codebase)
- [x] API Documentation (CopilotKit and AG-UI integration documented)
- [x] UX/UI Guidelines (front-end-spec.md)
- [x] Project Brief (market-analysis-brief.md)
- [ ] Technical Debt Documentation
- [ ] Coding Standards (partial in CLAUDE.md)

### Enhancement Scope Definition

#### Enhancement Type
- [x] New Feature Addition
- [x] Integration with New Systems (FRED API, Exa API)
- [ ] Major Feature Modification
- [ ] Performance/Scalability Improvements
- [ ] UI/UX Overhaul
- [ ] Technology Stack Upgrade
- [ ] Bug Fix and Stability Improvements

#### Enhancement Description
Adding autonomous Market Analysis capability that allows users to ask natural language questions about market conditions affecting their portfolio. The agent will gather economic data from FRED, relevant news from Exa, synthesize insights, and present portfolio-specific impacts with transparent source citations.

#### Impact Assessment
- [x] New backend workflows required
- [x] New UI components required
- [ ] Database schema changes
- [x] New external API integrations
- [x] Changes to existing user flows (adds new tab)
- [ ] Performance impact on existing features
- [x] New dependencies to manage

## System Context

### Current Architecture Summary

#### Tech Stack
- **Frontend**: Next.js 15.0.0, React 19, TypeScript, TailwindCSS
- **Backend**: FastAPI, Python 3.x, Agno framework
- **State Management**: CopilotKit useCoAgent
- **Streaming**: AG-UI EventEncoder with SSE
- **Data Sources**: yfinance (existing), FRED API (new), Exa API (new)

#### Key Integration Points
1. **Agent Workflows**: New `market_analysis.py` workflow following existing `stock_analysis.py` pattern
2. **Frontend Actions**: New CopilotKit action `render_market_analysis`
3. **Streaming Events**: Reuse existing StateDeltaEvent, ToolCallEvent patterns
4. **UI Components**: New MarketAnalysisPanel integrated via tab navigation

### Technical Constraints

#### Existing System Constraints
- Must maintain compatibility with existing Agno workflow system
- Cannot break current portfolio analysis features
- Must use existing AG-UI streaming infrastructure
- Frontend must integrate with current CopilotKit setup

#### MVP Simplifications (No Over-Engineering)
- **NO caching layer** - Direct API calls acceptable for MVP load
- **NO uptime SLAs** - Best effort availability
- **NO performance monitoring** - Manual testing sufficient
- **NO rate limiting strategies** - Basic API usage
- **Simple implementations preferred** over complex optimizations

#### Essential Reliability Features (MVP Must-Haves)
- **Error Recovery**: Graceful handling of API failures with clear user feedback
- **Partial Results**: Show successful data even if some APIs fail
- **Timeout Handling**: 120-second maximum wait with ability to abort
- **Retry Logic**: Simple exponential backoff for transient failures
- **Clear Error Messages**: Users understand what failed and why

## Functional Requirements

### User Stories

#### Story 1: Natural Language Market Query
**As a** portfolio manager
**I want to** ask questions about market conditions in natural language
**So that** I can understand economic and news context affecting my holdings

**Acceptance Criteria:**
- Query interface accepts natural language questions
- System identifies relevant economic indicators to fetch
- Analysis completes within 90-120 seconds
- Results show clear data/interpretation separation
- Each insight links to its source

#### Story 2: Economic Impact Analysis
**As a** portfolio manager
**I want to** see how economic indicators affect my specific holdings
**So that** I can make informed decisions based on macro trends

**Acceptance Criteria:**
- FRED data displayed with timestamp and attribution
- Impact scoring (High/Medium/Low) for each holding
- Clear explanation of why each holding is affected
- Fallback to cached/stale data if FRED unavailable

#### Story 3: Relevant News Context
**As a** portfolio manager
**I want to** see news specifically relevant to my portfolio
**So that** I can understand market sentiment and events

**Acceptance Criteria:**
- Exa returns 3-5 relevant articles per query
- News summaries explain relevance to holdings
- Direct links to original articles
- Graceful handling if Exa API fails

### Feature Breakdown

#### Core MVP Features
1. **Market Query Interface**
   - Natural language input
   - Query history (session only, no persistence)
   - Abort capability during analysis

2. **Economic Data Integration (FRED)**
   - Federal funds rate
   - CPI/Inflation data
   - GDP growth rate
   - Unemployment rate
   - Simple retry on failure

3. **News Integration (Exa)**
   - Neural search for portfolio-relevant content
   - 3-5 article summaries
   - Source attribution
   - Fallback to "News unavailable" message

4. **Portfolio Impact Analysis**
   - Calculate impact per holding
   - Show reasoning for each impact score
   - Visual heat map in UI

5. **Source Citations**
   - Every insight shows data source
   - Clickable links to original content
   - Timestamp for data freshness

#### Explicitly Out of Scope for MVP
- Technical analysis (RSI, MACD, etc.)
- Real-time/intraday data
- Custom alerts or notifications
- Saved queries or analysis history
- Multi-portfolio comparison
- International markets
- Caching layer
- Performance monitoring
- Complex rate limiting

### API Specifications

#### FRED API Integration
```python
# Simple direct integration
from fredapi import Fred

fred = Fred(api_key=os.getenv('FRED_API_KEY'))

# Basic data fetch with error handling
def get_economic_data():
    try:
        data = {
            'fed_rate': fred.get_series('DFF', limit=1),
            'inflation': fred.get_series('CPIAUCSL', limit=12),
            'gdp': fred.get_series('GDP', limit=4),
            'unemployment': fred.get_series('UNRATE', limit=1)
        }
        return data
    except Exception as e:
        # Return partial data or None
        return {'error': str(e)}
```

#### Exa API Integration
```python
# Neural search for relevant content
from exa_py import Exa

exa = Exa(api_key=os.getenv('EXA_API_KEY'))

def search_relevant_news(query, holdings):
    try:
        # Enhance query with portfolio context
        enhanced_query = f"{query} {' '.join(holdings)}"
        results = exa.search(enhanced_query, num_results=5)
        return results
    except Exception as e:
        return {'error': str(e)}
```

### Data Flow

1. User enters market query
2. Frontend sends to `/api/copilotkit` route
3. Backend agent:
   - Parses query to identify data needs
   - Fetches FRED data (with timeout)
   - Searches Exa for news (with timeout)
   - Analyzes impact on portfolio
   - Streams results via SSE
4. Frontend renders progressively as data arrives
5. User can click citations for sources

## UI/UX Requirements

### Reference Documentation
Full UI/UX specification available at `/docs/front-end-spec.md`

### Key UI Components (MVP)
1. **Tab Navigation**: Market Analysis as peer to Portfolio tab
2. **Query Input**: Natural language with abort button
3. **Progress Indicator**: Simple progress bar with current step
4. **Results Display**:
   - Economic data card
   - News summaries card
   - Portfolio impact matrix
5. **Error States**: Clear messages for failures

### Accessibility Requirements
- WCAG 2.1 AA compliance
- Keyboard navigation support
- Screen reader compatibility
- Clear error messages
- Sufficient color contrast

## Technical Requirements

### Performance Requirements (Relaxed for MVP)
- **Analysis Completion**: 90-120 seconds acceptable
- **First Insight**: Within 15 seconds preferred
- **Page Load**: Under 3 seconds
- **No formal SLAs or monitoring**

### Error Handling Requirements (Critical for MVP)

#### API Failure Handling
```python
async def gather_market_data(step_input):
    results = {
        'economic_data': None,
        'news_data': None,
        'errors': []
    }

    # Try FRED with timeout
    try:
        async with timeout(30):
            results['economic_data'] = await fetch_fred_data()
    except TimeoutError:
        results['errors'].append('Economic data timed out')
    except Exception as e:
        results['errors'].append(f'Economic data failed: {str(e)}')

    # Try Exa independently
    try:
        async with timeout(30):
            results['news_data'] = await fetch_exa_news()
    except TimeoutError:
        results['errors'].append('News search timed out')
    except Exception as e:
        results['errors'].append(f'News search failed: {str(e)}')

    # Always return something
    return results
```

#### User-Facing Error Messages
- "Economic data temporarily unavailable. Showing news analysis only."
- "News search failed. Showing economic analysis only."
- "Analysis taking longer than expected. You can abort or continue waiting."
- "Unable to complete analysis. Please try again."

### Security Requirements
- API keys stored in environment variables
- No storage of sensitive market data
- Clear disclaimers: "Not investment advice"
- No user data persistence in MVP

### Integration Requirements
1. **Backend**: Extend `agent/main.py` router
2. **Frontend**: Add new CopilotKit action
3. **Streaming**: Use existing EventEncoder
4. **State**: Extend useCoAgent state

## Development Plan

### Phase 1: Backend Foundation (Week 1-2)
1. Set up FRED and Exa API clients
2. Create `market_analysis.py` workflow
3. Implement error handling
4. Test with mock data

### Phase 2: Frontend Integration (Week 2-3)
1. Add Market Analysis tab
2. Create query interface
3. Implement streaming display
4. Add error states

### Phase 3: Integration Testing (Week 4)
1. End-to-end testing
2. Error scenario testing
3. Performance validation
4. User feedback incorporation

### Dependencies
- FRED API key (free, obtain immediately)
- Exa API key (coordinate with team for plan)
- No other blocking dependencies

## Success Metrics (MVP)

### Functional Success
- [x] Users can ask market questions and get answers
- [x] Analysis completes in under 2 minutes
- [x] Sources are clearly cited
- [x] Errors are handled gracefully

### User Success (Post-Launch)
- 50% of users try Market Analysis in first week
- 60% click through to source citations
- User feedback indicates trust in analysis
- No critical bugs blocking usage

## Risk Mitigation

### Technical Risks
1. **API Reliability**
   - Mitigation: Independent API calls, partial results

2. **Performance Issues**
   - Mitigation: 120-second timeout, abort capability

3. **Data Quality**
   - Mitigation: Clear source attribution, data/interpretation separation

### User Risks
1. **Trust in AI Analysis**
   - Mitigation: Transparent sources, confidence scores

2. **Misinterpretation as Advice**
   - Mitigation: Clear disclaimers, educational framing

## Open Questions

1. What's the optimal Exa query strategy for portfolio relevance?
2. Should we show stale FRED data with timestamps or hide it?
3. How to handle conflicting signals from different sources?

## Appendices

### A. API Documentation Links
- [FRED API Documentation](https://fred.stlouisfed.org/docs/api/)
- [Exa API Documentation](https://docs.exa.ai)

### B. Related Documents
- Market Analysis Project Brief: `/docs/market-analysis-brief.md`
- UI/UX Specification: `/docs/front-end-spec.md`
- Architecture Notes: `/CLAUDE.md`

### C. Example Queries for Testing
1. "How will Fed rate changes impact my tech stocks?"
2. "What economic headwinds affect my portfolio?"
3. "Is there sector rotation affecting my holdings?"
4. "What's the market sentiment around my largest positions?"

---

**Document Status**: Ready for Review
**Version**: 1.0 MVP
**Last Updated**: 2025-01-16
**Author**: John (PM)