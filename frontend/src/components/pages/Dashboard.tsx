import { useNavigate } from 'react-router-dom'
import { useSession } from '../../hooks/useSession'
import { ProgressDisplay } from '../ProgressDisplay'
import { format } from 'date-fns'

export default function Dashboard() {
  const navigate = useNavigate()
  const { sessions, isLoading } = useSession()

  const recentSessions = sessions
    ?.sort(
      (a, b) =>
        new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
    )
    .slice(0, 5)

  const completedCount = sessions?.filter(
    (s) => s.status === 'completed'
  ).length

  const inProgressCount = sessions?.filter(
    (s) => s.status === 'in_progress'
  ).length

  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <div className="bg-gradient-to-r from-indigo-600 to-indigo-700 rounded-lg p-8 text-white shadow-lg">
        <h1 className="text-4xl font-bold mb-2">Welcome back!</h1>
        <p className="text-indigo-100">
          Track and manage your data governance initiatives
        </p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg p-6 shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm font-medium">Total Projects</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">
                {sessions?.length || 0}
              </p>
            </div>
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <span className="text-2xl">📊</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg p-6 shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm font-medium">In Progress</p>
              <p className="text-3xl font-bold text-yellow-600 mt-2">
                {inProgressCount || 0}
              </p>
            </div>
            <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center">
              <span className="text-2xl">⏳</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg p-6 shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm font-medium">Completed</p>
              <p className="text-3xl font-bold text-green-600 mt-2">
                {completedCount || 0}
              </p>
            </div>
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <span className="text-2xl">✅</span>
            </div>
          </div>
        </div>
      </div>

      {/* New Session CTA */}
      <div className="bg-white rounded-lg p-6 shadow">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          Start a New Project
        </h2>
        <p className="text-gray-600 mb-6">
          Create a new data governance charter for your organization
        </p>
        <button
          onClick={() => navigate('/')}
          className="bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2 px-6 rounded-lg transition-colors"
        >
          New Session
        </button>
      </div>

      {/* Recent Sessions */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">
            Recent Projects
          </h2>
        </div>

        {isLoading ? (
          <div className="px-6 py-8 text-center text-gray-500">
            Loading projects...
          </div>
        ) : recentSessions && recentSessions.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                    Project Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                    Progress
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                    Last Updated
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {recentSessions.map((session) => (
                  <tr
                    key={session.id}
                    className="hover:bg-gray-50 transition-colors"
                  >
                    <td className="px-6 py-4 text-sm font-medium text-gray-900">
                      {session.projectName}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      <div className="flex items-center space-x-2">
                        <div className="flex-1 w-24 bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-indigo-600 h-2 rounded-full"
                            style={{
                              width: `${(session.currentStage / session.totalStages) * 100}%`,
                            }}
                          />
                        </div>
                        <span className="text-xs font-semibold text-gray-700">
                          {session.currentStage}/{session.totalStages}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm">
                      <span
                        className={`inline-block px-3 py-1 rounded-full text-xs font-semibold ${
                          session.status === 'completed'
                            ? 'bg-green-100 text-green-800'
                            : 'bg-yellow-100 text-yellow-800'
                        }`}
                      >
                        {session.status === 'completed' ? '✓ Completed' : '⏳ In Progress'}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {format(new Date(session.updatedAt), 'MMM d, yyyy')}
                    </td>
                    <td className="px-6 py-4 text-sm">
                      <button
                        onClick={() => navigate(`/sessions/${session.id}`)}
                        className="text-indigo-600 hover:text-indigo-800 font-medium"
                      >
                        View →
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="px-6 py-8 text-center text-gray-500">
            <p className="mb-4">No projects yet</p>
            <button
              onClick={() => navigate('/')}
              className="text-indigo-600 hover:text-indigo-800 font-medium"
            >
              Create your first project
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
