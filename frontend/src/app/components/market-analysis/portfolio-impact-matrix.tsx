"use client"

import { PortfolioImpactMatrixProps } from '@/types/market-analysis';
import {
  AlertCircle,
  Clock,
  Target,
  TrendingUp,
  TrendingDown,
  Eye,
  ShoppingCart,
  AlertTriangle,
  Shield,
  BarChart3,
  Info
} from 'lucide-react';

export function PortfolioImpactMatrix({
  data,
  isLoading,
  error,
  portfolioHoldings
}: PortfolioImpactMatrixProps) {
  if (isLoading) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-6">
        <div className="flex items-center gap-2 mb-4">
          <Clock className="w-5 h-5 text-blue-600 animate-spin" />
          <h2 className="text-lg font-semibold text-gray-900">Portfolio Impact</h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="animate-pulse p-4 border border-gray-200 rounded-lg">
              <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
              <div className="h-6 bg-gray-200 rounded w-3/4 mb-2"></div>
              <div className="h-12 bg-gray-200 rounded"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg border border-red-200 shadow-sm p-6">
        <div className="flex items-center gap-2 mb-4">
          <AlertCircle className="w-5 h-5 text-red-600" />
          <h2 className="text-lg font-semibold text-gray-900">Portfolio Impact</h2>
        </div>
        <div className="text-center py-6">
          <AlertCircle className="w-12 h-12 text-red-400 mx-auto mb-3" />
          <p className="text-red-700 font-medium mb-2">Impact Analysis Unavailable</p>
          <p className="text-red-600 text-sm">{error}</p>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Portfolio Impact</h2>
        <div className="text-center py-6">
          <div className="text-gray-400 mb-2">No impact analysis available</div>
          <div className="text-sm text-gray-500">Request an analysis to see portfolio impact</div>
        </div>
      </div>
    );
  }

  const getImpactColor = (level: string) => {
    switch (level) {
      case 'high':
        return 'bg-red-100 border-red-300 text-red-800';
      case 'medium':
        return 'bg-yellow-100 border-yellow-300 text-yellow-800';
      case 'low':
        return 'bg-green-100 border-green-300 text-green-800';
      default:
        return 'bg-gray-100 border-gray-300 text-gray-800';
    }
  };

  const getActionIcon = (action: string) => {
    switch (action) {
      case 'buy':
        return <ShoppingCart className="w-4 h-4 text-green-600" />;
      case 'sell':
        return <TrendingDown className="w-4 h-4 text-red-600" />;
      case 'hold':
        return <Shield className="w-4 h-4 text-blue-600" />;
      case 'watch':
        return <Eye className="w-4 h-4 text-yellow-600" />;
      default:
        return <Target className="w-4 h-4 text-gray-600" />;
    }
  };

  const getActionColor = (action: string) => {
    switch (action) {
      case 'buy':
        return 'text-green-700 bg-green-50 border-green-200';
      case 'sell':
        return 'text-red-700 bg-red-50 border-red-200';
      case 'hold':
        return 'text-blue-700 bg-blue-50 border-blue-200';
      case 'watch':
        return 'text-yellow-700 bg-yellow-50 border-yellow-200';
      default:
        return 'text-gray-700 bg-gray-50 border-gray-200';
    }
  };

  const getRiskIcon = (level: string) => {
    switch (level) {
      case 'critical':
      case 'high':
        return <AlertTriangle className="w-5 h-5 text-red-600" />;
      case 'medium':
        return <AlertCircle className="w-5 h-5 text-yellow-600" />;
      case 'low':
        return <Shield className="w-5 h-5 text-green-600" />;
      default:
        return <Info className="w-5 h-5 text-gray-600" />;
    }
  };

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'critical':
      case 'high':
        return 'text-red-700 bg-red-50 border-red-200';
      case 'medium':
        return 'text-yellow-700 bg-yellow-50 border-yellow-200';
      case 'low':
        return 'text-green-700 bg-green-50 border-green-200';
      default:
        return 'text-gray-700 bg-gray-50 border-gray-200';
    }
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
      {/* Header */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center justify-between mb-2">
          <h2 className="text-lg font-semibold text-gray-900">Portfolio Impact Analysis</h2>
          <div className="flex items-center gap-2">
            <BarChart3 className="w-4 h-4 text-gray-400" />
            <span className="text-xs text-gray-500">{data.holdings_impact.length} holdings analyzed</span>
          </div>
        </div>

        {/* Overall Risk Assessment */}
        <div className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full border text-sm font-medium ${getRiskColor(data.overall_risk_assessment.level)}`}>
          {getRiskIcon(data.overall_risk_assessment.level)}
          <span>Overall Risk: {data.overall_risk_assessment.level.toUpperCase()}</span>
          <span className="text-xs opacity-75">
            ({Math.round(data.overall_risk_assessment.score * 100)}%)
          </span>
        </div>
      </div>

      {/* Holdings Impact Grid */}
      <div className="p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
          {data.holdings_impact.map((holding, index) => {
            const portfolioHolding = portfolioHoldings.find(h => h.ticker === holding.ticker);

            return (
              <div
                key={holding.ticker}
                className={`p-4 rounded-lg border-2 transition-all hover:shadow-md ${getImpactColor(holding.impact_level)}`}
              >
                {/* Holding Header */}
                <div className="flex items-center justify-between mb-3">
                  <div>
                    <h3 className="font-bold text-lg">{holding.ticker}</h3>
                    {portfolioHolding && (
                      <p className="text-xs opacity-75">
                        ${portfolioHolding.amount.toLocaleString()} invested
                      </p>
                    )}
                  </div>
                  <div className="text-right">
                    <div className="text-lg font-bold">
                      {Math.round(holding.impact_score * 100)}%
                    </div>
                    <div className="text-xs opacity-75">Impact Score</div>
                  </div>
                </div>

                {/* Impact Details */}
                <div className="space-y-2 mb-3">
                  <p className="text-sm leading-relaxed">
                    {holding.reasoning}
                  </p>

                  {/* Factors */}
                  {holding.factors && holding.factors.length > 0 && (
                    <div>
                      <p className="text-xs font-medium mb-1">Key Factors:</p>
                      <div className="flex flex-wrap gap-1">
                        {holding.factors.map((factor, i) => (
                          <span
                            key={i}
                            className="inline-block text-xs px-2 py-0.5 bg-white bg-opacity-60 rounded border"
                          >
                            {factor}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {/* Action and Confidence */}
                <div className="flex items-center justify-between">
                  <div className={`flex items-center gap-1 px-2 py-1 rounded-full border text-xs font-medium ${getActionColor(holding.recommended_action)}`}>
                    {getActionIcon(holding.recommended_action)}
                    <span className="capitalize">{holding.recommended_action}</span>
                  </div>
                  <div className="text-xs">
                    <span className="opacity-75">Confidence: </span>
                    <span className="font-medium">
                      {Math.round(holding.confidence * 100)}%
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Market Outlook */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          {/* Short & Medium Term Outlook */}
          <div className="p-4 bg-purple-50 rounded-lg border border-purple-200">
            <h3 className="font-semibold text-purple-900 mb-3">Market Outlook</h3>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm text-purple-800">Short-term (3 months):</span>
                <span className={`px-2 py-1 rounded text-xs font-medium ${
                  data.market_outlook.short_term === 'bullish' ? 'bg-green-100 text-green-800' :
                  data.market_outlook.short_term === 'bearish' ? 'bg-red-100 text-red-800' :
                  'bg-gray-100 text-gray-800'
                }`}>
                  {data.market_outlook.short_term}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-purple-800">Medium-term (12 months):</span>
                <span className={`px-2 py-1 rounded text-xs font-medium ${
                  data.market_outlook.medium_term === 'bullish' ? 'bg-green-100 text-green-800' :
                  data.market_outlook.medium_term === 'bearish' ? 'bg-red-100 text-red-800' :
                  'bg-gray-100 text-gray-800'
                }`}>
                  {data.market_outlook.medium_term}
                </span>
              </div>
            </div>

            {/* Key Drivers */}
            <div className="mt-3">
              <p className="text-xs font-medium text-purple-900 mb-1">Key Drivers:</p>
              <ul className="text-xs text-purple-800 space-y-0.5">
                {data.market_outlook.key_drivers.map((driver, i) => (
                  <li key={i}>• {driver}</li>
                ))}
              </ul>
            </div>
          </div>

          {/* Confidence Scores */}
          <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
            <h3 className="font-semibold text-gray-900 mb-3">Analysis Confidence</h3>
            <div className="space-y-3">
              {Object.entries(data.confidence_scores).map(([key, score]) => (
                <div key={key}>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm text-gray-700 capitalize">
                      {key.replace('_', ' ')}
                    </span>
                    <span className="text-sm font-medium">
                      {Math.round((score as number) * 100)}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${
                        (score as number) > 0.8 ? 'bg-green-500' :
                        (score as number) > 0.6 ? 'bg-yellow-500' : 'bg-red-500'
                      }`}
                      style={{ width: `${(score as number) * 100}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Recommended Actions */}
        {data.recommended_actions && data.recommended_actions.length > 0 && (
          <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
            <h3 className="font-semibold text-blue-900 mb-3">Recommended Actions</h3>
            <div className="space-y-3">
              {data.recommended_actions.map((action, index) => (
                <div key={index} className="flex items-start gap-3">
                  <div className={`p-1.5 rounded-full ${
                    action.priority === 'urgent' ? 'bg-red-100' :
                    action.priority === 'important' ? 'bg-yellow-100' :
                    'bg-blue-100'
                  }`}>
                    <Target className={`w-3 h-3 ${
                      action.priority === 'urgent' ? 'text-red-600' :
                      action.priority === 'important' ? 'text-yellow-600' :
                      'text-blue-600'
                    }`} />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-medium text-blue-900 capitalize">
                        {action.action_type}
                      </span>
                      <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                        action.priority === 'urgent' ? 'bg-red-100 text-red-800' :
                        action.priority === 'important' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-blue-100 text-blue-800'
                      }`}>
                        {action.priority}
                      </span>
                    </div>
                    <p className="text-sm text-blue-800 mb-1">{action.description}</p>
                    <div className="flex items-center gap-4 text-xs text-blue-700">
                      <span>Affects: {action.affected_tickers.join(', ')}</span>
                      <span>Impact: {action.estimated_impact}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Major Risks */}
        {data.market_outlook.major_risks && data.market_outlook.major_risks.length > 0 && (
          <div className="mt-4 p-4 bg-red-50 rounded-lg border border-red-200">
            <h4 className="font-medium text-red-900 mb-2">Major Risks to Monitor</h4>
            <ul className="text-sm text-red-800 space-y-1">
              {data.market_outlook.major_risks.map((risk, i) => (
                <li key={i} className="flex items-start gap-2">
                  <AlertTriangle className="w-4 h-4 text-red-600 mt-0.5 flex-shrink-0" />
                  <span>{risk}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}