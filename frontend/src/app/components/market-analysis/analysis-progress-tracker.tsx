"use client"

import { useState, useEffect } from 'react';
import { AnalysisProgressTrackerProps } from '@/types/market-analysis';
import { CheckCircle, Clock, AlertCircle, X, Loader2 } from 'lucide-react';

interface AnalysisStep {
  id: string;
  name: string;
  description: string;
  status: 'pending' | 'processing' | 'completed' | 'error';
  duration?: number;
}

export function AnalysisProgressTracker({
  toolLogs,
  onAbort,
  estimatedTimeRemaining,
  currentStep
}: AnalysisProgressTrackerProps) {
  const [timeElapsed, setTimeElapsed] = useState(0);
  const [showDetails, setShowDetails] = useState(false);

  // Update elapsed time every second
  useEffect(() => {
    const interval = setInterval(() => {
      setTimeElapsed(prev => prev + 1);
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  // Define analysis steps
  const analysisSteps: AnalysisStep[] = [
    {
      id: 'query-analysis',
      name: 'Query Analysis',
      description: 'Parsing query and identifying required data sources',
      status: 'completed'
    },
    {
      id: 'economic-data',
      name: 'Economic Data',
      description: 'Fetching FRED economic indicators and market data',
      status: toolLogs.some(log => log.message.includes('economic') && log.status === 'completed')
        ? 'completed'
        : toolLogs.some(log => log.message.includes('economic') && log.status === 'processing')
        ? 'processing'
        : 'pending'
    },
    {
      id: 'news-analysis',
      name: 'News Analysis',
      description: 'Searching relevant market news and sentiment analysis',
      status: toolLogs.some(log => log.message.includes('news') && log.status === 'completed')
        ? 'completed'
        : toolLogs.some(log => log.message.includes('news') && log.status === 'processing')
        ? 'processing'
        : 'pending'
    },
    {
      id: 'portfolio-impact',
      name: 'Portfolio Impact',
      description: 'Analyzing impact on specific holdings and generating insights',
      status: toolLogs.some(log => log.message.includes('impact') && log.status === 'completed')
        ? 'completed'
        : toolLogs.some(log => log.message.includes('impact') && log.status === 'processing')
        ? 'processing'
        : 'pending'
    }
  ];

  const completedSteps = analysisSteps.filter(step => step.status === 'completed').length;
  const totalSteps = analysisSteps.length;
  const progressPercent = (completedSteps / totalSteps) * 100;

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getStepIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-600" />;
      case 'processing':
        return <Loader2 className="w-5 h-5 text-blue-600 animate-spin" />;
      case 'error':
        return <AlertCircle className="w-5 h-5 text-red-600" />;
      default:
        return <Clock className="w-5 h-5 text-gray-400" />;
    }
  };

  const getStepTextColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-green-800';
      case 'processing':
        return 'text-blue-800 font-semibold';
      case 'error':
        return 'text-red-800';
      default:
        return 'text-gray-600';
    }
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
      {/* Progress Header */}
      <div className="p-4 bg-gradient-to-r from-blue-50 to-indigo-50 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-semibold text-gray-900 mb-1">
              Analyzing Market Conditions
            </h3>
            <p className="text-sm text-gray-600">
              Step {completedSteps + 1} of {totalSteps} • {formatTime(timeElapsed)} elapsed
            </p>
          </div>

          <div className="flex items-center gap-3">
            {/* Progress Circle */}
            <div className="relative w-12 h-12">
              <svg className="w-12 h-12 transform -rotate-90" viewBox="0 0 36 36">
                <path
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                  fill="none"
                  stroke="#E5E7EB"
                  strokeWidth="2"
                />
                <path
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                  fill="none"
                  stroke="#3B82F6"
                  strokeWidth="2"
                  strokeDasharray={`${progressPercent}, 100`}
                  className="transition-all duration-300 ease-in-out"
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="text-xs font-semibold text-gray-700">
                  {Math.round(progressPercent)}%
                </span>
              </div>
            </div>

            {/* Abort Button */}
            <button
              onClick={onAbort}
              className="flex items-center gap-1 px-3 py-1.5 text-sm text-red-600 hover:text-red-700 hover:bg-red-50 rounded-md transition-colors"
              title="Abort analysis"
            >
              <X className="w-4 h-4" />
              Abort
            </button>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mt-3">
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="h-2 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full transition-all duration-300 ease-out"
              style={{ width: `${progressPercent}%` }}
            />
          </div>
        </div>

        {/* Time Estimate */}
        <div className="mt-2 flex items-center justify-between text-xs text-gray-600">
          <span>
            Estimated completion: {estimatedTimeRemaining > timeElapsed ? formatTime(estimatedTimeRemaining - timeElapsed) : 'Almost done'}
          </span>
          <button
            onClick={() => setShowDetails(!showDetails)}
            className="text-blue-600 hover:text-blue-700 font-medium"
          >
            {showDetails ? 'Hide details' : 'Show details'}
          </button>
        </div>
      </div>

      {/* Progress Steps */}
      <div className="p-4">
        <div className="space-y-3">
          {analysisSteps.map((step, index) => (
            <div
              key={step.id}
              className={`flex items-start gap-3 p-3 rounded-lg transition-colors ${
                step.status === 'processing'
                  ? 'bg-blue-50 border border-blue-200'
                  : step.status === 'completed'
                  ? 'bg-green-50 border border-green-200'
                  : 'bg-gray-50 border border-gray-200'
              }`}
            >
              {/* Step Icon */}
              <div className="flex-shrink-0 mt-0.5">
                {getStepIcon(step.status)}
              </div>

              {/* Step Content */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <h4 className={`font-medium ${getStepTextColor(step.status)}`}>
                    {step.name}
                  </h4>
                  {step.status === 'processing' && (
                    <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                      In Progress
                    </span>
                  )}
                </div>
                <p className="text-sm text-gray-600 mt-1">
                  {step.description}
                </p>

                {/* Duration if completed */}
                {step.status === 'completed' && step.duration && (
                  <p className="text-xs text-gray-500 mt-1">
                    Completed in {step.duration}s
                  </p>
                )}
              </div>

              {/* Step Number */}
              <div className="flex-shrink-0">
                <span className={`inline-flex items-center justify-center w-6 h-6 rounded-full text-xs font-medium ${
                  step.status === 'completed'
                    ? 'bg-green-100 text-green-800'
                    : step.status === 'processing'
                    ? 'bg-blue-100 text-blue-800'
                    : 'bg-gray-100 text-gray-600'
                }`}>
                  {index + 1}
                </span>
              </div>
            </div>
          ))}
        </div>

        {/* Detailed Logs */}
        {showDetails && toolLogs.length > 0 && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <h4 className="font-medium text-gray-900 mb-2">Detailed Progress</h4>
            <div className="space-y-2 max-h-40 overflow-y-auto">
              {toolLogs.map((log) => (
                <div
                  key={log.id}
                  className={`flex items-center gap-2 text-sm p-2 rounded ${
                    log.status === 'processing'
                      ? 'bg-yellow-50 text-yellow-800'
                      : 'bg-green-50 text-green-800'
                  }`}
                >
                  {log.status === 'processing' ? (
                    <div className="relative flex h-3 w-3">
                      <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-yellow-400 opacity-75"></span>
                      <span className="relative inline-flex rounded-full h-3 w-3 bg-yellow-500"></span>
                    </div>
                  ) : (
                    <CheckCircle className="w-3 h-3 text-green-600" />
                  )}
                  <span className="font-mono text-xs">{log.message}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Performance Stats */}
        {showDetails && (
          <div className="mt-4 pt-4 border-t border-gray-200 grid grid-cols-3 gap-4 text-center">
            <div>
              <div className="text-lg font-semibold text-gray-900">{completedSteps}</div>
              <div className="text-xs text-gray-600">Completed</div>
            </div>
            <div>
              <div className="text-lg font-semibold text-gray-900">{formatTime(timeElapsed)}</div>
              <div className="text-xs text-gray-600">Elapsed</div>
            </div>
            <div>
              <div className="text-lg font-semibold text-gray-900">
                {estimatedTimeRemaining > timeElapsed ? formatTime(estimatedTimeRemaining - timeElapsed) : '0:00'}
              </div>
              <div className="text-xs text-gray-600">Remaining</div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}