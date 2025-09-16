# Project Brief: Market Analysis Feature

## Executive Summary

The Market Analysis feature transforms your AI-powered stock portfolio application into an autonomous market intelligence platform. Portfolio managers can ask natural language questions about broader market conditions (e.g., "What economic headwinds might affect my tech holdings?") and receive comprehensive, multi-step research analysis. The agent autonomously gathers data from economic indicators, news sentiment, technical analysis, and fundamental metrics, then synthesizes actionable insights with confidence scores. This addresses the critical gap between portfolio tracking and market context understanding, enabling informed investment decisions based on real-time market intelligence rather than isolated stock performance.

## Problem Statement

**Current State & Pain Points:**

Portfolio managers using AI-powered investment tools face a critical information gap between portfolio performance data and market context. Currently, they must:
- **Context Switch Constantly:** Jump between 5-10 different platforms (portfolio tracker, news sites, economic data sources, technical analysis tools) to understand market conditions affecting their holdings
- **Manually Synthesize Information:** Spend 2-3 hours daily correlating market news, economic indicators, and technical signals with their specific portfolio positions
- **React Rather Than Anticipate:** Discover market shifts only after they've impacted portfolio performance, missing opportunities to proactively adjust positions

**Impact of the Problem (Quantified):**
- **Time Cost:** Portfolio managers spend 40% of their research time (~15 hours/week) gathering and correlating market data
- **Opportunity Cost:** Delayed market intelligence leads to 2-3 day lag in portfolio adjustments, potentially costing 1-2% returns during volatile periods
- **Decision Quality:** Without integrated analysis, 30% of trading decisions are made with incomplete market context
- **Scale Limitation:** Individual investors cannot match institutional research capabilities, creating an unfair disadvantage

**Why Existing Solutions Fall Short:**
- **Generic Analysis Tools** (Bloomberg, Reuters): Provide broad market coverage but don't contextualize for specific portfolio holdings
- **Portfolio Trackers** (existing app state): Show performance but lack market intelligence features
- **News Aggregators** (Google Finance, Yahoo): Offer raw information without synthesis or actionable insights
- **Robo-Advisors** (Betterment, Wealthfront): Focus on passive strategies, not active market analysis

**Urgency and Importance:**
Market volatility has increased 40% since 2020, with major shifts driven by Fed policy changes, geopolitical events, and sector rotations happening weekly rather than quarterly. Portfolio managers need real-time, contextual intelligence now more than ever to protect and grow wealth in this environment.

## Proposed Solution

**Core Concept and Approach:**

The Market Analysis feature introduces an **Autonomous Research Agent** that acts as a personal market analyst for each portfolio. When users ask questions like "What market forces are affecting my tech holdings?" or "Should I be concerned about rising interest rates?", the agent:

1. **Decomposes the Query:** Breaks complex questions into research steps (economic data, sector analysis, news sentiment, technical indicators)
2. **Executes Multi-Source Analysis:** Autonomously gathers data from yfinance, FRED API, news sources, and technical analysis engines
3. **Synthesizes Contextually:** Correlates findings specifically to user's portfolio holdings, not generic market commentary
4. **Delivers Actionable Intelligence:** Presents insights with confidence scores, supporting evidence, and specific recommendations

**Key Differentiators from Existing Solutions:**

- **Portfolio-Contextual Analysis:** Every insight directly relates to user's actual holdings, not generic market news
- **Autonomous Multi-Step Research:** Agent performs hours of research in seconds, following the same process a human analyst would
- **Transparent Reasoning:** Shows research steps, data sources, and confidence levels - users see the "why" behind insights
- **Real-Time Integration:** Analysis happens within the portfolio interface, no context switching required
- **Adaptive Intelligence:** Learns from user interactions to improve relevance and accuracy over time

**Why This Solution Will Succeed Where Others Haven't:**

