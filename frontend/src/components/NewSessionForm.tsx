import React, { useState } from 'react'
import { CreateSessionRequest } from '../services/api'

interface NewSessionFormProps {
  onSubmit: (data: CreateSessionRequest) => void
  onCancel: () => void
  isLoading?: boolean
  error?: string
}

/**
 * NewSessionForm Component
 * 
 * Form for creating a new session with user input.
 */
export const NewSessionForm: React.FC<NewSessionFormProps> = ({
  onSubmit,
  onCancel,
  isLoading = false,
  error,
}) => {
  const [formData, setFormData] = useState<CreateSessionRequest>({
    user_id: '',
    project_name: '',
    description: '',
  })

  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({})

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {}

    if (!formData.user_id.trim()) {
      errors.user_id = 'User ID is required'
    }

    if (!formData.project_name.trim()) {
      errors.project_name = 'Project name is required'
    }

    setValidationErrors(errors)
    return Object.keys(errors).length === 0
  }

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }))
    // Clear validation error for this field
    if (validationErrors[name]) {
      setValidationErrors((prev) => ({
        ...prev,
        [name]: '',
      }))
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    if (!validateForm()) {
      return
    }

    onSubmit(formData)
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-8">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">
        Create New Session
      </h2>

      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* User ID Field */}
        <div>
          <label htmlFor="user_id" className="block text-sm font-medium text-gray-700 mb-1">
            User ID
          </label>
          <input
            type="text"
            id="user_id"
            name="user_id"
            value={formData.user_id}
            onChange={handleChange}
            disabled={isLoading}
            required
            className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition ${
              validationErrors.user_id
                ? 'border-red-500'
                : 'border-gray-300'
            }`}
            placeholder="Enter your user ID"
          />
          {validationErrors.user_id && (
            <p className="text-red-600 text-sm mt-1">{validationErrors.user_id}</p>
          )}
        </div>

        {/* Project Name Field */}
        <div>
          <label htmlFor="project_name" className="block text-sm font-medium text-gray-700 mb-1">
            Project Name
          </label>
          <input
            type="text"
            id="project_name"
            name="project_name"
            value={formData.project_name}
            onChange={handleChange}
            disabled={isLoading}
            required
            className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition ${
              validationErrors.project_name
                ? 'border-red-500'
                : 'border-gray-300'
            }`}
            placeholder="Enter project name"
          />
          {validationErrors.project_name && (
            <p className="text-red-600 text-sm mt-1">{validationErrors.project_name}</p>
          )}
        </div>

        {/* Description Field */}
        <div>
          <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
            Description (Optional)
          </label>
          <textarea
            id="description"
            name="description"
            value={formData.description}
            onChange={handleChange}
            disabled={isLoading}
            rows={4}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition"
            placeholder="Enter project description"
          />
        </div>

        {/* Buttons */}
        <div className="flex gap-4 pt-4">
          <button
            type="submit"
            disabled={isLoading}
            className="flex-1 bg-indigo-600 text-white py-2 px-4 rounded-lg hover:bg-indigo-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors font-medium flex items-center justify-center gap-2"
          >
            {isLoading && (
              <svg
                className="animate-spin h-5 w-5"
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
            )}
            {isLoading ? 'Creating session...' : 'Start Session'}
          </button>
          <button
            type="button"
            onClick={onCancel}
            disabled={isLoading}
            className="flex-1 bg-gray-200 text-gray-900 py-2 px-4 rounded-lg hover:bg-gray-300 disabled:bg-gray-100 disabled:cursor-not-allowed transition-colors font-medium"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  )
}

export default NewSessionForm

