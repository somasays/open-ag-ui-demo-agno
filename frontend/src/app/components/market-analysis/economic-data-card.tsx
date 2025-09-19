"use client"

import { EconomicDataCardProps, EconomicIndicator } from '@/types/market-analysis';
import { TrendingUp, TrendingDown, Minus, ExternalLink, AlertCircle, Clock } from 'lucide-react';

export function EconomicDataCard({ data, isLoading, error }: EconomicDataCardProps) {
  if (isLoading) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-6">
        <div className="flex items-center gap-2 mb-4">
          <Clock className="w-5 h-5 text-blue-600 animate-spin" />
          <h2 className="text-lg font-semibold text-gray-900">Economic Data</h2>
        </div>
        <div className="space-y-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-1/3 mb-2"></div>
              <div className="h-8 bg-gray-200 rounded w-1/2"></div>
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
          <h2 className="text-lg font-semibold text-gray-900">Economic Data</h2>
        </div>
        <div className="text-center py-6">
          <AlertCircle className="w-12 h-12 text-red-400 mx-auto mb-3" />
          <p className="text-red-700 font-medium mb-2">Data Unavailable</p>
          <p className="text-red-600 text-sm">{error}</p>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Economic Data</h2>
        <div className="text-center py-6">
          <div className="text-gray-400 mb-2">No economic data available</div>
          <div className="text-sm text-gray-500">Request an analysis to see economic indicators</div>
        </div>
      </div>
    );
  }

  const renderIndicator = (indicator: EconomicIndicator, label: string, unit: string) => {
    const getTrendIcon = () => {
      switch (indicator.trend) {
        case 'up':
          return <TrendingUp className="w-4 h-4 text-green-600" />;
        case 'down':
          return <TrendingDown className="w-4 h-4 text-red-600" />;
        default:
          return <Minus className="w-4 h-4 text-gray-400" />;
      }
    };

    const getTrendColor = () => {
      switch (indicator.trend) {
        case 'up':
          return 'text-green-600';
        case 'down':
          return 'text-red-600';
        default:
          return 'text-gray-600';
      }
    };

    const getChangeColor = () => {
      const change = indicator.change;
      if (change > 0) return 'text-green-600';
      if (change < 0) return 'text-red-600';
      return 'text-gray-600';
    };

    return (
      <div className="p-4 bg-gray-50 rounded-lg">
        <div className="flex items-center justify-between mb-2">
          <h3 className="font-medium text-gray-900">{label}</h3>
          <div className="flex items-center gap-1">
            {getTrendIcon()}
            <span className={`text-xs font-medium ${getTrendColor()}`}>
              {indicator.trend}
            </span>
          </div>
        </div>

        <div className="flex items-baseline gap-2 mb-2">
          <span className="text-2xl font-bold text-gray-900">
            {indicator.value.toFixed(indicator.value % 1 === 0 ? 0 : 1)}{unit}
          </span>
          <span className={`text-sm font-medium ${getChangeColor()}`}>
            {indicator.change > 0 ? '+' : ''}{indicator.change.toFixed(1)}{unit}
          </span>
        </div>

        <div className="flex items-center justify-between text-xs text-gray-500">
          <span>
            As of {new Date(indicator.date).toLocaleDateString()}
          </span>
          <div className="flex items-center gap-1">
            <div className={`w-2 h-2 rounded-full ${
              indicator.confidence > 0.8 ? 'bg-green-400' :
              indicator.confidence > 0.6 ? 'bg-yellow-400' : 'bg-red-400'
            }`} />
            <span>{Math.round(indicator.confidence * 100)}% confidence</span>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
      {/* Header */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900">Economic Indicators</h2>
          <div className="flex items-center gap-2 text-xs text-gray-500">
            <span>Updated: {new Date(data.data_freshness).toLocaleString()}</span>
          </div>
        </div>
        <p className="text-sm text-gray-600 mt-1">
          Federal Reserve and economic data from trusted sources
        </p>
      </div>

      {/* Indicators Grid */}
      <div className="p-6">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
          {renderIndicator(data.federal_funds_rate, 'Federal Funds Rate', '%')}
          {renderIndicator(data.inflation_rate, 'Inflation Rate (CPI)', '%')}
          {renderIndicator(data.gdp_growth, 'GDP Growth', '%')}
          {renderIndicator(data.unemployment_rate, 'Unemployment Rate', '%')}
        </div>

        {/* Economic Summary */}
        <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
          <h3 className="font-medium text-blue-900 mb-2">Economic Environment Summary</h3>
          <div className="text-sm text-blue-800 space-y-1">
            <p>
              • Federal funds rate at {data.federal_funds_rate.value}%
              ({data.federal_funds_rate.trend === 'up' ? 'rising' : data.federal_funds_rate.trend === 'down' ? 'falling' : 'stable'})
            </p>
            <p>
              • Inflation {data.inflation_rate.trend === 'up' ? 'increasing' : data.inflation_rate.trend === 'down' ? 'decreasing' : 'stable'}
              at {data.inflation_rate.value}%
            </p>
            <p>
              • GDP growth showing {data.gdp_growth.trend === 'up' ? 'expansion' : data.gdp_growth.trend === 'down' ? 'contraction' : 'stability'}
              at {data.gdp_growth.value}%
            </p>
            <p>
              • Labor market {data.unemployment_rate.trend === 'up' ? 'loosening' : data.unemployment_rate.trend === 'down' ? 'tightening' : 'stable'}
              with {data.unemployment_rate.value}% unemployment
            </p>
          </div>
        </div>

        {/* Source Citations */}
        {data.source_citations && data.source_citations.length > 0 && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <h4 className="text-sm font-medium text-gray-900 mb-2">Data Sources</h4>
            <div className="space-y-1">
              {data.source_citations.map((citation, index) => (
                <div key={index} className="flex items-center gap-2 text-xs text-gray-600">
                  <ExternalLink className="w-3 h-3" />
                  <a
                    href={citation.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="hover:text-blue-600 underline"
                  >
                    {citation.source}: {citation.description}
                  </a>
                </div>
              ))}
            </div>
            <p className="text-xs text-gray-500 mt-2">
              Last accessed: {new Date(data.source_citations[0]?.accessed_at).toLocaleString()}
            </p>
          </div>
        )}

        {/* Market Impact Indicator */}
        <div className="mt-4 p-3 bg-yellow-50 rounded-lg border border-yellow-200">
          <div className="flex items-start gap-2">
            <div className="w-2 h-2 rounded-full bg-yellow-400 mt-1.5 flex-shrink-0" />
            <div>
              <p className="text-sm font-medium text-yellow-800">Market Impact Assessment</p>
              <p className="text-xs text-yellow-700 mt-1">
                Current economic conditions suggest {
                  data.federal_funds_rate.trend === 'up' ? 'potential headwinds for growth stocks' :
                  data.federal_funds_rate.trend === 'down' ? 'supportive environment for risk assets' :
                  'mixed signals requiring careful portfolio positioning'
                }
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}