1. **Leverages Existing Architecture:** Built on proven Agno workflow system already handling portfolio analysis successfully
2. **Progressive Complexity:** Starts with economic indicators (reliable, free data) before adding premium sources
3. **Trust Through Transparency:** Unlike black-box recommendations, shows complete research trail
4. **Narrow Initial Focus:** MVP targets portfolio-specific questions, not broad market predictions
5. **Defensive Positioning:** Presents analysis and context, not investment advice, avoiding regulatory issues

**High-Level Vision for the Product:**

Transform the portfolio application from a **reactive tracking tool** into a **proactive intelligence platform** where AI agents continuously monitor market conditions, alert users to relevant changes, and provide on-demand deep analysis. Users should feel like they have a team of analysts working 24/7 to understand how global markets affect their specific investments.

## Target Users

### Primary User Segment: Active Portfolio Managers

**Demographic/Firmographic Profile:**
- **Financial Profile:** Managing portfolios between $100K - $10M
- **Experience Level:** 2+ years active investing experience
- **Age Range:** 28-55, tech-savvy professionals
- **Location:** Global, with focus on US/European markets
- **Investment Style:** Active traders making weekly adjustments, mix of growth and value strategies

**Current Behaviors and Workflows:**
- Spend 2-3 hours daily researching market conditions across Bloomberg, Yahoo Finance, SeekingAlpha
- Monitor 10-30 individual positions plus sector ETFs
- Execute 5-10 trades weekly based on market analysis
- Maintain spreadsheets correlating economic indicators with portfolio performance
- Set price alerts and news notifications across multiple platforms

**Specific Needs and Pain Points:**
- **Information Overload:** Drowning in data from multiple sources without clear synthesis
- **Context Gap:** Generic market news doesn't relate to specific portfolio holdings
- **Time Pressure:** Market moves faster than manual research capabilities
- **Analysis Paralysis:** Too many indicators without clear prioritization
- **FOMO Risk:** Missing opportunities while researching threats

**Goals They're Trying to Achieve:**
- Outperform index benchmarks by 5-10% annually
- Identify market shifts before they impact portfolio
- Reduce research time while improving decision quality
- Build conviction in investment thesis through comprehensive analysis
- Sleep better knowing portfolio risks are monitored 24/7

### Secondary User Segment: Financial Advisors & Wealth Managers

**Demographic/Firmographic Profile:**
- **Professional Role:** RIAs, wealth managers, financial planners
- **Client Base:** Managing 50-200 client portfolios
- **AUM Range:** $10M - $500M under management
- **Firm Size:** Small to mid-size advisory firms (1-20 advisors)

**Current Behaviors and Workflows:**
- Prepare weekly/monthly market commentary for clients
- Justify portfolio decisions with market evidence
- Monitor multiple client portfolios with different risk profiles
- Generate personalized reports explaining market impacts

**Specific Needs and Pain Points:**
- **Scalability Challenge:** Cannot provide deep analysis for every client portfolio
- **Communication Burden:** Explaining complex market dynamics to non-financial clients
- **Compliance Requirements:** Need documented reasoning for investment decisions
- **Client Retention:** Must demonstrate value beyond passive indexing

**Goals They're Trying to Achieve:**
- Provide institutional-quality analysis at boutique firm scale
- Increase client satisfaction through proactive market insights
- Reduce time spent on market research and report generation
- Differentiate service offering from robo-advisors and large firms

## Goals & Success Metrics

### Business Objectives
- **User Engagement:** Increase average session time by 40% within 3 months (baseline: 12 min → target: 17 min)
- **Feature Adoption:** 60% of active users utilize Market Analysis weekly within 6 months
- **Revenue Growth:** Convert 15% of free users to premium tier with advanced analysis features
- **Retention Improvement:** Reduce monthly churn from 8% to 5% for users actively using Market Analysis
- **Platform Stickiness:** Users perform 3+ market analyses per week on average

