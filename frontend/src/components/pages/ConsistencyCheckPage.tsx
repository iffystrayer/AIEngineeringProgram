import { useParams, useNavigate } from 'react-router-dom'
import ConsistencyChecker from '../ConsistencyChecker'

export default function ConsistencyCheckPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()

  if (!id) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
        <h2 className="text-lg font-semibold text-red-900 mb-2">
          Session Not Found
        </h2>
        <button
          onClick={() => navigate('/sessions')}
          className="text-indigo-600 hover:text-indigo-800 font-medium"
        >
          Back to Sessions
        </button>
      </div>
    )
  }

  return (
    <div>
      <ConsistencyChecker sessionId={id} />
    </div>
  )
}
