import React from 'react'
import { SessionResponse } from '../services/api'

interface SessionModalProps {
  isOpen: boolean
  sessions: SessionResponse[]
  isLoading?: boolean
  onSelect: (session: SessionResponse) => void
  onClose: () => void
}

/**
 * SessionModal Component
 * 
 * Displays a modal with a list of user sessions for resuming.
 */
export const SessionModal: React.FC<SessionModalProps> = ({
  isOpen,
  sessions,
  isLoading = false,
  onSelect,
  onClose,
}) => {
  if (!isOpen) {
    return null
  }

  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose()
    }
  }

  return (
    <div
      className="fixed inset-0 z-50 bg-black bg-opacity-50 flex items-center justify-center"
      onClick={handleBackdropClick}
    >
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
          <h2 className="text-2xl font-bold text-gray-900">Select Session</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
            aria-label="Close"
          >
            <svg
              className="w-6 h-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="px-6 py-4">
          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin">
                <svg
                  className="w-8 h-8 text-indigo-600"
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
              <p className="ml-3 text-gray-600">Loading sessions...</p>
            </div>
          ) : sessions.length === 0 ? (
            <div className="text-center py-8">
              <svg
                className="w-12 h-12 text-gray-400 mx-auto mb-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
              <p className="text-gray-600">No sessions found</p>
            </div>
          ) : (
            <div className="space-y-3">
              {sessions.map((session) => (
                <button
                  key={session.session_id}
                  data-testid={`session-item-${session.session_id}`}
                  onClick={() => onSelect(session)}
                  className="w-full text-left p-4 border border-gray-200 rounded-lg hover:border-indigo-500 hover:bg-indigo-50 transition-all"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900">
                        {session.project_name}
                      </h3>
                      {session.description && (
                        <p className="text-sm text-gray-600 mt-1">
                          {session.description}
                        </p>
                      )}
                      <div className="flex items-center space-x-4 mt-2">
                        <span className="text-xs text-gray-500">
                          {new Date(session.created_at || '').toLocaleDateString()}
                        </span>
                        <span className={`text-xs px-2 py-1 rounded-full ${
                          session.status === 'completed'
                            ? 'bg-green-100 text-green-800'
                            : session.status === 'in_progress'
                            ? 'bg-blue-100 text-blue-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}>
                          {session.status}
                        </span>
                      </div>
                    </div>
                    <svg
                      className="w-5 h-5 text-gray-400 ml-4 flex-shrink-0"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M9 5l7 7-7 7"
                      />
                    </svg>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default SessionModal

