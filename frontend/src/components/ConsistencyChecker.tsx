import { useSession } from '../hooks/useSession'
import { useState, useMemo } from 'react'

interface ConsistencyCheck {
  id: string
  name: string
  description: string
  status: 'pass' | 'fail' | 'warning'
  message: string
  recommendation?: string
}

interface ConsistencyCheckerProps {
  sessionId: string
  onComplete?: (checks: ConsistencyCheck[]) => void
}

export default function ConsistencyChecker({ sessionId, onComplete }: ConsistencyCheckerProps) {
  const { sessions } = useSession()
  const [isChecking, setIsChecking] = useState(false)

  const session = sessions?.find((s) => s.id === sessionId)

  const consistencyChecks = useMemo(() => {
    if (!session) return []

    const checks: ConsistencyCheck[] = []
    const data = session.stageData || {}

    // Check 1: Problem Statement Clarity
    const ps = (data[1] as any)?.problemStatement || ''
    checks.push({
      id: 'problem-clarity',
      name: 'Problem Statement Clarity',
      description: 'Validates that the problem statement is clearly defined',
      status: ps && ps.length > 50 ? 'pass' : ps ? 'warning' : 'fail',
      message:
        ps && ps.length > 50
          ? 'Problem statement is well-defined'
          : 'Problem statement needs more detail',
      recommendation:
        ps && ps.length <= 50
          ? 'Provide more specific details about the problem'
          : undefined,
    })

    // Check 2: Metric Definition
    const metrics = (data[2] as any)?.successMetrics || ''
    checks.push({
      id: 'metric-definition',
      name: 'Metric Definition',
      description: 'Validates that success metrics are defined',
      status: metrics && metrics.length > 30 ? 'pass' : metrics ? 'warning' : 'fail',
      message:
        metrics && metrics.length > 30
          ? 'Success metrics are clearly defined'
          : 'Success metrics need definition',
      recommendation:
        metrics && metrics.length <= 30
          ? 'Define specific, measurable success criteria'
          : undefined,
    })

    // Check 3: Data Quality Assessment
    const dataQuality = (data[3] as any)?.dataQualityRequirements || ''
    checks.push({
      id: 'data-quality',
      name: 'Data Quality Assessment',
      description: 'Validates data quality requirements are specified',
      status: dataQuality && dataQuality.length > 40 ? 'pass' : dataQuality ? 'warning' : 'fail',
      message:
        dataQuality && dataQuality.length > 40
          ? 'Data quality requirements are defined'
          : 'Data quality requirements need clarification',
      recommendation:
        dataQuality && dataQuality.length <= 40
          ? 'Provide detailed data quality specifications'
          : undefined,
    })

    // Check 4: Impact Assessment
    const impact = (data[4] as any)?.organizationalImpact || ''
    checks.push({
      id: 'impact-assessment',
      name: 'Impact Assessment',
      description: 'Validates organizational impact is assessed',
      status: impact && impact.length > 50 ? 'pass' : impact ? 'warning' : 'fail',
      message:
        impact && impact.length > 50
          ? 'Organizational impact is well-assessed'
          : 'Impact assessment needs more detail',
      recommendation:
        impact && impact.length <= 50
          ? 'Provide detailed organizational impact analysis'
          : undefined,
    })

    // Check 5: Governance Structure
    const governance = (data[5] as any)?.governanceStructure || ''
    checks.push({
      id: 'governance',
      name: 'Governance Structure',
      description: 'Validates governance structure is defined',
      status: governance && governance.length > 50 ? 'pass' : governance ? 'warning' : 'fail',
      message:
        governance && governance.length > 50
          ? 'Governance structure is defined'
          : 'Governance structure needs definition',
      recommendation:
        governance && governance.length <= 50
          ? 'Define clear governance structure and roles'
          : undefined,
    })

    // Check 6: Cross-stage Consistency
    const allFieldsFilled = ps && metrics && dataQuality && impact && governance
    checks.push({
      id: 'completeness',
      name: 'Questionnaire Completeness',
      description: 'Validates all stages are completed',
      status: allFieldsFilled ? 'pass' : 'fail',
      message: allFieldsFilled
        ? 'All stages are complete'
        : 'Some stages are incomplete',
      recommendation: !allFieldsFilled
        ? 'Complete all remaining stages'
        : undefined,
    })

    return checks
  }, [session])

  const passCount = consistencyChecks.filter((c) => c.status === 'pass').length
  const warningCount = consistencyChecks.filter((c) => c.status === 'warning').length
  const failCount = consistencyChecks.filter((c) => c.status === 'fail').length
  const totalCount = consistencyChecks.length

  const overallStatus =
    failCount > 0 ? 'fail' : warningCount > 0 ? 'warning' : 'pass'

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pass':
        return 'text-green-700 bg-green-50 border-green-200'
      case 'warning':
        return 'text-yellow-700 bg-yellow-50 border-yellow-200'
      case 'fail':
        return 'text-red-700 bg-red-50 border-red-200'
      default:
        return 'text-gray-700 bg-gray-50 border-gray-200'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pass':
        return '✓'
      case 'warning':
        return '⚠️'
      case 'fail':
        return '✗'
      default:
        return '—'
    }
  }

  if (!session) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
        <p className="text-red-700">Session not found</p>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Consistency Check Report
        </h1>
        <p className="text-gray-600">
          Validation of questionnaire responses for {session.projectName}
        </p>
      </div>

      {/* Overall Status */}
      <div
        className={`rounded-lg border-2 p-6 ${getStatusColor(overallStatus)}`}
      >
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold mb-2">
              {getStatusIcon(overallStatus)} Overall Status:{' '}
              {overallStatus === 'pass'
                ? 'PASSED'
                : overallStatus === 'warning'
                  ? 'WARNINGS'
                  : 'NEEDS ATTENTION'}
            </h2>
            <p>
              {passCount} passed, {warningCount} warnings, {failCount} issues out of {totalCount} checks
            </p>
          </div>
          <div className="text-right">
            <div className="text-4xl font-bold">
              {Math.round((passCount / totalCount) * 100)}%
            </div>
            <div className="text-sm">Pass Rate</div>
          </div>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Progress</h3>
        <div className="space-y-2">
          <div className="flex items-center space-x-2">
            <div className="flex-1 h-3 bg-gray-200 rounded-full overflow-hidden">
              <div
                className="h-full bg-green-500 transition-all"
                style={{ width: `${(passCount / totalCount) * 100}%` }}
              />
            </div>
            <span className="text-sm font-medium text-gray-600 w-12 text-right">
              {Math.round((passCount / totalCount) * 100)}%
            </span>
          </div>
          <div className="flex items-center justify-between text-sm text-gray-600">
            <div className="flex space-x-4">
              <span className="flex items-center space-x-1">
                <span className="w-2 h-2 rounded-full bg-green-500"></span>
                <span>Pass: {passCount}</span>
              </span>
              <span className="flex items-center space-x-1">
                <span className="w-2 h-2 rounded-full bg-yellow-500"></span>
                <span>Warnings: {warningCount}</span>
              </span>
              <span className="flex items-center space-x-1">
                <span className="w-2 h-2 rounded-full bg-red-500"></span>
                <span>Fail: {failCount}</span>
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Detailed Check Results */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900">Detailed Results</h3>
        {consistencyChecks.map((check) => (
          <div
            key={check.id}
            className={`rounded-lg border-2 p-6 ${getStatusColor(check.status)}`}
          >
            <div className="flex items-start justify-between mb-2">
              <h4 className="text-lg font-semibold">
                {getStatusIcon(check.status)} {check.name}
              </h4>
              <span
                className={`px-3 py-1 rounded-full text-sm font-medium ${
                  check.status === 'pass'
                    ? 'bg-green-100 text-green-800'
                    : check.status === 'warning'
                      ? 'bg-yellow-100 text-yellow-800'
                      : 'bg-red-100 text-red-800'
                }`}
              >
                {check.status.toUpperCase()}
              </span>
            </div>
            <p className="text-sm mb-3">{check.description}</p>
            <p className="font-medium mb-2">{check.message}</p>
            {check.recommendation && (
              <div className="mt-3 p-3 bg-white bg-opacity-50 rounded">
                <p className="text-sm font-medium">Recommendation:</p>
                <p className="text-sm">{check.recommendation}</p>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Recommendations */}
      {failCount > 0 || warningCount > 0 ? (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-blue-900 mb-4">
            Recommended Actions
          </h3>
          <ol className="list-decimal list-inside space-y-2 text-blue-700">
            {consistencyChecks
              .filter((c) => c.recommendation)
              .map((check, idx) => (
                <li key={idx}>{check.recommendation}</li>
              ))}
          </ol>
        </div>
      ) : (
        <div className="bg-green-50 border border-green-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-green-900 mb-2">
            All Checks Passed ✓
          </h3>
          <p className="text-green-700">
            Your questionnaire responses are consistent and complete. You're ready to generate your governance charter!
          </p>
        </div>
      )}
    </div>
  )
}
