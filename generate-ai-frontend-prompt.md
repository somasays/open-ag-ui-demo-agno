# AI Frontend Generation Prompt: Market Analysis UI with Hybrid Approach

## Project Context

You are building a Market Analysis feature for an AI-powered stock portfolio application. The application uses a decoupled architecture with Next.js 15 frontend and FastAPI backend, connected via CopilotKit and AG-UI protocol for real-time streaming.

## Current Architecture Overview

### Frontend Stack
- **Framework**: Next.js 15 with TypeScript, Turbopack dev server
- **UI Library**: Tailwind CSS v4, Lucide React icons, Recharts for visualization
- **AI Integration**: CopilotKit v1.9.2 for agent communication
- **State Management**: useCoAgent for agent state, useState for local UI state
- **Streaming**: AG-UI protocol via Server-Sent Events (SSE)

### Backend Integration
- **Agent Framework**: Agno workflow system with Python FastAPI
- **Communication**: HttpAgent via `/api/copilotkit/route.ts`
- **Event Types**: StateDeltaEvent, TextMessageContentEvent, ToolCallEvent
- **Data Sources**: yfinance, FRED API, Exa neural search (planned)

### Existing Components
- **Layout**: 3-panel layout (left prompt panel, center canvas, optional right tree)
- **Charts**: LineChartComponent, BarChartComponent, AllocationTableComponent
- **Cards**: InsightCardComponent for bull/bear analysis
- **Panels**: PromptPanel (chat), CashPanel (portfolio summary), GenerativeCanvas (main display)

## Market Analysis Feature Requirements

### Core Functionality
The Market Analysis feature introduces an **Autonomous Research Agent** that:

1. **Accepts Natural Language Queries**: Users ask questions like "What economic headwinds might affect my tech holdings?"
2. **Executes Multi-Step Analysis**: Autonomously gathers economic data, news sentiment, and technical indicators
3. **Provides Contextual Insights**: Correlates findings specifically to user's portfolio holdings
4. **Delivers Transparent Results**: Shows research steps, data sources, and confidence levels

### Key User Flows
1. **Query Input**: User types market analysis question in chat interface
2. **Progress Indication**: Clean progress bar shows current analysis step
3. **Real-time Streaming**: Results stream in via SSE as agent completes each step
4. **Interactive Display**: Users can explore data sources and drill into insights
5. **Portfolio Integration**: Insights directly relate to user's current holdings

### UI Design Requirements

#### 1. Hybrid Approach: Tabs + Insights Panel

**Main Interface Layout:**
```
┌─────────────────────────────────────────────────────────────────┐
│  Market Analysis Results                                        │
│  ┌─── Tabs ───┐                                                │
│  │ Overview │ Economic │ News │ Technical │                     │
│  └─────────────────────────────────────────┘                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                                                             ││
│  │               Tab Content Area                              ││
│  │                                                             ││
│  │                                                             ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  ┌── Insights Panel ──┐                                        │
│  │ Bull/Bear Analysis │                                        │
│  │ ┌─Bull─┐ ┌─Bear─┐  │                                        │
│  │ │ 🐂   │ │ 🐻   │  │                                        │
│  │ │ ...  │ │ ...  │  │                                        │
│  │ └─────┘ └─────┘  │                                        │
│  └───────────────────┘                                        │
└─────────────────────────────────────────────────────────────────┘
```

#### 2. Tab-Specific Content Requirements

**Overview Tab:**
- High-level market summary
- Key economic indicators dashboard
- Portfolio impact heat map
- Quick action recommendations

**Economic Tab:**
- FRED data visualizations (interest rates, inflation, GDP)
- Economic indicator trends with portfolio correlation
- Clear data/interpretation separation
- Clickable source citations

**News Tab:**
- Exa neural search results
- News sentiment analysis
- Portfolio-relevant article summaries
- Source links to original content

**Technical Tab (Future):**
- Chart patterns and technical indicators
- Support/resistance levels
- Volume analysis
- Technical recommendations

#### 3. Insights Panel Requirements

