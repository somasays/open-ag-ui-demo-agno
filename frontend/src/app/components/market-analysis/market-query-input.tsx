"use client"

import { useState, useRef, useEffect } from 'react';
import { MarketQueryInputProps } from '@/types/market-analysis';
import { Send, X, Clock, Lightbulb } from 'lucide-react';

export function MarketQueryInput({
  onSubmit,
  isAnalyzing,
  portfolioContext,
  suggestedQueries = []
}: MarketQueryInputProps) {
  const [query, setQuery] = useState('');
  const [showSuggestions, setShowSuggestions] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [query]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim() && !isAnalyzing) {
      onSubmit(query.trim());
      setQuery('');
      setShowSuggestions(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    setQuery(suggestion);
    setShowSuggestions(false);
    onSubmit(suggestion);
  };

  const portfolioTickers = portfolioContext.map(p => p.ticker).join(', ');

  return (
    <div className="bg-white rounded-lg border border-gray-200 shadow-sm">
      {/* Portfolio Context Bar */}
      {portfolioContext.length > 0 && (
        <div className="px-4 py-2 bg-gray-50 border-b border-gray-200 rounded-t-lg">
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <span className="font-medium">Portfolio context:</span>
            <span className="font-mono text-xs bg-gray-100 px-2 py-1 rounded">
              {portfolioTickers}
            </span>
          </div>
        </div>
      )}

      {/* Query Input Form */}
      <form onSubmit={handleSubmit} className="p-4">
        <div className="relative">
          <textarea
            ref={textareaRef}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about market conditions affecting your portfolio...

Examples:
• How will Fed rate changes impact my tech stocks?
• What economic headwinds affect my portfolio?
• Is there sector rotation happening in my holdings?"
            className="w-full resize-none border-0 focus:ring-0 focus:outline-none text-gray-900 placeholder-gray-500 text-base leading-relaxed"
            rows={3}
            disabled={isAnalyzing}
            maxLength={500}
          />

          {/* Character count */}
          <div className="absolute bottom-2 right-2 text-xs text-gray-400">
            {query.length}/500
          </div>
        </div>

        {/* Action Bar */}
        <div className="flex items-center justify-between mt-4 pt-3 border-t border-gray-100">
          <div className="flex items-center gap-2">
            {/* Suggestions Toggle */}
            <button
              type="button"
              onClick={() => setShowSuggestions(!showSuggestions)}
              className={`flex items-center gap-1 px-3 py-1.5 text-sm rounded-md transition-colors ${
                showSuggestions
                  ? 'bg-blue-100 text-blue-700'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
              disabled={isAnalyzing}
            >
              <Lightbulb className="w-4 h-4" />
              Suggestions
            </button>

            {/* Analysis Status */}
            {isAnalyzing && (
              <div className="flex items-center gap-2 text-sm text-amber-600">
                <Clock className="w-4 h-4 animate-spin" />
                <span>Analyzing...</span>
              </div>
            )}
          </div>

          {/* Submit Button */}
          <div className="flex items-center gap-2">
            {query.trim() && (
              <button
                type="button"
                onClick={() => setQuery('')}
                className="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-md transition-colors"
                disabled={isAnalyzing}
              >
                <X className="w-4 h-4" />
              </button>
            )}

            <button
              type="submit"
              disabled={!query.trim() || isAnalyzing}
              className={`flex items-center gap-2 px-4 py-2 rounded-md font-medium text-sm transition-colors ${
                query.trim() && !isAnalyzing
                  ? 'bg-blue-600 text-white hover:bg-blue-700'
                  : 'bg-gray-100 text-gray-400 cursor-not-allowed'
              }`}
            >
              <Send className="w-4 h-4" />
              {isAnalyzing ? 'Analyzing...' : 'Analyze'}
            </button>
          </div>
        </div>
      </form>

      {/* Suggested Queries */}
      {showSuggestions && suggestedQueries.length > 0 && (
        <div className="border-t border-gray-200 p-4 bg-gray-50 rounded-b-lg">
          <div className="mb-2">
            <span className="text-sm font-medium text-gray-700">Suggested Questions:</span>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {suggestedQueries.map((suggestion, index) => (
              <button
                key={index}
                onClick={() => handleSuggestionClick(suggestion)}
                className="text-left p-3 text-sm bg-white border border-gray-200 rounded-md hover:bg-blue-50 hover:border-blue-300 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                disabled={isAnalyzing}
              >
                <div className="font-medium text-gray-900 mb-1">
                  {suggestion}
                </div>
                <div className="text-xs text-gray-500">
                  Click to analyze
                </div>
              </button>
            ))}
          </div>

          {/* Portfolio-specific suggestions */}
          {portfolioContext.length > 0 && (
            <div className="mt-3 pt-3 border-t border-gray-200">
              <span className="text-xs font-medium text-gray-600 mb-2 block">
                Based on your {portfolioTickers}:
              </span>
              <div className="space-y-1">
                <button
                  onClick={() => handleSuggestionClick(`How do current economic indicators affect ${portfolioTickers}?`)}
                  className="block w-full text-left p-2 text-xs bg-blue-50 text-blue-700 rounded border border-blue-200 hover:bg-blue-100 transition-colors disabled:opacity-50"
                  disabled={isAnalyzing}
                >
                  Economic impact on your specific holdings
                </button>
                <button
                  onClick={() => handleSuggestionClick(`What's the market sentiment for ${portfolioTickers.split(', ')[0]} sector?`)}
                  className="block w-full text-left p-2 text-xs bg-green-50 text-green-700 rounded border border-green-200 hover:bg-green-100 transition-colors disabled:opacity-50"
                  disabled={isAnalyzing}
                >
                  Sector sentiment analysis
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}