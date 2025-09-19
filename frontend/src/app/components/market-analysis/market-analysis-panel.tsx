"use client"

import { useState, useCallback, useEffect } from 'react';
import { useCoAgent, useCopilotAction } from '@copilotkit/react-core';
import { MarketQueryInput } from './market-query-input';
import { AnalysisProgressTracker } from './analysis-progress-tracker';
import { EconomicDataCard } from './economic-data-card';
import { NewsAnalysisCard } from './news-analysis-card';
import { PortfolioImpactMatrix } from './portfolio-impact-matrix';
import { InsightsSummary } from './insights-summary';
import {
  MarketAnalysisState,
  ExtendedPortfolioState,
  MarketAnalysisResponse,
  MarketQuery
} from '@/types/market-analysis';
import { AlertCircle, CheckCircle, Clock, TrendingUp } from 'lucide-react';

export function MarketAnalysisPanel() {
  const { state, setState } = useCoAgent<ExtendedPortfolioState>({
    name: "agnoAgent"
  });
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [currentQuery, setCurrentQuery] = useState<string>('');

  // Initialize market analysis state if not present
  useEffect(() => {
    if (!state?.market_analysis) {
      setState(prev => ({
        ...prev,
        market_analysis: {
          economic_data: null,
          news_analysis: null,
          portfolio_impact: null,
          analysis_status: 'idle',
          query_history: [],
          errors: []
        } as MarketAnalysisState
      }));
    }
  }, [state, setState]);

  // Handle query submission
  const handleQuerySubmit = useCallback(async (query: string) => {
    if (!query.trim() || isAnalyzing) return;

    setIsAnalyzing(true);
    setCurrentQuery(query);
    setAnalysisResults({ status: 'analyzing' });

    // Create new query record
    const newQuery: MarketQuery = {
      id: Date.now().toString(),
      query: query.trim(),
      timestamp: new Date().toISOString(),
      analysis_status: 'processing',
      portfolio_context: state?.investment_portfolio?.map(p => p.ticker) || []
    };

    // Update state to show analysis starting
    setState(prev => ({
      ...prev,
      market_analysis: {
        ...prev.market_analysis,
        analysis_status: 'analyzing',
        current_query: newQuery,
        query_history: [newQuery, ...(prev.market_analysis?.query_history || [])].slice(0, 10), // Keep last 10
        errors: []
      }
    }));

    // Add initial tool log
    setState(prev => ({
      ...prev,
      tool_logs: [
        ...(prev.tool_logs || []),
        {
          id: 'query-start',
          message: `Starting analysis: "${query}"`,
          status: 'processing'
        }
      ]
    }));

    // Call the stub API with streaming
    try {
      const portfolioTickers = state?.investment_portfolio?.map(p => p.ticker) || ['AAPL', 'MSFT'];

      const response = await fetch('/api/market-analysis-v2-stub', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          portfolio_tickers: portfolioTickers,
          query: query.trim()
        })
      });

      if (!response.ok) {
        throw new Error(`API call failed: ${response.status}`);
      }

      // Process the streaming response
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value);
          const lines = chunk.split('\n');

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const eventData = JSON.parse(line.slice(6));
                console.log('Received event:', eventData);

                // Update state based on event type
                if (eventData.type === 'PROGRESS_UPDATE') {
                  setState(prev => ({
                    ...prev,
                    tool_logs: [
                      ...(prev.tool_logs || []),
                      {
                        id: `progress-${Date.now()}`,
                        message: eventData.data.message,
                        status: eventData.data.status === 'completed' ? 'completed' : 'processing'
                      }
                    ]
                  }));
                } else if (eventData.type === 'ECONOMIC_DATA_COMPLETE') {
                  setAnalysisResults(prev => ({
                    ...prev,
                    economic_data: eventData.data.economic_data,
                    status: 'analyzing'
                  }));
                } else if (eventData.type === 'NEWS_ANALYSIS_COMPLETE') {
                  setAnalysisResults(prev => ({
                    ...prev,
                    news_analysis: eventData.data.news_analysis,
                    status: 'analyzing'
                  }));
                } else if (eventData.type === 'PORTFOLIO_IMPACT_COMPLETE') {
                  setAnalysisResults(prev => ({
                    ...prev,
                    portfolio_impact: eventData.data.portfolio_impact,
                    status: 'analyzing'
                  }));
                } else if (eventData.type === 'ANALYSIS_COMPLETE') {
                  setAnalysisResults(prev => ({
                    ...prev,
                    economic_data: eventData.data.economic_data || prev.economic_data,
                    news_analysis: eventData.data.news_analysis || prev.news_analysis,
                    portfolio_impact: eventData.data.portfolio_impact || prev.portfolio_impact,
                    status: 'complete'
                  }));

                  setIsAnalyzing(false);

                  // Update query status
                  setState(prev => {
                    if (prev.market_analysis?.current_query) {
                      const updatedQuery = {
                        ...prev.market_analysis.current_query,
                        analysis_status: 'completed' as const,
                        response_time_ms: eventData.data.processing_time_ms
                      };

                      return {
                        ...prev,
                        market_analysis: {
                          ...prev.market_analysis,
                          current_query: updatedQuery,
                          query_history: prev.market_analysis?.query_history?.map(q =>
                            q.id === updatedQuery.id ? updatedQuery : q
                          ) || []
                        }
                      };
                    }
                    return prev;
                  });
                }
              } catch (e) {
                console.error('Error parsing event data:', e);
              }
            }
          }
        }
      }
    } catch (error) {
      console.error('Analysis failed:', error);
      setIsAnalyzing(false);
      setState(prev => ({
        ...prev,
        market_analysis: {
          ...prev.market_analysis,
          analysis_status: 'error',
          errors: [`Analysis failed: ${error instanceof Error ? error.message : 'Unknown error'}`]
        }
      }));
    }
  }, [isAnalyzing, state, setState]);

  // Handle analysis abortion
  const handleAbortAnalysis = useCallback(() => {
    setIsAnalyzing(false);
    setCurrentQuery('');

    setState(prev => ({
      ...prev,
      market_analysis: {
        ...prev.market_analysis,
        analysis_status: 'idle',
        current_query: undefined
      },
      tool_logs: [
        ...(prev.tool_logs || []),
        {
          id: 'query-abort',
          message: 'Analysis aborted by user',
          status: 'completed'
        }
      ]
    }));
  }, [setState]);

  // CopilotKit action for rendering market analysis results
  useCopilotAction({
    name: "render_market_analysis",
    description: "Render comprehensive market analysis results with economic data, news, and portfolio impact",
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
          },
          status: {
            type: "string",
            description: "Analysis status: success, error, or partial"
          },
          errors: {
            type: "array",
            description: "Any error messages"
          }
        }
      }
    ],
    renderAndWaitForResponse: ({ args, respond, status }) => {
      const results = args.analysis_results as MarketAnalysisResponse;

      useEffect(() => {
        if (results && status !== "complete") {
          // Update state with analysis results
          setState(prev => ({
            ...prev,
            market_analysis: {
              ...prev.market_analysis,
              economic_data: results.economic_data || prev.market_analysis?.economic_data,
              news_analysis: results.news_analysis || prev.market_analysis?.news_analysis,
              portfolio_impact: results.portfolio_impact || prev.market_analysis?.portfolio_impact,
              analysis_status: results.status === 'error' ? 'error' : 'complete',
              errors: results.errors || [],
              last_updated: results.timestamp
            }
          }));

          setIsAnalyzing(false);

          // Update query status
          if (state?.market_analysis?.current_query) {
            const updatedQuery = {
              ...state.market_analysis.current_query,
              analysis_status: results.status === 'error' ? 'failed' : 'completed' as const,
              response_time_ms: results.processing_time_ms
            };

            setState(prev => ({
              ...prev,
              market_analysis: {
                ...prev.market_analysis,
                current_query: updatedQuery,
                query_history: prev.market_analysis?.query_history?.map(q =>
                  q.id === updatedQuery.id ? updatedQuery : q
                ) || []
              }
            }));
          }
        }
      }, [results, status]);

      return (
        <div className="p-4 border rounded-lg bg-blue-50 border-blue-200">
          <h3 className="font-semibold text-blue-900 mb-2">Market Analysis Results</h3>

          {results?.status === 'error' ? (
            <div className="flex items-center gap-2 text-red-700">
              <AlertCircle className="w-4 h-4" />
              <span>Analysis failed. Please try again.</span>
            </div>
          ) : results?.status === 'partial' ? (
            <div className="flex items-center gap-2 text-yellow-700">
              <Clock className="w-4 h-4" />
              <span>Partial results available. Some data sources failed.</span>
            </div>
          ) : (
            <div className="flex items-center gap-2 text-green-700">
              <CheckCircle className="w-4 h-4" />
              <span>Analysis complete!</span>
            </div>
          )}

          {status !== "complete" && (
            <div className="flex gap-2 mt-4">
              <button
                onClick={() => respond && respond({ accepted: true })}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
              >
                View Results
              </button>
              <button
                onClick={() => respond && respond({ accepted: false })}
                className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400 transition-colors"
              >
                Dismiss
              </button>
            </div>
          )}
        </div>
      );
    }
  });

  const portfolioContext = state?.investment_portfolio || [];
  const marketAnalysis = state?.market_analysis;
  const toolLogs = state?.tool_logs || [];

  // Component state for handling analysis results
  const [analysisResults, setAnalysisResults] = useState<{
    economic_data?: any;
    news_analysis?: any;
    portfolio_impact?: any;
    status: 'idle' | 'analyzing' | 'complete' | 'error';
  }>({ status: 'idle' });

  // Suggested queries based on portfolio
  const suggestedQueries = [
    "How will Fed rate changes impact my portfolio?",
    "What economic headwinds affect my holdings?",
    "Is there sector rotation affecting my stocks?",
    "What's the market sentiment around my positions?"
  ];

  return (
    <div className="h-full overflow-auto bg-[#FAFCFA]">
      <div className="p-6 max-w-7xl mx-auto">

        {/* Header Section */}
        <div className="mb-6">
          <div className="flex items-center gap-3 mb-2">
            <TrendingUp className="w-6 h-6 text-blue-600" />
            <h1 className="text-2xl font-bold text-gray-900">Market Analysis</h1>
          </div>
          <p className="text-gray-600">
            Ask questions about market conditions affecting your portfolio holdings
          </p>
        </div>

        {/* Query Input Section */}
        <div className="mb-6">
          <MarketQueryInput
            onSubmit={handleQuerySubmit}
            isAnalyzing={isAnalyzing}
            portfolioContext={portfolioContext}
            suggestedQueries={suggestedQueries}
          />
        </div>

        {/* Progress Tracker */}
        {isAnalyzing && (
          <div className="mb-6">
            <AnalysisProgressTracker
              toolLogs={toolLogs}
              onAbort={handleAbortAnalysis}
              estimatedTimeRemaining={120}
              currentStep={marketAnalysis?.current_query?.analysis_status || 'processing'}
            />
          </div>
        )}

        {/* Error Display */}
        {marketAnalysis?.errors && marketAnalysis.errors.length > 0 && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex items-center gap-2 text-red-800">
              <AlertCircle className="w-5 h-5" />
              <h3 className="font-semibold">Analysis Errors</h3>
            </div>
            <ul className="mt-2 text-red-700">
              {marketAnalysis.errors.map((error, index) => (
                <li key={index} className="text-sm">• {error}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Results Grid */}
        {analysisResults.status === 'complete' && (
          <div className="space-y-6">

            {/* Top Row: Economic Data and News */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <EconomicDataCard
                data={analysisResults.economic_data}
                isLoading={isAnalyzing}
                error={marketAnalysis?.errors?.find(e => e.includes('economic')) || undefined}
              />

              <NewsAnalysisCard
                data={analysisResults.news_analysis}
                isLoading={isAnalyzing}
                error={marketAnalysis?.errors?.find(e => e.includes('news')) || undefined}
                portfolioTickers={portfolioContext.map(p => p.ticker)}
              />
            </div>

            {/* Middle Row: Portfolio Impact */}
            <PortfolioImpactMatrix
              data={analysisResults.portfolio_impact}
              isLoading={isAnalyzing}
              error={marketAnalysis?.errors?.find(e => e.includes('portfolio')) || undefined}
              portfolioHoldings={portfolioContext}
            />

            {/* Bottom Row: Insights Summary */}
            <InsightsSummary
              economicData={analysisResults.economic_data}
              newsAnalysis={analysisResults.news_analysis}
              portfolioImpact={analysisResults.portfolio_impact}
            />
          </div>
        )}

        {/* Empty State */}
        {!isAnalyzing && analysisResults.status === 'idle' && (
          <div className="text-center py-12">
            <TrendingUp className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-gray-700 mb-2">
              Ready for Market Analysis
            </h2>
            <p className="text-gray-500 mb-6">
              Ask a question about market conditions to get started
            </p>
            <div className="flex flex-wrap justify-center gap-2">
              {suggestedQueries.slice(0, 2).map((query, index) => (
                <button
                  key={index}
                  onClick={() => handleQuerySubmit(query)}
                  className="px-4 py-2 text-sm bg-blue-100 text-blue-700 rounded-md hover:bg-blue-200 transition-colors"
                >
                  {query}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Query History (if we have any) */}
        {marketAnalysis?.query_history && marketAnalysis.query_history.length > 0 && (
          <div className="mt-8 p-4 bg-gray-50 rounded-lg">
            <h3 className="font-semibold text-gray-900 mb-3">Recent Queries</h3>
            <div className="space-y-2">
              {marketAnalysis.query_history.slice(0, 3).map((query) => (
                <div key={query.id} className="flex items-center justify-between text-sm">
                  <span className="text-gray-700 truncate flex-1 mr-4">
                    {query.query}
                  </span>
                  <span className="text-gray-500 text-xs">
                    {new Date(query.timestamp).toLocaleTimeString()}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}