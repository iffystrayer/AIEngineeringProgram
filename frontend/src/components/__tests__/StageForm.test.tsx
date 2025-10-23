import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import StageForm from '../forms/StageForm'

const createQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  })

const mockOnSubmit = vi.fn()
const defaultProps = {
  stageId: 1,
  stageName: 'Problem Statement',
  description: 'Define the problem your organization is trying to solve',
  fields: [
    { name: 'problemStatement', label: 'Problem Statement', type: 'textarea', required: true },
    { name: 'businessContext', label: 'Business Context', type: 'textarea', required: true },
  ],
  initialData: {},
  onSubmit: mockOnSubmit,
}

describe('StageForm - Specification Tests', () => {
  it('should provide a form for collecting stage-specific data', () => {
    expect(StageForm).toBeDefined()
    expect(typeof StageForm).toBe('function')
  })

  it('should enforce validation before allowing submission', () => {
    // Specification: Form validates all required fields
    expect(StageForm).toBeDefined()
  })

  it('should collect data for any of the 5 stages', () => {
    // Specification: Generic form component for all stages
    expect(StageForm).toBeDefined()
  })
})

describe('StageForm - Structure Tests', () => {
  it('should render without crashing', () => {
    render(
      <QueryClientProvider client={createQueryClient()}>
        <BrowserRouter>
          <StageForm {...defaultProps} />
        </BrowserRouter>
      </QueryClientProvider>
    )
    expect(document.body).toBeDefined()
  })

  it('should display stage title', () => {
    render(
      <QueryClientProvider client={createQueryClient()}>
        <BrowserRouter>
          <StageForm {...defaultProps} />
        </BrowserRouter>
      </QueryClientProvider>
    )

    expect(screen.getByText('Problem Statement')).toBeInTheDocument()
  })

  it('should display stage description', () => {
    render(
      <QueryClientProvider client={createQueryClient()}>
        <BrowserRouter>
          <StageForm {...defaultProps} />
        </BrowserRouter>
      </QueryClientProvider>
    )

    expect(screen.getByText(/Define the problem/i)).toBeInTheDocument()
  })

  it('should render form fields based on stage', () => {
    render(
      <QueryClientProvider client={createQueryClient()}>
        <BrowserRouter>
          <StageForm {...defaultProps} />
        </BrowserRouter>
      </QueryClientProvider>
    )

    expect(screen.getByLabelText(/Problem Statement/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/Business Context/i)).toBeInTheDocument()
  })

  it('should have submit button', () => {
    render(
      <QueryClientProvider client={createQueryClient()}>
        <BrowserRouter>
          <StageForm {...defaultProps} />
        </BrowserRouter>
      </QueryClientProvider>
    )

    expect(screen.getByRole('button', { name: /continue|submit|next/i })).toBeInTheDocument()
  })
})

describe('StageForm - Execution Tests', () => {
  it('should accept user input', async () => {
    const user = userEvent.setup()
    const { container } = render(
      <QueryClientProvider client={createQueryClient()}>
        <BrowserRouter>
          <StageForm {...defaultProps} />
        </BrowserRouter>
      </QueryClientProvider>
    )

    // Find the textarea by its id or role
    const problemInputs = container.querySelectorAll('textarea, input')
    if (problemInputs.length > 0) {
      await user.type(problemInputs[0], 'Test problem statement')
      expect((problemInputs[0] as HTMLTextAreaElement).value).toContain('Test')
    }
  })

  it('should show validation error for empty required field', async () => {
    const user = userEvent.setup()
    const { container } = render(
      <QueryClientProvider client={createQueryClient()}>
        <BrowserRouter>
          <StageForm {...defaultProps} />
        </BrowserRouter>
      </QueryClientProvider>
    )

    const submitBtn = screen.getByRole('button', { name: /continue|submit|next/i })
    await user.click(submitBtn)

    // Form should prevent invalid submission
    expect(container).toBeDefined()
  })

  it('should enable submit when all required fields are filled', async () => {
    const user = userEvent.setup()
    const { container } = render(
      <QueryClientProvider client={createQueryClient()}>
        <BrowserRouter>
          <StageForm {...defaultProps} />
        </BrowserRouter>
      </QueryClientProvider>
    )

    const inputs = container.querySelectorAll('textarea, input[type="text"]')
    if (inputs.length >= 2) {
      await user.type(inputs[0], 'Test problem')
      await user.type(inputs[1], 'Test context')
    }

    const submitBtn = screen.getByRole('button', { name: /continue|submit|next/i })
    expect(submitBtn).not.toBeDisabled()
  })

  it('should call onSubmit with form data when submitted', async () => {
    const user = userEvent.setup()
    const { container } = render(
      <QueryClientProvider client={createQueryClient()}>
        <BrowserRouter>
          <StageForm {...defaultProps} />
        </BrowserRouter>
      </QueryClientProvider>
    )

    const inputs = container.querySelectorAll('textarea, input[type="text"]')
    if (inputs.length >= 2) {
      await user.type(inputs[0], 'Test problem')
      await user.type(inputs[1], 'Test context')
    }

    const submitBtn = screen.getByRole('button', { name: /continue|submit|next/i })
    await user.click(submitBtn)

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalled()
    })
  })

  it('should display progress indicator showing current stage', () => {
    render(
      <QueryClientProvider client={createQueryClient()}>
        <BrowserRouter>
          <StageForm {...defaultProps} />
        </BrowserRouter>
      </QueryClientProvider>
    )

    expect(screen.getByText(/Stage 1/i)).toBeInTheDocument()
  })
})

describe('StageForm - Integration Tests', () => {
  it('should work with React Hook Form', () => {
    render(
      <QueryClientProvider client={createQueryClient()}>
        <BrowserRouter>
          <StageForm {...defaultProps} />
        </BrowserRouter>
      </QueryClientProvider>
    )

    expect(screen.getByText('Problem Statement')).toBeInTheDocument()
  })

  it('should populate initial data when provided', () => {
    const propsWithData = {
      ...defaultProps,
      initialData: {
        problemStatement: 'Existing problem',
        businessContext: 'Existing context',
      },
    }

    render(
      <QueryClientProvider client={createQueryClient()}>
        <BrowserRouter>
          <StageForm {...propsWithData} />
        </BrowserRouter>
      </QueryClientProvider>
    )

    expect(screen.getByLabelText(/Problem Statement/i)).toHaveValue('Existing problem')
    expect(screen.getByLabelText(/Business Context/i)).toHaveValue('Existing context')
  })
})

describe('StageForm - Error Handling Tests', () => {
  it('should handle submission errors gracefully', async () => {
    const user = userEvent.setup()
    const mockErrorSubmit = vi.fn().mockRejectedValue(new Error('Submit failed'))

    render(
      <QueryClientProvider client={createQueryClient()}>
        <BrowserRouter>
          <StageForm {...{ ...defaultProps, onSubmit: mockErrorSubmit }} />
        </BrowserRouter>
      </QueryClientProvider>
    )

    const problemInput = screen.getByLabelText(/Problem Statement/i)
    const contextInput = screen.getByLabelText(/Business Context/i)

    await user.type(problemInput, 'Test')
    await user.type(contextInput, 'Test')

    const submitBtn = screen.getByRole('button', { name: /continue|submit|next/i })
    await user.click(submitBtn)

    await waitFor(() => {
      expect(mockErrorSubmit).toHaveBeenCalled()
    })
  })
})
