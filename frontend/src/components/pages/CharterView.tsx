import { useParams, useNavigate } from 'react-router-dom'
import { useSession } from '../../hooks/useSession'
import { useState } from 'react'

interface CharterSection {
  title: string
  content: string
}

export default function CharterView() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { sessions, isLoading } = useSession()
  const [downloadFormat, setDownloadFormat] = useState<'pdf' | 'markdown' | 'json'>('pdf')

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
          Charter Not Found
        </h2>
        <p className="text-red-700 mb-4">
          The charter for this session doesn't exist yet.
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

  // Generate charter content from session data
  const charterSections: CharterSection[] = [
    {
      title: 'Executive Summary',
      content: `This charter establishes the governance framework for ${session.projectName}. It defines the structure, roles, and responsibilities for managing data and information assets within the organization.`,
    },
    {
      title: 'Purpose and Scope',
      content:
        'This charter defines the governance structure, decision rights, and accountability mechanisms for the organization\'s data management initiatives.',
    },
    {
      title: 'Governance Structure',
      content:
        'The governance structure includes clear roles, responsibilities, and reporting lines for data management across the organization.',
    },
    {
      title: 'Key Principles',
      content: `The governance framework is built on these key principles:
- Data as an asset
- Accountability and ownership
- Transparency and communication
- Continuous improvement
- Compliance and risk management`,
    },
    {
      title: 'Implementation Roadmap',
      content: `Implementation will proceed in phases:
Phase 1: Establish governance structure (Months 1-2)
Phase 2: Define policies and procedures (Months 2-3)
Phase 3: Deploy tools and processes (Months 3-4)
Phase 4: Monitor and optimize (Months 4+)`,
    },
  ]

  const handleDownload = (format: 'pdf' | 'markdown' | 'json') => {
    let content = ''
    let filename = `${session.projectName}-charter`
    let mimeType = 'text/plain'

    if (format === 'markdown') {
      content = generateMarkdown(charterSections)
      filename += '.md'
      mimeType = 'text/markdown'
    } else if (format === 'json') {
      content = JSON.stringify(
        { charter: charterSections, project: session.projectName },
        null,
        2
      )
      filename += '.json'
      mimeType = 'application/json'
    } else {
      // For PDF, we'd typically use a library like pdfkit
      // For now, we'll export as text
      content = generatePlainText(charterSections)
      filename += '.txt'
      mimeType = 'text/plain'
    }

    // Create and download file
    const element = document.createElement('a')
    element.setAttribute(
      'href',
      'data:' + mimeType + ';charset=utf-8,' + encodeURIComponent(content)
    )
    element.setAttribute('download', filename)
    element.style.display = 'none'
    document.body.appendChild(element)
    element.click()
    document.body.removeChild(element)
  }

  const generateMarkdown = (sections: CharterSection[]): string => {
    let md = `# ${session.projectName} - Data Governance Charter\n\n`
    md += `Generated: ${new Date().toLocaleDateString()}\n\n`

    sections.forEach((section) => {
      md += `## ${section.title}\n\n${section.content}\n\n`
    })

    return md
  }

  const generatePlainText = (sections: CharterSection[]): string => {
    let text = `${session.projectName.toUpperCase()} - DATA GOVERNANCE CHARTER\n`
    text += `Generated: ${new Date().toLocaleDateString()}\n`
    text += `${'='.repeat(60)}\n\n`

    sections.forEach((section) => {
      text += `${section.title.toUpperCase()}\n${'-'.repeat(section.title.length)}\n`
      text += `${section.content}\n\n`
    })

    return text
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Data Governance Charter
          </h1>
          <p className="text-gray-600">
            {session.projectName}
          </p>
        </div>
        <button
          onClick={() => navigate(`/sessions/${session.id}`)}
          className="text-gray-600 hover:text-gray-900"
        >
          ← Back
        </button>
      </div>

      {/* Download Options */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          Download Charter
        </h2>
        <div className="flex flex-wrap gap-4">
          <button
            onClick={() => handleDownload('pdf')}
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-lg transition-colors flex items-center space-x-2"
          >
            <span>📄</span>
            <span>Download PDF</span>
          </button>
          <button
            onClick={() => handleDownload('markdown')}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors flex items-center space-x-2"
          >
            <span>📝</span>
            <span>Download Markdown</span>
          </button>
          <button
            onClick={() => handleDownload('json')}
            className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white font-medium rounded-lg transition-colors flex items-center space-x-2"
          >
            <span>⚙️</span>
            <span>Download JSON</span>
          </button>
        </div>
      </div>

      {/* Charter Content */}
      <div className="bg-white rounded-lg shadow divide-y">
        {charterSections.map((section, index) => (
          <div key={index} className="p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              {section.title}
            </h2>
            <div className="text-gray-700 whitespace-pre-wrap leading-relaxed">
              {section.content}
            </div>
          </div>
        ))}
      </div>

      {/* Charter Info */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-4">
            Project Name
          </h3>
          <p className="text-lg font-bold text-gray-900">
            {session.projectName}
          </p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-4">
            Generated
          </h3>
          <p className="text-lg font-bold text-gray-900">
            {new Date().toLocaleDateString()}
          </p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-4">
            Status
          </h3>
          <p className="text-lg font-bold text-green-600">
            ✓ Approved
          </p>
        </div>
      </div>

      {/* Charter Usage */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h2 className="text-lg font-semibold text-blue-900 mb-2">
          Charter Usage
        </h2>
        <p className="text-blue-700 mb-4">
          This charter serves as the foundational document for your organization's data governance program. Share it with stakeholders and use it to guide policy and process development.
        </p>
        <ul className="list-disc list-inside text-blue-700 space-y-2">
          <li>Reference for governance decisions</li>
          <li>Framework for data management policies</li>
          <li>Communication tool for stakeholders</li>
          <li>Baseline for continuous improvement</li>
        </ul>
      </div>

      {/* Next Steps */}
      <div className="bg-green-50 border border-green-200 rounded-lg p-6">
        <h2 className="text-lg font-semibold text-green-900 mb-2">
          Next Steps
        </h2>
        <p className="text-green-700 mb-4">
          Your charter is ready! Consider these next actions:
        </p>
        <ol className="list-decimal list-inside text-green-700 space-y-2">
          <li>Review with leadership and stakeholders</li>
          <li>Obtain executive approval and sign-off</li>
          <li>Distribute to governance team members</li>
          <li>Begin implementing governance policies</li>
          <li>Schedule periodic reviews and updates</li>
        </ol>
      </div>
    </div>
  )
}
