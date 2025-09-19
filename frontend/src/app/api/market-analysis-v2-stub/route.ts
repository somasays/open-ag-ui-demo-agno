import { NextRequest, NextResponse } from 'next/server';

// Simple data generators
function generateEconomicData() {
  const currentDate = new Date();
  return {
    federal_funds_rate: {
      value: 5.33,
      change: 0.25,
      date: currentDate.toISOString().split('T')[0],
      trend: 'up' as const,
      confidence: 0.92
    },
    inflation_rate: {
      value: 3.1,
      change: -0.2,
      date: new Date(currentDate.getTime() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      trend: 'down' as const,
      confidence: 0.88
    },
    gdp_growth: {
      value: 2.8,
      change: 0.3,
      date: currentDate.toISOString().split('T')[0].replace(/\d{2}$/, 'Q4'),
      trend: 'up' as const,
      confidence: 0.81
    },
    unemployment_rate: {
      value: 3.7,
      change: -0.1,
      date: new Date(currentDate.getTime() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      trend: 'down' as const,
      confidence: 0.94
    },
    data_freshness: currentDate.toISOString(),
    source_citations: [
      {
        source: "FRED",
        url: "https://fred.stlouisfed.org/series/DFF",
        description: "Federal Funds Effective Rate",
        accessed_at: currentDate.toISOString()
      }
    ]
  };
}

function generateNewsAnalysis(portfolioTickers: string[]) {
  const articles = [
    {
      title: "Fed Signals Potential Rate Pause as Inflation Shows Signs of Cooling",
      source: "Reuters",
      url: "https://example.com/article-1",
      snippet: "Federal Reserve officials indicated they may pause interest rate hikes following recent inflation data...",
      relevance_score: 0.92,
      published_date: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
      portfolio_tickers: portfolioTickers.filter(t => ['AAPL', 'MSFT', 'GOOGL'].includes(t)),
      sentiment: 'positive' as const
    },
    {
      title: "Technology Sector Outlook: Navigating Rate Environment",
      source: "Bloomberg",
      url: "https://example.com/article-2",
      snippet: "Technology companies continue to face headwinds from higher interest rates while investing in AI...",
      relevance_score: 0.87,
      published_date: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
      portfolio_tickers: portfolioTickers.filter(t => ['AAPL', 'MSFT', 'NVDA'].includes(t)),
      sentiment: 'neutral' as const
    }
  ];

  return {
    articles,
    sentiment_summary: {
      positive: 50,
      neutral: 30,
      negative: 20,
      overall_tone: 'bullish' as const
    },
    portfolio_relevance: {
      high: 2,
      medium: 0,
      low: 0,
      coverage_score: 0.78
    },
    search_metadata: {
      query_used: `market analysis ${portfolioTickers.join(' ')}`,
      total_results: articles.length,
      search_time_ms: 1850,
      filters_applied: ["financial_news", "last_7_days", "english"]
    }
  };
}

function generatePortfolioImpact(portfolioTickers: string[]) {
  const holdingsImpact = portfolioTickers.map(ticker => {
    const isTech = ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'META'].includes(ticker);

    return {
      ticker,
      impact_level: isTech ? 'medium' : 'low' as const,
      impact_score: isTech ? 0.7 : 0.4,
      reasoning: isTech
        ? `${ticker} may face pressure from rising rates affecting growth valuations.`
        : `${ticker} shows moderate sensitivity to current economic conditions.`,
      recommended_action: 'hold' as const,
      confidence: isTech ? 0.75 : 0.65,
      factors: ['Interest rate environment', 'Market sentiment', 'Earnings expectations']
    };
  });

  return {
    holdings_impact: holdingsImpact,
    overall_risk_assessment: {
      level: 'medium' as const,
      score: 0.62,
      description: "Current market conditions present moderate opportunities with manageable risks.",
      time_horizon: "medium-term"
    },
    recommended_actions: [
      {
        action_type: 'monitor' as const,
        priority: 'normal' as const,
        description: "Monitor rate environment impact on growth positions.",
        affected_tickers: portfolioTickers,
        estimated_impact: "2-5% portfolio adjustment"
      }
    ],
    confidence_scores: {
      economic_analysis: 0.84,
      news_sentiment: 0.72,
      portfolio_impact: 0.78,
      overall_assessment: 0.81
    },
    market_outlook: {
      short_term: 'neutral' as const,
      medium_term: 'bullish' as const,
      key_drivers: ["Federal Reserve policy", "Inflation trajectory"],
      major_risks: ["Interest rate volatility", "Market sentiment shifts"]
    }
  };
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { portfolio_tickers = [], query = '' } = body;

    console.log('🔍 Market Analysis Stub API called:', {
      portfolio_tickers,
      query,
      timestamp: new Date().toISOString()
    });

    const encoder = new TextEncoder();

    const stream = new ReadableStream({
      async start(controller) {
        const sendEvent = (eventType: string, data: any) => {
          const eventData = {
            type: eventType,
            data,
            timestamp: new Date().toISOString()
          };
          const chunk = `data: ${JSON.stringify(eventData)}\n\n`;
          controller.enqueue(encoder.encode(chunk));
        };

        try {
          // 1. Analysis started
          sendEvent('ANALYSIS_STARTED', {
            query,
            portfolio_context: portfolio_tickers,
            estimated_duration: 90
          });

          await new Promise(resolve => setTimeout(resolve, 1000));

          // 2. Economic data processing
          sendEvent('PROGRESS_UPDATE', {
            step: 'economic_data',
            status: 'processing',
            message: 'Fetching Federal Reserve economic indicators...'
          });

          await new Promise(resolve => setTimeout(resolve, 2000));

          const economicData = generateEconomicData();
          sendEvent('ECONOMIC_DATA_COMPLETE', {
            economic_data: economicData
          });

          sendEvent('PROGRESS_UPDATE', {
            step: 'economic_data',
            status: 'completed',
            message: 'Economic indicators retrieved successfully'
          });

          await new Promise(resolve => setTimeout(resolve, 1000));

          // 3. News analysis processing
          sendEvent('PROGRESS_UPDATE', {
            step: 'news_analysis',
            status: 'processing',
            message: 'Searching relevant market news...'
          });

          await new Promise(resolve => setTimeout(resolve, 2000));

          const newsAnalysis = generateNewsAnalysis(portfolio_tickers);
          sendEvent('NEWS_ANALYSIS_COMPLETE', {
            news_analysis: newsAnalysis
          });

          sendEvent('PROGRESS_UPDATE', {
            step: 'news_analysis',
            status: 'completed',
            message: 'Market news analysis complete'
          });

          await new Promise(resolve => setTimeout(resolve, 1000));

          // 4. Portfolio impact processing
          sendEvent('PROGRESS_UPDATE', {
            step: 'portfolio_impact',
            status: 'processing',
            message: 'Analyzing portfolio impact...'
          });

          await new Promise(resolve => setTimeout(resolve, 2000));

          const portfolioImpact = generatePortfolioImpact(portfolio_tickers);
          sendEvent('PORTFOLIO_IMPACT_COMPLETE', {
            portfolio_impact: portfolioImpact
          });

          sendEvent('PROGRESS_UPDATE', {
            step: 'portfolio_impact',
            status: 'completed',
            message: 'Portfolio impact analysis complete'
          });

          await new Promise(resolve => setTimeout(resolve, 500));

          // 5. Final analysis complete
          sendEvent('ANALYSIS_COMPLETE', {
            status: 'success',
            processing_time_ms: 8000,
            economic_data: economicData,
            news_analysis: newsAnalysis,
            portfolio_impact: portfolioImpact,
            timestamp: new Date().toISOString()
          });

          controller.close();

        } catch (error) {
          sendEvent('ANALYSIS_ERROR', {
            error: error instanceof Error ? error.message : 'Unknown error occurred',
            timestamp: new Date().toISOString()
          });
          controller.close();
        }
      }
    });

    return new Response(stream, {
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
      },
    });

  } catch (error) {
    console.error('❌ Market Analysis Stub API error:', error);
    return NextResponse.json(
      {
        error: 'Failed to process market analysis request',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
}

export async function OPTIONS() {
  return new Response(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    },
  });
}

export async function GET() {
  return NextResponse.json({
    message: 'Market Analysis V2 Stub API',
    version: '1.0.0',
    endpoints: {
      'POST /api/market-analysis-v2-stub': 'Stream market analysis with stub data',
    },
    example_payload: {
      portfolio_tickers: ['AAPL', 'MSFT', 'GOOGL'],
      query: 'How will Fed rate changes impact my tech stocks?'
    },
    description: 'Stub API that simulates real market analysis workflow with realistic delays and progressive data delivery'
  });
}