**Design Specifications:**
- Fixed height panel below main content (not floating)
- Two-column layout: Bull insights (left) | Bear insights (right)
- Reuse existing InsightCardComponent design
- Green accent (#00d237) for bull, red accent for bear
- Expandable cards for detailed analysis

**Content Structure:**
- Title with emoji indicator
- Summary description
- Supporting evidence with citations
- Confidence score (High/Medium/Low)
- Portfolio impact assessment

#### 4. Progress & Streaming UI

**Progress Indicator:**
- Clean, minimal progress bar in main content area
- Current step display: "Analyzing economic data..." | "Searching relevant news..." | "Generating insights..."
- No complex workflow visualization, just reassurance
- Estimated time remaining (90-120 seconds target)

**Streaming Behavior:**
- Content appears progressively as agent completes steps
- Tabs become active as data becomes available
- Insights stream into panel in real-time
- Loading states for individual components

#### 5. Data Transparency & Citations

**Source Attribution:**
- Every data point shows clear source: "According to Federal Reserve data from [date]..."
- Clickable links to FRED, Exa results, yfinance data
- Evidence chain: [DATA] → [ANALYSIS] → [CONCLUSION]
- Trust indicators: 60% of users should click through to sources

**Data vs. Interpretation Separation:**
- Raw data in dedicated sections with clear labels
- Interpretation and analysis clearly marked as such
- Confidence indicators for AI-generated insights
- User can distinguish facts from opinions

## Technical Implementation Details

### Component Architecture

**New Components to Create:**

1. **MarketAnalysisContainer** (Main wrapper)
   - Manages overall state and tab navigation
   - Handles streaming updates from agent
   - Coordinates between tabs and insights panel

2. **MarketAnalysisTabs** (Tab navigation)
   - Tab switching logic
   - Active state management
   - Content lazy loading

3. **Tab Content Components:**
   - **OverviewTab**: High-level dashboard
   - **EconomicTab**: FRED data visualization
   - **NewsTab**: Exa search results
   - **TechnicalTab**: Placeholder for future

4. **MarketInsightsPanel** (Bottom insights panel)
   - Reuses existing InsightCardComponent
   - Bull/bear layout management
   - Streaming insight updates

5. **DataSourceCitation** (Source linking)
   - Clickable source indicators
   - Modal/tooltip for source details
   - Trust-building transparency

6. **MarketProgressIndicator** (Custom progress UI)
   - Step-by-step progress display
   - Time estimation
   - Clean, minimal design

### State Management

**Agent State Extensions:**
```typescript
interface MarketAnalysisState {
  query: string
  progress: {
    step: string
    percentage: number
    estimatedTimeRemaining: number
  }
  economicData: {
    indicators: EconomicIndicator[]
    sources: DataSource[]
  }
  newsAnalysis: {
    articles: NewsArticle[]
    sentiment: SentimentAnalysis
  }
  portfolioImpact: {
    holdings: HoldingImpact[]
    overallRisk: RiskLevel
  }
  bullInsights: Insight[]
  bearInsights: Insight[]
}
```

**Local UI State:**
```typescript
interface MarketAnalysisUIState {
  activeTab: 'overview' | 'economic' | 'news' | 'technical'
  expandedInsights: string[]
  showSourceModal: boolean
  selectedSource?: DataSource
}
```

### CopilotKit Integration

**New CopilotAction for Market Analysis:**
```typescript
useCopilotAction({
  name: "render_market_analysis",
  description: "Renders comprehensive market analysis with tabs and insights",
  renderAndWaitForResponse: ({ args, respond, status }) => {
    // Handle streaming market analysis results
    // Update tabs with new data
    // Stream insights to panel
    // Show progress updates
  }
})
```

**Streaming Event Handling:**
- **StateDeltaEvent**: Update analysis progress and data
- **TextMessageContentEvent**: Stream narrative insights
- **ToolCallEvent**: Trigger tab updates and insight rendering

### Styling Requirements

**Design System Alignment:**
- Follow existing color palette:
  - Background: `#FAFCFA`
  - Borders: `#D8D8E5`
  - Text: `#575758`, `#030507`
  - Accent: `#1B606F` (teal), `#3B82F6` (blue)
- Typography: Roobert for headings, Plus Jakarta Sans for body
- Border radius: `rounded-xl` for cards, `rounded-md` for smaller elements
- Spacing: Consistent 4px grid system

**Tab Styling:**
```css
/* Active tab */
.tab-active {
  @apply bg-white border-b-2 border-blue-500 text-blue-600;
}

/* Inactive tab */
.tab-inactive {
  @apply bg-gray-50 text-gray-600 hover:bg-gray-100;
}

/* Tab content area */
.tab-content {
  @apply bg-white border border-[#D8D8E5] rounded-xl p-4 min-h-[400px];
}
```

**Insights Panel Styling:**
```css
.insights-panel {
  @apply mt-6 bg-white border border-[#D8D8E5] rounded-xl p-4;
  @apply grid grid-cols-2 gap-4;
  @apply max-h-[300px] overflow-y-auto;
}
```

### Performance Considerations

**Optimization Requirements:**
- Lazy load tab content to improve initial render
- Implement virtual scrolling for large insight lists
- Cache FRED/Exa API responses to avoid duplicate requests
- Use React.memo for insight cards to prevent unnecessary re-renders
- Debounce user interactions (tab switching, expansion)

**Loading States:**
- Skeleton loaders for tab content while streaming
- Progressive enhancement as data arrives
- Graceful fallbacks for API failures
- Clear error states with retry options

### Integration Points

**Agent Communication:**
- Market analysis requests via CopilotKit chat interface
- Progress updates via AG-UI StateDeltaEvent
- Result streaming via ToolCallEvent for `render_market_analysis`
- Error handling for API timeouts and failures

**Existing Component Integration:**
- Reuse LineChartComponent for economic data visualization
- Leverage InsightCardComponent for bull/bear insights
- Integrate with existing PromptPanel for query input
- Maintain consistency with GenerativeCanvas layout patterns

## Success Criteria

### User Experience Targets
- **Analysis Speed**: Complete analysis in 90-120 seconds for 90% of queries
- **Trust Indicators**: 60% of users click through to at least one data source
- **Usability**: Clear separation between facts and interpretation in UI
- **Engagement**: Users actively explore tabs and expand insights

### Technical Performance
- **First Insight**: Deliver within 15 seconds of query submission
- **Streaming Smoothness**: No blocking during progressive content updates
- **Error Recovery**: Graceful handling of API failures with clear messaging
- **Mobile Responsiveness**: Tabs and panels adapt to smaller screens

### Business Impact
- **Session Duration**: Increase average session time by 40%
- **Feature Adoption**: 60% of active users utilize Market Analysis weekly
- **User Satisfaction**: Maintain 4.5+ star rating for feature

## Implementation Priority

### Phase 1: MVP Core Components
1. MarketAnalysisContainer with basic tab structure
2. OverviewTab with high-level dashboard
3. EconomicTab with FRED data integration
4. MarketInsightsPanel with streaming bull/bear insights
5. Basic progress indicator and source citations

### Phase 2: Enhanced Experience
1. NewsTab with Exa integration
2. Advanced filtering and search within tabs
3. Interactive source exploration
4. Performance optimizations and caching

### Phase 3: Advanced Features
1. TechnicalTab with chart analysis
2. Custom alert configuration
3. Historical analysis comparisons
4. Export and sharing capabilities

## Code Examples

### MarketAnalysisContainer Structure
```typescript
export function MarketAnalysisContainer({ query, portfolioState }: MarketAnalysisProps) {
  const [activeTab, setActiveTab] = useState<TabType>('overview')
  const [analysisState, setAnalysisState] = useState<MarketAnalysisState>(initialState)

  // Handle streaming updates from agent
  const handleAnalysisUpdate = useCallback((update: MarketAnalysisUpdate) => {
    setAnalysisState(prev => ({
      ...prev,
      ...update
    }))
  }, [])

  return (
    <div className="market-analysis-container">
      <MarketProgressIndicator
        step={analysisState.progress.step}
        percentage={analysisState.progress.percentage}
      />

      <MarketAnalysisTabs
        activeTab={activeTab}
        onTabChange={setActiveTab}
        dataAvailable={getAvailableTabs(analysisState)}
      />

      <TabContent
        activeTab={activeTab}
        analysisState={analysisState}
        portfolioState={portfolioState}
      />

      <MarketInsightsPanel
        bullInsights={analysisState.bullInsights}
        bearInsights={analysisState.bearInsights}
      />
    </div>
  )
}
```

### Economic Data Visualization Example
```typescript
export function EconomicTab({ economicData, portfolioState }: EconomicTabProps) {
  return (
    <div className="economic-tab space-y-6">
      <div className="grid grid-cols-2 gap-4">
        <EconomicIndicatorCard
          title="Federal Funds Rate"
          value={economicData.federalFundsRate}
          trend={economicData.federalFundsRateTrend}
          source="Federal Reserve (FRED)"
          portfolioImpact="Medium"
        />
        <EconomicIndicatorCard
          title="Consumer Price Index"
          value={economicData.cpi}
          trend={economicData.cpiTrend}
          source="Bureau of Labor Statistics"
          portfolioImpact="High"
        />
      </div>

      <div className="mt-6">
        <SectionTitle title="Economic Trends vs Portfolio Performance" />
        <LineChartComponent
          data={economicData.correlationData}
          size="normal"
        />
      </div>

      <DataSourceCitations sources={economicData.sources} />
    </div>
  )
}
```

This comprehensive prompt provides all the context, requirements, and implementation guidance needed to generate a high-quality Market Analysis UI that integrates seamlessly with the existing AI portfolio application while delivering the hybrid tabs + insights panel approach.