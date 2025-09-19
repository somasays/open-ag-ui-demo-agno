"use client"

import { NewsAnalysisCardProps } from '@/types/market-analysis';
import {
  ExternalLink,
  AlertCircle,
  Clock,
  TrendingUp,
  TrendingDown,
  Minus,
  Star,
  Calendar,
  Search
} from 'lucide-react';

export function NewsAnalysisCard({
  data,
  isLoading,
  error,
  portfolioTickers
}: NewsAnalysisCardProps) {
  if (isLoading) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-6">
        <div className="flex items-center gap-2 mb-4">
          <Clock className="w-5 h-5 text-blue-600 animate-spin" />
          <h2 className="text-lg font-semibold text-gray-900">Market News</h2>
        </div>
        <div className="space-y-4">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="animate-pulse border-b border-gray-100 pb-4 last:border-b-0">
              <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
              <div className="h-3 bg-gray-200 rounded w-1/2 mb-2"></div>
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
          <h2 className="text-lg font-semibold text-gray-900">Market News</h2>
        </div>
        <div className="text-center py-6">
          <AlertCircle className="w-12 h-12 text-red-400 mx-auto mb-3" />
          <p className="text-red-700 font-medium mb-2">News Unavailable</p>
          <p className="text-red-600 text-sm">{error}</p>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Market News</h2>
        <div className="text-center py-6">
          <div className="text-gray-400 mb-2">No news analysis available</div>
          <div className="text-sm text-gray-500">Request an analysis to see relevant market news</div>
        </div>
      </div>
    );
  }

  const getSentimentIcon = (sentiment: string) => {
    switch (sentiment) {
      case 'positive':
        return <TrendingUp className="w-4 h-4 text-green-600" />;
      case 'negative':
        return <TrendingDown className="w-4 h-4 text-red-600" />;
      default:
        return <Minus className="w-4 h-4 text-gray-400" />;
    }
  };

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case 'positive':
        return 'text-green-600 bg-green-50 border-green-200';
      case 'negative':
        return 'text-red-600 bg-red-50 border-red-200';
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getRelevanceStars = (score: number) => {
    const stars = Math.round(score * 5);
    return Array.from({ length: 5 }, (_, i) => (
      <Star
        key={i}
        className={`w-3 h-3 ${
          i < stars ? 'text-yellow-400 fill-current' : 'text-gray-300'
        }`}
      />
    ));
  };

  const highlightPortfolioTickers = (text: string, tickers: string[]) => {
    let highlightedText = text;
    tickers.forEach(ticker => {
      const regex = new RegExp(`\\b${ticker}\\b`, 'gi');
      highlightedText = highlightedText.replace(
        regex,
        `<span class="bg-blue-100 text-blue-800 px-1 py-0.5 rounded text-xs font-mono font-semibold">${ticker}</span>`
      );
    });
    return highlightedText;
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
      {/* Header */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center justify-between mb-2">
          <h2 className="text-lg font-semibold text-gray-900">Market News & Sentiment</h2>
          <div className="flex items-center gap-2">
            <Search className="w-4 h-4 text-gray-400" />
            <span className="text-xs text-gray-500">{data.articles.length} articles</span>
          </div>
        </div>

        {/* Sentiment Overview */}
        <div className="flex items-center gap-4 text-sm">
          <div className="flex items-center gap-1">
            <TrendingUp className="w-4 h-4 text-green-600" />
            <span className="text-green-700">{data.sentiment_summary.positive}% Positive</span>
          </div>
          <div className="flex items-center gap-1">
            <Minus className="w-4 h-4 text-gray-400" />
            <span className="text-gray-600">{data.sentiment_summary.neutral}% Neutral</span>
          </div>
          <div className="flex items-center gap-1">
            <TrendingDown className="w-4 h-4 text-red-600" />
            <span className="text-red-700">{data.sentiment_summary.negative}% Negative</span>
          </div>
        </div>

        {/* Overall Tone */}
        <div className="mt-3">
          <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium border ${
            data.sentiment_summary.overall_tone === 'bullish'
              ? 'text-green-700 bg-green-50 border-green-200'
              : data.sentiment_summary.overall_tone === 'bearish'
              ? 'text-red-700 bg-red-50 border-red-200'
              : 'text-gray-700 bg-gray-50 border-gray-200'
          }`}>
            {data.sentiment_summary.overall_tone === 'bullish' && <TrendingUp className="w-3 h-3" />}
            {data.sentiment_summary.overall_tone === 'bearish' && <TrendingDown className="w-3 h-3" />}
            {data.sentiment_summary.overall_tone === 'neutral' && <Minus className="w-3 h-3" />}
            Overall: {data.sentiment_summary.overall_tone}
          </span>
        </div>
      </div>

      {/* Articles */}
      <div className="p-6">
        <div className="space-y-4">
          {data.articles.map((article, index) => (
            <div
              key={index}
              className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors"
            >
              {/* Article Header */}
              <div className="flex items-start justify-between gap-3 mb-2">
                <h3 className="font-medium text-gray-900 leading-snug flex-1">
                  <a
                    href={article.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="hover:text-blue-600 hover:underline"
                  >
                    {article.title}
                  </a>
                </h3>
                <ExternalLink className="w-4 h-4 text-gray-400 flex-shrink-0 mt-0.5" />
              </div>

              {/* Article Meta */}
              <div className="flex items-center gap-4 mb-3 text-xs text-gray-500">
                <div className="flex items-center gap-1">
                  <span className="font-medium">{article.source}</span>
                </div>
                <div className="flex items-center gap-1">
                  <Calendar className="w-3 h-3" />
                  <span>{new Date(article.published_date).toLocaleDateString()}</span>
                </div>
                <div className="flex items-center gap-1">
                  <span>Relevance:</span>
                  <div className="flex">{getRelevanceStars(article.relevance_score)}</div>
                </div>
              </div>

              {/* Article Snippet */}
              <p
                className="text-sm text-gray-700 mb-3 leading-relaxed"
                dangerouslySetInnerHTML={{
                  __html: highlightPortfolioTickers(article.snippet, portfolioTickers)
                }}
              />

              {/* Article Footer */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  {/* Portfolio Tickers */}
                  {article.portfolio_tickers.length > 0 && (
                    <div className="flex items-center gap-1">
                      <span className="text-xs text-gray-500">Affects:</span>
                      {article.portfolio_tickers.map(ticker => (
                        <span
                          key={ticker}
                          className="inline-block bg-blue-100 text-blue-800 text-xs font-mono font-semibold px-1.5 py-0.5 rounded"
                        >
                          {ticker}
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                {/* Sentiment Badge */}
                <div className={`flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium border ${getSentimentColor(article.sentiment)}`}>
                  {getSentimentIcon(article.sentiment)}
                  <span className="capitalize">{article.sentiment}</span>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Portfolio Relevance Summary */}
        <div className="mt-6 p-4 bg-indigo-50 rounded-lg border border-indigo-200">
          <h4 className="font-medium text-indigo-900 mb-2">Portfolio Relevance</h4>
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <div className="text-lg font-bold text-indigo-900">
                {data.portfolio_relevance.high}
              </div>
              <div className="text-xs text-indigo-700">High Relevance</div>
            </div>
            <div>
              <div className="text-lg font-bold text-indigo-900">
                {data.portfolio_relevance.medium}
              </div>
              <div className="text-xs text-indigo-700">Medium Relevance</div>
            </div>
            <div>
              <div className="text-lg font-bold text-indigo-900">
                {data.portfolio_relevance.low}
              </div>
              <div className="text-xs text-indigo-700">Low Relevance</div>
            </div>
          </div>
          <div className="mt-3 text-center">
            <span className="text-sm text-indigo-800">
              Coverage Score: {Math.round(data.portfolio_relevance.coverage_score * 100)}%
            </span>
          </div>
        </div>

        {/* Search Metadata */}
        {data.search_metadata && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <div className="text-xs text-gray-500 space-y-1">
              <p><span className="font-medium">Search query:</span> {data.search_metadata.query_used}</p>
              <p><span className="font-medium">Search time:</span> {data.search_metadata.search_time_ms}ms</p>
              {data.search_metadata.filters_applied.length > 0 && (
                <p>
                  <span className="font-medium">Filters:</span> {data.search_metadata.filters_applied.join(', ')}
                </p>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}