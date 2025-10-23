import { useState, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { useSession } from '../../hooks/useSession'
import { format } from 'date-fns'

type FilterStatus = 'all' | 'in_progress' | 'completed'

const ITEMS_PER_PAGE = 10

export default function SessionsList() {
  const navigate = useNavigate()
  const { sessions, isLoading, deleteSession } = useSession()
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState<FilterStatus>('all')
  const [currentPage, setCurrentPage] = useState(1)

  // Filter and search logic
  const filteredSessions = useMemo(() => {
    return (sessions || [])
      .filter((session) => {
        const matchesSearch = session.projectName
          .toLowerCase()
          .includes(searchQuery.toLowerCase())
        const matchesStatus =
          statusFilter === 'all' || session.status === statusFilter
        return matchesSearch && matchesStatus
      })
      .sort(
        (a, b) =>
          new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
      )
  }, [sessions, searchQuery, statusFilter])

  // Pagination logic
  const totalPages = Math.ceil(filteredSessions.length / ITEMS_PER_PAGE)
  const startIndex = (currentPage - 1) * ITEMS_PER_PAGE
  const paginatedSessions = filteredSessions.slice(
    startIndex,
    startIndex + ITEMS_PER_PAGE
  )

  const handleDelete = async (sessionId: string) => {
    if (
      window.confirm(
        'Are you sure you want to delete this session? This action cannot be undone.'
      )
    ) {
      await deleteSession(sessionId)
      if (currentPage > totalPages) {
        setCurrentPage(Math.max(1, totalPages))
      }
    }
  }

  const handlePageChange = (page: number) => {
    setCurrentPage(Math.max(1, Math.min(page, totalPages)))
  }

  const getStatusColor = (status: string) => {
    return status === 'completed'
      ? 'bg-green-100 text-green-800'
      : 'bg-yellow-100 text-yellow-800'
  }

  const getStatusIcon = (status: string) => {
    return status === 'completed' ? '✓' : '⏳'
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">All Projects</h1>
          <p className="text-gray-600 mt-1">
            Manage and track all your data governance initiatives
          </p>
        </div>
        <button
          onClick={() => navigate('/')}
          className="bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2 px-6 rounded-lg transition-colors"
        >
          New Project
        </button>
      </div>

      {/* Search and Filter Controls */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Search Input */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Search Projects
            </label>
            <input
              type="text"
              placeholder="Search by project name..."
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value)
                setCurrentPage(1)
              }}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition"
            />
          </div>

          {/* Status Filter */}
          <div>
            <label
              htmlFor="status-filter"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              Filter by Status
            </label>
            <select
              id="status-filter"
              value={statusFilter}
              onChange={(e) => {
                setStatusFilter(e.target.value as FilterStatus)
                setCurrentPage(1)
              }}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition"
            >
              <option value="all">All Statuses</option>
              <option value="in_progress">In Progress</option>
              <option value="completed">Completed</option>
            </select>
          </div>
        </div>

        {/* Results Summary */}
        <div className="mt-4 text-sm text-gray-600">
          Showing {filteredSessions.length === 0 ? 0 : startIndex + 1} to{' '}
          {Math.min(startIndex + ITEMS_PER_PAGE, filteredSessions.length)} of{' '}
          {filteredSessions.length} projects
        </div>
      </div>

      {/* Sessions Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        {isLoading ? (
          <div className="px-6 py-8 text-center text-gray-500">
            Loading projects...
          </div>
        ) : paginatedSessions.length > 0 ? (
          <>
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
                      Created
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
                  {paginatedSessions.map((session) => (
                    <tr
                      key={session.id}
                      className="hover:bg-gray-50 transition-colors"
                    >
                      <td className="px-6 py-4 text-sm font-medium text-gray-900">
                        {session.projectName}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-600">
                        <div className="flex items-center space-x-2">
                          <div className="flex-1 w-20 bg-gray-200 rounded-full h-2">
                            <div
                              className="bg-indigo-600 h-2 rounded-full"
                              style={{
                                width: `${(session.currentStage / session.totalStages) * 100}%`,
                              }}
                            />
                          </div>
                          <span className="text-xs font-semibold text-gray-700 whitespace-nowrap">
                            {session.currentStage}/{session.totalStages}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4 text-sm">
                        <span
                          className={`inline-block px-3 py-1 rounded-full text-xs font-semibold ${getStatusColor(session.status)}`}
                        >
                          {getStatusIcon(session.status)}{' '}
                          {session.status === 'completed'
                            ? 'Completed'
                            : 'In Progress'}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-600">
                        {format(new Date(session.createdAt), 'MMM d, yyyy')}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-600">
                        {format(new Date(session.updatedAt), 'MMM d, yyyy')}
                      </td>
                      <td className="px-6 py-4 text-sm">
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={() => navigate(`/sessions/${session.id}`)}
                            className="text-indigo-600 hover:text-indigo-800 font-medium"
                          >
                            View
                          </button>
                          <span className="text-gray-300">|</span>
                          <button
                            onClick={() => handleDelete(session.id)}
                            className="text-red-600 hover:text-red-800 font-medium"
                          >
                            Delete
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination Controls */}
            {totalPages > 1 && (
              <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
                <button
                  onClick={() => handlePageChange(currentPage - 1)}
                  disabled={currentPage === 1}
                  className="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition"
                >
                  Previous
                </button>

                <div className="flex items-center space-x-2">
                  {Array.from({ length: totalPages }, (_, i) => i + 1).map(
                    (page) => (
                      <button
                        key={page}
                        onClick={() => handlePageChange(page)}
                        className={`px-3 py-1 rounded text-sm font-medium transition ${
                          page === currentPage
                            ? 'bg-indigo-600 text-white'
                            : 'border border-gray-300 text-gray-700 hover:bg-gray-50'
                        }`}
                      >
                        {page}
                      </button>
                    )
                  )}
                </div>

                <button
                  onClick={() => handlePageChange(currentPage + 1)}
                  disabled={currentPage === totalPages}
                  className="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition"
                >
                  Next
                </button>
              </div>
            )}
          </>
        ) : (
          <div className="px-6 py-12 text-center">
            <p className="text-gray-500 mb-4">No projects found</p>
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
