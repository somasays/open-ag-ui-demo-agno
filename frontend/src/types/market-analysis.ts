// Market Analysis TypeScript Interfaces
// These types define the structure for market analysis data coming from the backend

// Economic indicator data structure (from FRED API)
export interface EconomicIndicator {
  value: number;
  change: number;  // Change from previous period
  date: string;    // ISO date string
  trend: 'up' | 'down' | 'stable';
  confidence: number; // 0-1 confidence score
}

// Economic data aggregated from FRED
export interface EconomicData {
  federal_funds_rate: EconomicIndicator;
  inflation_rate: EconomicIndicator;
  gdp_growth: EconomicIndicator;
  unemployment_rate: EconomicIndicator;
  data_freshness: string;  // ISO timestamp
  source_citations: SourceCitation[];
}

// Source citation for transparency
export interface SourceCitation {
  source: string;    // "FRED", "Exa", etc.
  url: string;       // Direct link to source
  description: string; // Brief description
  accessed_at: string; // ISO timestamp
}

// News article from Exa API
export interface NewsArticle {
  title: string;
  source: string;    // Publisher name
  url: string;       // Article URL
  snippet: string;   // Article summary/excerpt
  relevance_score: number; // 0-1 relevance to portfolio
  published_date: string;  // ISO date string
  portfolio_tickers: string[]; // Which holdings this affects
  sentiment: 'positive' | 'negative' | 'neutral';
}

// News analysis results
export interface NewsAnalysis {
  articles: NewsArticle[];
  sentiment_summary: SentimentAnalysis;
  portfolio_relevance: RelevanceScore;
  search_metadata: SearchMetadata;
}

// Sentiment analysis breakdown
export interface SentimentAnalysis {
  positive: number;  // Percentage
  neutral: number;   // Percentage
  negative: number;  // Percentage
  overall_tone: 'bullish' | 'bearish' | 'neutral';
}

// Portfolio relevance scoring
export interface RelevanceScore {
  high: number;      // Number of high-relevance articles
  medium: number;    // Number of medium-relevance articles
  low: number;       // Number of low-relevance articles
  coverage_score: number; // 0-1 how well portfolio is covered
}

// Search metadata for debugging
export interface SearchMetadata {
  query_used: string;
  total_results: number;
  search_time_ms: number;
  filters_applied: string[];
}

// Impact assessment for individual holdings
export interface HoldingImpact {
  ticker: string;
  impact_level: 'high' | 'medium' | 'low';
  impact_score: number;  // 0-1 numerical score
  reasoning: string;     // Explanation for the impact
  recommended_action: 'buy' | 'sell' | 'hold' | 'watch';
  confidence: number;    // 0-1 confidence in assessment
  factors: string[];     // List of contributing factors
}

// Overall portfolio impact analysis
export interface PortfolioImpact {
  holdings_impact: HoldingImpact[];
  overall_risk_assessment: RiskLevel;
  recommended_actions: RecommendedAction[];
  confidence_scores: ConfidenceScores;
  market_outlook: MarketOutlook;
}

// Risk assessment levels
export interface RiskLevel {
  level: 'low' | 'medium' | 'high' | 'critical';
  score: number;         // 0-1 numerical risk score
  description: string;   // Human-readable explanation
  time_horizon: string;  // "short-term", "medium-term", "long-term"
}

// Recommended actions for portfolio
export interface RecommendedAction {
  action_type: 'rebalance' | 'hedge' | 'monitor' | 'research';
  priority: 'urgent' | 'important' | 'normal' | 'low';
  description: string;
  affected_tickers: string[];
  estimated_impact: string;
}

// Confidence scores for various aspects
export interface ConfidenceScores {
  economic_analysis: number;   // 0-1
  news_sentiment: number;      // 0-1
  portfolio_impact: number;    // 0-1
  overall_assessment: number;  // 0-1
}

// Market outlook summary
export interface MarketOutlook {
  short_term: 'bullish' | 'bearish' | 'neutral';  // Next 3 months
  medium_term: 'bullish' | 'bearish' | 'neutral'; // Next 12 months
  key_drivers: string[];       // Main factors influencing outlook
  major_risks: string[];       // Key risks to watch
}

// Query history for session management
export interface MarketQuery {
  id: string;
  query: string;
  timestamp: string;          // ISO timestamp
  analysis_status: 'pending' | 'processing' | 'completed' | 'failed';
  response_time_ms?: number;  // How long analysis took
  portfolio_context: string[]; // Tickers in portfolio at query time
}

// Main market analysis state structure
export interface MarketAnalysisState {
  economic_data: EconomicData | null;
  news_analysis: NewsAnalysis | null;
  portfolio_impact: PortfolioImpact | null;
  analysis_status: 'idle' | 'analyzing' | 'complete' | 'error';
  query_history: MarketQuery[];
  current_query?: MarketQuery;
  errors: string[];          // Any error messages to display
  last_updated?: string;     // ISO timestamp of last successful analysis
}

// Extended portfolio state including market analysis
export interface ExtendedPortfolioState {
  // Existing portfolio data
  available_cash: number;
  investment_summary: any;
  investment_portfolio: Array<{
    ticker: string;
    amount: number;
  }>;
  tool_logs: Array<{
    id: string | number;
    message: string;
    status: "processing" | "completed";
  }>;

  // New market analysis data
  market_analysis: MarketAnalysisState;
}

// Component props interfaces
export interface MarketAnalysisPanelProps {
  portfolioContext: Array<{
    ticker: string;
    amount: number;
  }>;
}

export interface MarketQueryInputProps {
  onSubmit: (query: string) => void;
  isAnalyzing: boolean;
  portfolioContext: Array<{
    ticker: string;
    amount: number;
  }>;
  suggestedQueries?: string[];
}

export interface AnalysisProgressTrackerProps {
  toolLogs: Array<{
    id: string | number;
    message: string;
    status: "processing" | "completed";
  }>;
  onAbort: () => void;
  estimatedTimeRemaining: number;
  currentStep?: string;
}

export interface EconomicDataCardProps {
  data: EconomicData | null;
  isLoading: boolean;
  error?: string;
}

export interface NewsAnalysisCardProps {
  data: NewsAnalysis | null;
  isLoading: boolean;
  error?: string;
  portfolioTickers: string[];
}

export interface PortfolioImpactMatrixProps {
  data: PortfolioImpact | null;
  isLoading: boolean;
  error?: string;
  portfolioHoldings: Array<{
    ticker: string;
    amount: number;
  }>;
}

// API response structure from backend
export interface MarketAnalysisResponse {
  status: 'success' | 'error' | 'partial';
  economic_data?: EconomicData;
  news_analysis?: NewsAnalysis;
  portfolio_impact?: PortfolioImpact;
  errors?: string[];
  processing_time_ms: number;
  timestamp: string;
}

// Stub data configuration for development
export interface StubDataConfig {
  enable_delays: boolean;        // Simulate API delays
  simulate_errors: boolean;      // Randomly inject errors
  error_probability: number;     // 0-1 chance of error per API call
  economic_data_delay_ms: number;
  news_data_delay_ms: number;
  impact_analysis_delay_ms: number;
}