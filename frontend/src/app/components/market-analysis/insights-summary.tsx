"use client"

import { EconomicData, NewsAnalysis, PortfolioImpact } from '@/types/market-analysis';
import { Lightbulb, TrendingUp, TrendingDown, Target, AlertTriangle } from 'lucide-react';

interface InsightsSummaryProps {
  economicData: EconomicData | null;
  newsAnalysis: NewsAnalysis | null;
  portfolioImpact: PortfolioImpact | null;
}

export function InsightsSummary({
  economicData,
  newsAnalysis,
  portfolioImpact
}: InsightsSummaryProps) {
  // Don't render if no data is available
  if (!economicData && !newsAnalysis && !portfolioImpact) {
    return null;
  }

  // Generate key insights from the data
  const generateInsights = () => {
    const insights = [];

    // Economic insights
    if (economicData) {
      if (economicData.federal_funds_rate.trend === 'up') {
        insights.push({
          type: 'economic',
          icon: <TrendingUp className="w-4 h-4 text-blue-600" />,
          title: 'Rising Interest Rates',
          description: `Fed rate at ${economicData.federal_funds_rate.value}% may pressure growth stocks while benefiting financial sector holdings.`,
          impact: 'medium'
        });
      }

      if (economicData.inflation_rate.value > 3.0) {
        insights.push({
          type: 'economic',
          icon: <AlertTriangle className="w-4 h-4 text-yellow-600" />,
          title: 'Elevated Inflation',
          description: `Inflation at ${economicData.inflation_rate.value}% suggests continued monetary policy vigilance affecting rate-sensitive investments.`,
          impact: 'medium'
        });
      }

      if (economicData.unemployment_rate.value < 4.0) {
        insights.push({
          type: 'economic',
          icon: <TrendingUp className="w-4 h-4 text-green-600" />,
          title: 'Strong Labor Market',
          description: `Low unemployment at ${economicData.unemployment_rate.value}% indicates economic strength but may pressure wage costs.`,
          impact: 'low'
        });
      }
    }

    // News sentiment insights
    if (newsAnalysis) {
      if (newsAnalysis.sentiment_summary.overall_tone === 'bullish') {
        insights.push({
          type: 'sentiment',
          icon: <TrendingUp className="w-4 h-4 text-green-600" />,
          title: 'Positive Market Sentiment',
          description: `${newsAnalysis.sentiment_summary.positive}% of recent news shows positive sentiment, supporting market optimism.`,
          impact: 'medium'
        });
      } else if (newsAnalysis.sentiment_summary.overall_tone === 'bearish') {
        insights.push({
          type: 'sentiment',
          icon: <TrendingDown className="w-4 h-4 text-red-600" />,
          title: 'Cautious Market Sentiment',
          description: `${newsAnalysis.sentiment_summary.negative}% negative sentiment in recent news may weigh on market confidence.`,
          impact: 'medium'
        });
      }

      if (newsAnalysis.portfolio_relevance.coverage_score > 0.8) {
        insights.push({
          type: 'sentiment',
          icon: <Target className="w-4 h-4 text-blue-600" />,
          title: 'High Portfolio Coverage',
          description: `${Math.round(newsAnalysis.portfolio_relevance.coverage_score * 100)}% of your holdings are well-covered in current market discussion.`,
          impact: 'low'
        });
      }
    }

    // Portfolio impact insights
    if (portfolioImpact) {
      const highImpactHoldings = portfolioImpact.holdings_impact.filter(h => h.impact_level === 'high');
      if (highImpactHoldings.length > 0) {
        insights.push({
          type: 'portfolio',
          icon: <AlertTriangle className="w-4 h-4 text-red-600" />,
          title: 'High-Impact Holdings',
          description: `${highImpactHoldings.length} holdings (${highImpactHoldings.map(h => h.ticker).join(', ')}) show high sensitivity to current conditions.`,
          impact: 'high'
        });
      }

      if (portfolioImpact.overall_risk_assessment.level === 'low') {
        insights.push({
          type: 'portfolio',
          icon: <TrendingUp className="w-4 h-4 text-green-600" />,
          title: 'Favorable Risk Profile',
          description: 'Your portfolio shows low risk exposure to current market conditions with balanced positioning.',
          impact: 'low'
        });
      } else if (portfolioImpact.overall_risk_assessment.level === 'high') {
        insights.push({
          type: 'portfolio',
          icon: <AlertTriangle className="w-4 h-4 text-red-600" />,
          title: 'Elevated Portfolio Risk',
          description: 'Current market conditions present higher risk for your portfolio positioning. Consider defensive measures.',
          impact: 'high'
        });
      }

      // Action-specific insights
      const urgentActions = portfolioImpact.recommended_actions?.filter(a => a.priority === 'urgent') || [];
      if (urgentActions.length > 0) {
        insights.push({
          type: 'action',
          icon: <Target className="w-4 h-4 text-orange-600" />,
          title: 'Urgent Actions Required',
          description: `${urgentActions.length} urgent action(s) recommended for optimal portfolio positioning.`,
          impact: 'high'
        });
      }
    }

    return insights;
  };

  const insights = generateInsights();

  if (insights.length === 0) {
    return null;
  }

  const getImpactColor = (impact: string) => {
    switch (impact) {
      case 'high':
        return 'border-red-200 bg-red-50';
      case 'medium':
        return 'border-yellow-200 bg-yellow-50';
      case 'low':
        return 'border-green-200 bg-green-50';
      default:
        return 'border-gray-200 bg-gray-50';
    }
  };

  const getImpactTextColor = (impact: string) => {
    switch (impact) {
      case 'high':
        return 'text-red-800';
      case 'medium':
        return 'text-yellow-800';
      case 'low':
        return 'text-green-800';
      default:
        return 'text-gray-800';
    }
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
      {/* Header */}
      <div className="p-6 border-b border-gray-200 bg-gradient-to-r from-indigo-50 to-purple-50">
        <div className="flex items-center gap-2">
          <Lightbulb className="w-6 h-6 text-indigo-600" />
          <h2 className="text-lg font-semibold text-gray-900">Key Insights</h2>
        </div>
        <p className="text-sm text-gray-600 mt-1">
          Synthesis of economic data, market sentiment, and portfolio analysis
        </p>
      </div>

      {/* Insights Grid */}
      <div className="p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {insights.map((insight, index) => (
            <div
              key={index}
              className={`p-4 rounded-lg border ${getImpactColor(insight.impact)} transition-all hover:shadow-md`}
            >
              <div className="flex items-start gap-3">
                <div className="flex-shrink-0 mt-0.5">
                  {insight.icon}
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <h3 className={`font-semibold ${getImpactTextColor(insight.impact)}`}>
                      {insight.title}
                    </h3>
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                      insight.impact === 'high' ? 'bg-red-100 text-red-700' :
                      insight.impact === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                      'bg-green-100 text-green-700'
                    }`}>
                      {insight.impact} impact
                    </span>
                  </div>
                  <p className={`text-sm leading-relaxed ${getImpactTextColor(insight.impact)}`}>
                    {insight.description}
                  </p>
                  <div className="mt-2">
                    <span className={`inline-block px-2 py-1 rounded text-xs font-medium ${
                      insight.type === 'economic' ? 'bg-blue-100 text-blue-700' :
                      insight.type === 'sentiment' ? 'bg-purple-100 text-purple-700' :
                      insight.type === 'portfolio' ? 'bg-indigo-100 text-indigo-700' :
                      'bg-orange-100 text-orange-700'
                    }`}>
                      {insight.type}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Summary Statistics */}
        <div className="mt-6 pt-6 border-t border-gray-200">
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold text-gray-900">
                {economicData ? Object.keys(economicData).filter(key => key !== 'data_freshness' && key !== 'source_citations').length : 0}
              </div>
              <div className="text-xs text-gray-600">Economic Indicators</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900">
                {newsAnalysis?.articles.length || 0}
              </div>
              <div className="text-xs text-gray-600">News Articles</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900">
                {portfolioImpact?.holdings_impact.length || 0}
              </div>
              <div className="text-xs text-gray-600">Holdings Analyzed</div>
            </div>
          </div>
        </div>

        {/* Overall Assessment */}
        {portfolioImpact?.overall_risk_assessment && (
          <div className="mt-4 p-4 bg-indigo-50 rounded-lg border border-indigo-200">
            <div className="flex items-center gap-2 mb-2">
              <Target className="w-4 h-4 text-indigo-600" />
              <h4 className="font-medium text-indigo-900">Overall Assessment</h4>
            </div>
            <p className="text-sm text-indigo-800">
              {portfolioImpact.overall_risk_assessment.description}
            </p>
            <div className="mt-2 text-xs text-indigo-700">
              Risk Level: <span className="font-semibold capitalize">{portfolioImpact.overall_risk_assessment.level}</span>
              {' '} • Time Horizon: <span className="font-semibold">{portfolioImpact.overall_risk_assessment.time_horizon}</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}