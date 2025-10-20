import React from 'react'

export interface ProgressData {
  session_id: string
  current_stage: number
  questions_answered: number
  charter_status: string
  total_questions?: number
  started_at?: string
}

interface ProgressDisplayProps {
  progress: ProgressData | null
}

const STAGES = [
  'Business Translation',
  'Value Quantification',
  'Data Feasibility',
  'User Centricity',
  'Ethical Governance',
]

const getStatusColor = (status: string): string => {
  switch (status) {
    case 'completed':
      return 'bg-green-100 text-green-800'
    case 'generating':
      return 'bg-blue-100 text-blue-800'
    case 'error':
      return 'bg-red-100 text-red-800'
    case 'pending':
      return 'bg-yellow-100 text-yellow-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

const getStatusLabel = (status: string): string => {
  switch (status) {
    case 'completed':
      return 'Completed'
    case 'generating':
      return 'Generating'
    case 'error':
      return 'Error'
    case 'pending':
      return 'Pending'
    default:
      return status
  }
}

/**
 * ProgressDisplay Component
 * 
 * Displays real-time progress of the questionnaire and charter generation.
 * Shows current stage, questions answered, and charter status.
 */
export const ProgressDisplay: React.FC<ProgressDisplayProps> = ({ progress }) => {
  if (!progress) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <p className="text-yellow-800">No progress data available</p>
      </div>
    )
  }

  const progressPercentage = progress.total_questions
    ? Math.round((progress.questions_answered / progress.total_questions) * 100)
    : 0

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-xl font-bold text-gray-900">Progress Tracking</h3>
        <div className={`badge px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(progress.charter_status)}`}>
          {getStatusLabel(progress.charter_status)}
        </div>
      </div>

      {/* Questions Progress */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <label className="text-sm font-medium text-gray-700">
            Questions Answered
          </label>
          <span className="text-sm font-semibold text-gray-900">
            {progress.questions_answered} of {progress.total_questions || 20}
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            role="progressbar"
            aria-valuenow={progressPercentage}
            aria-valuemin={0}
            aria-valuemax={100}
            className="bg-indigo-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${progressPercentage}%` }}
          />
        </div>
      </div>

      {/* Current Stage */}
      <div>
        <label className="text-sm font-medium text-gray-700 block mb-3">
          Current Stage: Stage {progress.current_stage}
        </label>
        <div className="flex items-center justify-between">
          {STAGES.map((stage, index) => {
            const stageNumber = index + 1
            let stageClass = 'bg-gray-300'
            
            if (stageNumber < progress.current_stage) {
              stageClass = 'bg-green-600'
            } else if (stageNumber === progress.current_stage) {
              stageClass = 'bg-indigo-600'
            }

            return (
              <div key={stageNumber} className="flex flex-col items-center">
                <div
                  data-testid={`stage-${stageNumber}`}
                  className={`w-10 h-10 rounded-full flex items-center justify-center text-white font-bold mb-2 transition-all ${stageClass}`}
                >
                  {stageNumber}
                </div>
                <span className="text-xs text-gray-600 text-center max-w-[80px]">
                  {stage.split(' ')[0]}
                </span>
              </div>
            )
          })}
        </div>
      </div>

      {/* Stage Details */}
      <div className="bg-gray-50 rounded-lg p-4">
        <h4 className="font-semibold text-gray-900 mb-2">
          {STAGES[progress.current_stage - 1]}
        </h4>
        <p className="text-sm text-gray-600">
          {progress.questions_answered} questions answered
        </p>
      </div>

      {/* Charter Status */}
      {progress.charter_status === 'generating' && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <div className="animate-spin">
              <svg
                className="w-5 h-5 text-blue-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                />
              </svg>
            </div>
            <p className="text-sm text-blue-800">
              Generating project charter...
            </p>
          </div>
        </div>
      )}

      {progress.charter_status === 'completed' && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <svg
              className="w-5 h-5 text-green-600"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                clipRule="evenodd"
              />
            </svg>
            <p className="text-sm text-green-800">
              Project charter generated successfully!
            </p>
          </div>
        </div>
      )}

      {progress.charter_status === 'error' && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <svg
              className="w-5 h-5 text-red-600"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                clipRule="evenodd"
              />
            </svg>
            <p className="text-sm text-red-800">
              Error generating charter. Please try again.
            </p>
          </div>
        </div>
      )}
    </div>
  )
}

export default ProgressDisplay

