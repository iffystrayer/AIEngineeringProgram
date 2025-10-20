import React from 'react'

interface LandingPageProps {
  onStartNew?: () => void
  onResume?: () => void
}

/**
 * LandingPage Component
 * 
 * Main entry point for the U-AIP Scoping Assistant.
 * Allows users to start a new questionnaire or resume an existing session.
 */
export const LandingPage: React.FC<LandingPageProps> = ({
  onStartNew,
  onResume,
}) => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <h1 className="text-3xl font-bold text-gray-900">
            U-AIP Scoping Assistant
          </h1>
          <p className="text-gray-600 mt-2">
            Universal AI Project Scoping and Framing Protocol
          </p>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Start New Session Card */}
          <div className="bg-white rounded-lg shadow-lg p-8 hover:shadow-xl transition-shadow">
            <div className="flex items-center justify-center w-12 h-12 rounded-md bg-indigo-500 text-white mb-4">
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
                  d="M12 4v16m8-8H4"
                />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              Start New Project
            </h2>
            <p className="text-gray-600 mb-6">
              Begin a new AI project evaluation. Answer questions across 5 stages
              to assess feasibility and generate a comprehensive project charter.
            </p>
            <button
              onClick={onStartNew}
              className="w-full bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 transition-colors font-medium"
              data-testid="start-new-button"
            >
              Start New Questionnaire
            </button>
          </div>

          {/* Resume Session Card */}
          <div className="bg-white rounded-lg shadow-lg p-8 hover:shadow-xl transition-shadow">
            <div className="flex items-center justify-center w-12 h-12 rounded-md bg-green-500 text-white mb-4">
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
                  d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              Resume Session
            </h2>
            <p className="text-gray-600 mb-6">
              Continue working on an existing project evaluation. Your progress
              is automatically saved.
            </p>
            <button
              onClick={onResume}
              className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 transition-colors font-medium"
              data-testid="resume-button"
            >
              View Sessions
            </button>
          </div>
        </div>

        {/* Features Section */}
        <div className="mt-12">
          <h3 className="text-2xl font-bold text-gray-900 mb-8">
            5-Stage Evaluation Process
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            {[
              { num: 1, title: 'Business Translation', desc: 'Define the problem' },
              { num: 2, title: 'Value Quantification', desc: 'Measure impact' },
              { num: 3, title: 'Data Feasibility', desc: 'Assess data' },
              { num: 4, title: 'User Centricity', desc: 'Consider users' },
              { num: 5, title: 'Ethical Governance', desc: 'Ensure ethics' },
            ].map((stage) => (
              <div
                key={stage.num}
                className="bg-white rounded-lg shadow p-4 text-center"
              >
                <div className="flex items-center justify-center w-10 h-10 rounded-full bg-indigo-100 text-indigo-600 font-bold mx-auto mb-2">
                  {stage.num}
                </div>
                <h4 className="font-semibold text-gray-900 text-sm mb-1">
                  {stage.title}
                </h4>
                <p className="text-xs text-gray-600">{stage.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  )
}

export default LandingPage

