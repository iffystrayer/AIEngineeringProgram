import { useParams, useNavigate } from 'react-router-dom'
import { useSession } from '../../hooks/useSession'
import { ProgressDisplay } from '../ProgressDisplay'

export default function SessionDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { sessions, isLoading } = useSession()

  const session = sessions?.find((s) => s.id === id)

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    )
  }

  if (!session) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
        <h2 className="text-lg font-semibold text-red-900 mb-2">
          Session Not Found
        </h2>
        <p className="text-red-700 mb-4">
          The session you're looking for doesn't exist or has been deleted.
        </p>
        <button
          onClick={() => navigate('/sessions')}
          className="text-indigo-600 hover:text-indigo-800 font-medium"
        >
          Back to Sessions
        </button>
      </div>
    )
  }

  const stages = [
    { id: 1, name: 'Problem Statement', status: 'completed' },
    { id: 2, name: 'Metric Alignment', status: 'in_progress' },
    { id: 3, name: 'Data Quality', status: 'pending' },
    { id: 4, name: 'Impact Assessment', status: 'pending' },
    { id: 5, name: 'Governance', status: 'pending' },
  ]

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            {session.projectName}
          </h1>
          <p className="text-gray-600">
            Complete the 5-stage questionnaire to generate your data governance
            charter
          </p>
        </div>
        <button
          onClick={() => navigate('/sessions')}
          className="text-gray-600 hover:text-gray-900"
        >
          ← Back
        </button>
      </div>

      {/* Progress Overview */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Progress</h2>
        <ProgressDisplay
          currentStage={session.currentStage}
          totalStages={session.totalStages}
        />
        <p className="text-sm text-gray-600 mt-4">
          Stage {session.currentStage} of {session.totalStages}
        </p>
      </div>

      {/* Stage Navigation */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Stages</h2>
        </div>

        <div className="divide-y divide-gray-200">
          {stages.map((stage, index) => (
            <div
              key={stage.id}
              className="px-6 py-4 hover:bg-gray-50 transition-colors"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  {/* Stage Number */}
                  <div
                    className={`flex items-center justify-center w-10 h-10 rounded-full font-bold text-sm ${
                      stage.status === 'completed'
                        ? 'bg-green-100 text-green-700'
                        : stage.status === 'in_progress'
                          ? 'bg-indigo-100 text-indigo-700'
                          : 'bg-gray-100 text-gray-700'
                    }`}
                  >
                    {stage.status === 'completed' ? '✓' : index + 1}
                  </div>

                  {/* Stage Info */}
                  <div>
                    <h3 className="font-medium text-gray-900">
                      Stage {stage.id}: {stage.name}
                    </h3>
                    <p className="text-sm text-gray-600 mt-1">
                      {stage.status === 'completed' && 'Completed'}
                      {stage.status === 'in_progress' && 'In Progress'}
                      {stage.status === 'pending' && 'Not Started'}
                    </p>
                  </div>
                </div>

                {/* Action Button */}
                {session.currentStage >= stage.id && (
                  <button
                    onClick={() =>
                      navigate(`/sessions/${session.id}/stage/${stage.id}`)
                    }
                    className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-lg transition-colors"
                  >
                    {stage.status === 'completed'
                      ? 'Review'
                      : stage.status === 'in_progress'
                        ? 'Continue'
                        : 'Start'}
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Session Info */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-4">
            Status
          </h3>
          <p className="text-2xl font-bold text-gray-900 capitalize">
            {session.status === 'completed' ? '✓ Completed' : '⏳ In Progress'}
          </p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-4">
            Created
          </h3>
          <p className="text-2xl font-bold text-gray-900">
            {new Date(session.createdAt).toLocaleDateString()}
          </p>
        </div>
      </div>

      {/* Charter Section - if completed */}
      {session.status === 'completed' && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-green-900 mb-2">
            Questionnaire Complete! 🎉
          </h2>
          <p className="text-green-700 mb-4">
            Your data governance charter has been generated. You can now review
            and download it.
          </p>
          <button
            onClick={() => navigate(`/charter/${session.id}`)}
            className="bg-green-600 hover:bg-green-700 text-white font-medium py-2 px-6 rounded-lg transition-colors"
          >
            View Charter
          </button>
        </div>
      )}
    </div>
  )
}