### User Success Metrics
- **Research Efficiency:** Reduce market research time from 3 hours to 30 minutes per session (6x improvement)
- **Decision Confidence:** 80% of users report increased confidence in trading decisions (via in-app surveys)
- **Portfolio Performance:** Users outperform their benchmark indices by 2-5% annually
- **Information Synthesis:** Successfully correlate 10+ data sources per analysis (vs 3-4 manually)
- **Proactive Insights:** Deliver relevant market alerts 2-3 days before portfolio impact

### Key Performance Indicators (KPIs)
- **Analysis Speed:** Complete comprehensive market analysis in <120 seconds for 90% of queries
- **Data Coverage:** Successfully retrieve data from 3+ sources per analysis request
- **Accuracy Score:** 85%+ correlation between predicted market impacts and actual portfolio changes
- **User Satisfaction (CSAT):** Maintain 4.5+ star rating for Market Analysis feature
- **API Reliability:** 99.5% uptime for all data source integrations
- **Cost Efficiency:** Keep data API costs below $0.20 per analysis query
- **Streaming Performance:** Deliver first insight within 15 seconds of query submission
- **Trust Metrics:** 60% of users click through to view source citations

## MVP Scope

### Core Features (Must Have)

**Natural Language Market Query Interface:** Simple question → comprehensive answer in 90-120 seconds. Focus on economic context questions affecting portfolio.

**Economic Impact Analysis with Clear Data/Interpretation Separation:**
- **Data Section:** Raw numbers from FRED (Fed rate: 5.5%, Inflation: 3.2%, etc.)
- **Interpretation Section:** "Rising rates typically pressure growth stocks. Your tech holdings (45% of portfolio) may face headwinds."
- **Impact Scoring:** Show High/Medium/Low impact per holding with reasoning

**Evidence-Based Insights with Proper Citations:**
- Each insight shows: [DATA] → [ANALYSIS] → [CONCLUSION]
- Clickable source links to FRED, yfinance, Exa results
- Clear attribution: "According to Federal Reserve data from [date]..."
- Transparency builds trust - users see exactly where insights come from

**Relevant Market Context via Exa Neural Search:**
- Find 3-5 most relevant news/analysis pieces using semantic search
- Summarize how each relates to user's specific holdings
- Link to original sources for users who want to dive deeper

**Simple Progress Indication:**
- Clean progress bar with current step: "Analyzing economic data..."
- No complex workflow visualization, just reassurance it's working

### Out of Scope for MVP
- Technical analysis (RSI, moving averages, support/resistance)
- Options flow or institutional positioning
- Social media sentiment
- International markets
- Intraday/real-time analysis
- Custom alerts or saved queries
- Multi-portfolio comparison

### MVP Success Criteria
- Analysis completes in 90-120 seconds for 90% of queries
- Users can trace every insight back to its data source
- 60% of users click through to at least one source (trust indicator)
- Clear separation between facts and interpretation in UI

## Post-MVP Vision

### Phase 2 Features
- Advanced filtering and custom analysis parameters
- Historical analysis comparisons ("How would this portfolio perform in 2008?")
- Proactive alerts when market conditions change significantly
- Sector rotation analysis and recommendations
- Integration with more premium data sources (Alpha Vantage, Polygon)

### Long-term Vision
- Full technical analysis suite (but kept separate from market context)
- Multi-asset class support (bonds, commodities, international)
- AI-powered portfolio optimization suggestions based on market analysis
- Collaborative features for investment clubs/teams
- White-label solution for financial advisors

### Expansion Opportunities
- B2B offering for RIAs and wealth management firms
- API access for developers to build on top of analysis engine
- Educational content generation based on market analysis
- Integration with broker APIs for automated rebalancing

## Technical Considerations

### Platform Requirements
- **Target Platforms:** Web (primary), responsive mobile web
- **Browser/OS Support:** Chrome, Safari, Firefox (latest 2 versions)
- **Performance Requirements:** First insight within 15 seconds, complete analysis under 120 seconds

### Technology Preferences
- **Frontend:** Next.js 15 (existing), CopilotKit (existing), AG-UI for streaming
- **Backend:** FastAPI with Agno workflows, AG-UI EventEncoder for SSE
- **Database:** PostgreSQL for user data, Redis for caching API responses
- **Hosting/Infrastructure:** Vercel (frontend), AWS/Railway (backend)

