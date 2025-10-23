import { useParams, useNavigate } from 'react-router-dom'
import { useState } from 'react'
import { useSession } from '../../hooks/useSession'
import StageForm, { FormField } from '../forms/StageForm'

// Stage configurations
const stageConfigs = [
  {
    id: 1,
    name: 'Problem Statement',
    description:
      'Define the problem your organization is trying to solve and the business context.',
    fields: [
      {
        name: 'problemStatement',
        label: 'What is the core problem you are trying to solve?',
        type: 'textarea' as const,
        required: true,
        helpText: 'Provide a clear and concise description of the problem.',
      },
      {
        name: 'businessContext',
        label: 'What is the business context?',
        type: 'textarea' as const,
        required: true,
        helpText:
          'Explain how this problem affects your organization and stakeholders.',
      },
      {
        name: 'currentApproach',
        label: 'What is your current approach to addressing this?',
        type: 'textarea' as const,
        required: false,
      },
    ],
  },
  {
    id: 2,
    name: 'Metric Alignment',
    description: 'Define key metrics and success criteria for your initiative.',
    fields: [
      {
        name: 'successMetrics',
        label: 'What are your success metrics?',
        type: 'textarea' as const,
        required: true,
        helpText: 'List the metrics you will use to measure success.',
      },
      {
        name: 'targetAudience',
        label: 'Who is your target audience?',
        type: 'textarea' as const,
        required: true,
      },
      {
        name: 'timeline',
        label: 'What is your expected timeline?',
        type: 'text' as const,
        required: false,
        placeholder: 'e.g., 6 months, Q1 2026',
      },
    ],
  },
  {
    id: 3,
    name: 'Data Quality',
    description:
      'Assess data quality requirements and current data landscape.',
    fields: [
      {
        name: 'dataQualityRequirements',
        label:
          'What are your data quality requirements for this initiative?',
        type: 'textarea' as const,
        required: true,
      },
      {
        name: 'currentDataLandscape',
        label: 'Describe your current data landscape',
        type: 'textarea' as const,
        required: true,
        helpText:
          'What data sources do you have? What quality issues exist?',
      },
      {
        name: 'dataGovernanceMaturity',
        label: 'What is your current data governance maturity level?',
        type: 'select' as const,
        required: true,
        options: [
          { value: 'ad-hoc', label: 'Ad-hoc (No formal processes)' },
          { value: 'developing', label: 'Developing (Initial processes)' },
          { value: 'managed', label: 'Managed (Defined processes)' },
          { value: 'optimized', label: 'Optimized (Continuous improvement)' },
        ],
      },
    ],
  },
  {
    id: 4,
    name: 'Impact Assessment',
    description: 'Evaluate the organizational impact and dependencies.',
    fields: [
      {
        name: 'organizationalImpact',
        label: 'What is the potential organizational impact?',
        type: 'textarea' as const,
        required: true,
      },
      {
        name: 'stakeholders',
        label: 'Who are the key stakeholders?',
        type: 'textarea' as const,
        required: true,
      },
      {
        name: 'risks',
        label: 'What are the key risks and mitigation strategies?',
        type: 'textarea' as const,
        required: true,
      },
    ],
  },
  {
    id: 5,
    name: 'Governance',
    description:
      'Define governance structure, roles, and responsibilities.',
    fields: [
      {
        name: 'governanceStructure',
        label: 'Describe your proposed governance structure',
        type: 'textarea' as const,
        required: true,
      },
      {
        name: 'rolesResponsibilities',
        label: 'Define roles and responsibilities',
        type: 'textarea' as const,
        required: true,
      },
      {
        name: 'complianceRequirements',
        label: 'What compliance and regulatory requirements apply?',
        type: 'textarea' as const,
        required: false,
      },
      {
        name: 'reviewCycle',
        label: 'What is your governance review cycle?',
        type: 'select' as const,
        required: true,
        options: [
          { value: 'quarterly', label: 'Quarterly' },
          { value: 'biannual', label: 'Biannual' },
          { value: 'annual', label: 'Annual' },
        ],
      },
    ],
  },
]

export default function StageExecution() {
  const { id: sessionId, stageId } = useParams<{
    id: string
    stageId: string
  }>()
  const navigate = useNavigate()
  const { sessions, updateSession } = useSession()
  const [isSubmitting, setIsSubmitting] = useState(false)

  const currentStageId = parseInt(stageId || '1', 10)
  const stageConfig = stageConfigs[currentStageId - 1]
  const session = sessions?.find((s) => s.id === sessionId)

  if (!session) {
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

  if (!stageConfig) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
        <h2 className="text-lg font-semibold text-red-900 mb-2">
          Invalid Stage
        </h2>
        <button
          onClick={() => navigate(`/sessions/${sessionId}`)}
          className="text-indigo-600 hover:text-indigo-800 font-medium"
        >
          Back to Session
        </button>
      </div>
    )
  }

  const handleStageSubmit = async (data: Record<string, any>) => {
    setIsSubmitting(true)
    try {
      // Save stage data to session
      const nextStage = Math.min(currentStageId + 1, 5)
      const isComplete = nextStage > session.totalStages

      await updateSession({
        ...session,
        currentStage: nextStage,
        status: isComplete ? 'completed' : 'in_progress',
        stageData: {
          ...session.stageData,
          [currentStageId]: data,
        },
      })

      // Navigate to next stage or back to session detail
      if (isComplete) {
        navigate(`/sessions/${sessionId}`)
      } else {
        navigate(`/sessions/${sessionId}/stage/${nextStage}`)
      }
    } catch (error) {
      console.error('Error saving stage:', error)
    } finally {
      setIsSubmitting(false)
    }
  }

  const initialData = (session.stageData?.[currentStageId] as Record<string, any>) || {}

  return (
    <div className="space-y-8">
      {/* Navigation */}
      <div className="flex items-center justify-between mb-8">
        <button
          onClick={() => navigate(`/sessions/${sessionId}`)}
          className="text-gray-600 hover:text-gray-900 flex items-center space-x-2"
        >
          <span>←</span>
          <span>Back to Session</span>
        </button>
      </div>

      {/* Stage Form */}
      <StageForm
        stageId={stageConfig.id}
        stageName={stageConfig.name}
        description={stageConfig.description}
        fields={stageConfig.fields as FormField[]}
        initialData={initialData}
        onSubmit={handleStageSubmit}
        isLoading={isSubmitting}
      />
    </div>
  )
}

// Re-export stage configs for testing
export { stageConfigs }
