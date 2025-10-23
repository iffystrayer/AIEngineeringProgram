import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { ReactNode } from 'react'

export interface FormField {
  name: string
  label: string
  type: 'text' | 'textarea' | 'select' | 'checkbox' | 'radio'
  required?: boolean
  placeholder?: string
  options?: { value: string; label: string }[]
  helpText?: string
}

interface StageFormProps {
  stageId: number
  stageName: string
  description: string
  fields: FormField[]
  initialData?: Record<string, any>
  onSubmit: (data: Record<string, any>) => Promise<void>
  isLoading?: boolean
}

export default function StageForm({
  stageId,
  stageName,
  description,
  fields,
  initialData = {},
  onSubmit,
  isLoading = false,
}: StageFormProps) {
  // Dynamically create Zod schema based on fields
  const schemaShape: Record<string, z.ZodTypeAny> = {}

  fields.forEach((field) => {
    let fieldSchema: z.ZodTypeAny = z.string()

    if (field.type === 'textarea') {
      fieldSchema = z.string().min(10, 'Please provide more details')
    } else if (field.type === 'checkbox') {
      fieldSchema = z.boolean()
    }

    if (field.required) {
      fieldSchema = fieldSchema.refine((val) => {
        if (field.type === 'checkbox') return typeof val === 'boolean'
        return val && val.toString().trim().length > 0
      }, `${field.label} is required`)
    } else {
      fieldSchema = fieldSchema.optional()
    }

    schemaShape[field.name] = fieldSchema
  })

  const validationSchema = z.object(schemaShape)
  type FormData = z.infer<typeof validationSchema>

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<FormData>({
    resolver: zodResolver(validationSchema),
    defaultValues: initialData,
  })

  const handleFormSubmit = async (data: FormData) => {
    try {
      await onSubmit(data)
      reset()
    } catch (error) {
      console.error('Form submission error:', error)
    }
  }

  return (
    <div className="max-w-2xl mx-auto space-y-8">
      {/* Progress Indicator */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            Stage {stageId}: {stageName}
          </h1>
          <p className="text-gray-600 mt-2">{description}</p>
        </div>
        <div className="text-right">
          <div className="text-sm text-gray-600">Progress</div>
          <div className="text-2xl font-bold text-indigo-600">
            {stageId}/5
          </div>
        </div>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-6">
        {/* Form Fields */}
        {fields.map((field) => (
          <div key={field.name}>
            <label
              htmlFor={field.name}
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              {field.label}
              {field.required && <span className="text-red-500 ml-1">*</span>}
            </label>

            {/* Text Input */}
            {field.type === 'text' && (
              <input
                {...register(field.name)}
                type="text"
                id={field.name}
                placeholder={field.placeholder}
                className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition ${
                  errors[field.name]
                    ? 'border-red-500'
                    : 'border-gray-300'
                }`}
              />
            )}

            {/* Textarea */}
            {field.type === 'textarea' && (
              <textarea
                {...register(field.name)}
                id={field.name}
                placeholder={field.placeholder}
                rows={4}
                className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition resize-none ${
                  errors[field.name]
                    ? 'border-red-500'
                    : 'border-gray-300'
                }`}
              />
            )}

            {/* Select */}
            {field.type === 'select' && (
              <select
                {...register(field.name)}
                id={field.name}
                className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition ${
                  errors[field.name]
                    ? 'border-red-500'
                    : 'border-gray-300'
                }`}
              >
                <option value="">Select an option</option>
                {field.options?.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            )}

            {/* Checkbox */}
            {field.type === 'checkbox' && (
              <div className="flex items-center mt-2">
                <input
                  {...register(field.name)}
                  type="checkbox"
                  id={field.name}
                  className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded cursor-pointer"
                />
              </div>
            )}

            {/* Radio Buttons */}
            {field.type === 'radio' && (
              <div className="space-y-2 mt-2">
                {field.options?.map((option) => (
                  <div key={option.value} className="flex items-center">
                    <input
                      {...register(field.name)}
                      type="radio"
                      id={`${field.name}-${option.value}`}
                      value={option.value}
                      className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 cursor-pointer"
                    />
                    <label
                      htmlFor={`${field.name}-${option.value}`}
                      className="ml-3 text-sm text-gray-700 cursor-pointer"
                    >
                      {option.label}
                    </label>
                  </div>
                ))}
              </div>
            )}

            {/* Help Text */}
            {field.helpText && !errors[field.name] && (
              <p className="mt-1 text-sm text-gray-500">{field.helpText}</p>
            )}

            {/* Error Message */}
            {errors[field.name] && (
              <p className="mt-1 text-sm text-red-500">
                {errors[field.name]?.message as string}
              </p>
            )}
          </div>
        ))}

        {/* Form Actions */}
        <div className="flex items-center justify-between pt-6 border-t border-gray-200">
          <button
            type="button"
            className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 font-medium hover:bg-gray-50 transition-colors"
          >
            Back
          </button>

          <button
            type="submit"
            disabled={isLoading}
            className="px-6 py-2 bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-400 text-white font-medium rounded-lg transition-colors"
          >
            {isLoading ? 'Saving...' : 'Continue to Next Stage'}
          </button>
        </div>
      </form>
    </div>
  )
}