### Architecture Considerations
- **Repository Structure:** Monorepo with frontend/ and agent/ directories
- **Service Architecture:** Microservices pattern with separate analysis workers
- **Integration Requirements:** FRED API, Exa API, yfinance, OpenAI
- **Security/Compliance:** No financial advice, clear disclaimers, secure API key management

## Constraints & Assumptions

### Constraints
- **Budget:** $500-1000/month for API costs during MVP
- **Timeline:** 8 weeks to MVP launch
- **Resources:** 1-2 developers, 1 product owner
- **Technical:** API rate limits (FRED: 120 req/min, Exa: varies by plan)

### Key Assumptions
- Users trust AI analysis when sources are transparent
- 90-120 second wait time acceptable for comprehensive analysis
- Economic indicators provide sufficient value without technical analysis
- Exa's neural search will find more relevant content than keyword-based APIs

## Risks & Open Questions

### Key Risks
- **API Reliability:** FRED or Exa downtime could break entire feature
- **Cost Overruns:** Exa API costs could exceed budget with high usage
- **Trust Gap:** Users might not trust AI interpretation despite citations
- **Regulatory:** Unclear line between market analysis and investment advice

### Open Questions
- What's the optimal Exa query strategy for portfolio-specific news?
- Should we cache analyses or always run fresh?
- How do we handle conflicting information from different sources?

### Areas Needing Further Research
- Exa API pricing tiers and rate limits
- FRED API data availability and update frequencies
- Optimal LLM prompting for market analysis synthesis

## Appendices

### A. Research Summary

**Technical Validation Completed:**
- Agno framework supports multi-step workflows with streaming events
- AG-UI EventEncoder handles SSE protocol for real-time updates
- FRED API provides reliable economic data with reasonable rate limits
- Exa neural search offers superior relevance for portfolio-specific queries

**Competitive Landscape Analysis:**
- Bloomberg Terminal: $24,000/year, institutional focus, overwhelming for individual investors
- Yahoo Finance Plus: $35/month, basic screening, no portfolio context
- Seeking Alpha Premium: $240/year, focused on stock picks, not market analysis
- Our Differentiator: Portfolio-contextual analysis with transparent reasoning at accessible price

### B. Stakeholder Input

_(To be populated during stakeholder review sessions)_

### C. References

- [Agno Documentation](https://docs.agno.com) - Workflow orchestration framework
- [AG-UI Protocol Specification](https://docs.ag-ui.com) - Event streaming protocol
- [FRED API Documentation](https://fred.stlouisfed.org/docs/api/) - Federal Reserve economic data
- [Exa API](https://docs.exa.ai) - Neural search for relevant content
- [yfinance Documentation](https://github.com/ranaroussi/yfinance) - Yahoo Finance market data

## Next Steps

### Immediate Actions
1. Create GitHub issue for Market Analysis feature epic
2. Set up development environment with Agno and AG-UI
3. Obtain API keys for FRED and Exa
4. Create UI mockups for market analysis interface
5. Define specific Agno workflow steps
6. Implement basic FRED integration prototype
7. Test Exa search relevance for portfolio queries

### PM Handoff

This Project Brief provides the full context for the Market Analysis feature. The feature addresses a critical gap in portfolio management by providing autonomous, transparent market intelligence that contextualizes economic and news data specifically for each user's holdings.

Key success factors:
- Trust through transparency (clear data/interpretation separation)
- Realistic performance targets (90-120 seconds)
- Focused MVP scope (economic indicators + news, no technical analysis)
- Proven technical stack (Agno + AG-UI + existing architecture)

Please proceed with PRD generation, focusing on detailed user stories, API specifications, and UI/UX requirements that align with this brief's vision while maintaining the pragmatic scope constraints.

---

*Document created: 2025-01-16*
*Author: Mary (Business Analyst)*
*Status: Ready for PM Review*