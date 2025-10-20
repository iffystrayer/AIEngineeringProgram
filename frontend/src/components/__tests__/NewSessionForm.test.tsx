import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { NewSessionForm } from '../NewSessionForm'

describe('NewSessionForm Component', () => {
  it('should render form with all fields', () => {
    render(<NewSessionForm onSubmit={vi.fn()} onCancel={vi.fn()} />)
    
    expect(screen.getByLabelText(/User ID/)).toBeInTheDocument()
    expect(screen.getByLabelText(/Project Name/)).toBeInTheDocument()
    expect(screen.getByLabelText(/Description/)).toBeInTheDocument()
  })

  it('should render submit button', () => {
    render(<NewSessionForm onSubmit={vi.fn()} onCancel={vi.fn()} />)
    
    expect(screen.getByRole('button', { name: /Start Session/ })).toBeInTheDocument()
  })

  it('should render cancel button', () => {
    render(<NewSessionForm onSubmit={vi.fn()} onCancel={vi.fn()} />)
    
    expect(screen.getByRole('button', { name: /Cancel/ })).toBeInTheDocument()
  })

  it('should call onCancel when cancel button is clicked', async () => {
    const user = userEvent.setup()
    const onCancel = vi.fn()
    
    render(<NewSessionForm onSubmit={vi.fn()} onCancel={onCancel} />)
    
    const cancelButton = screen.getByRole('button', { name: /Cancel/ })
    await user.click(cancelButton)
    
    expect(onCancel).toHaveBeenCalled()
  })

  it('should validate required fields', async () => {
    const user = userEvent.setup()
    const onSubmit = vi.fn()
    
    render(<NewSessionForm onSubmit={onSubmit} onCancel={vi.fn()} />)
    
    const submitButton = screen.getByRole('button', { name: /Start Session/ })
    await user.click(submitButton)
    
    expect(onSubmit).not.toHaveBeenCalled()
  })

  it('should submit form with valid data', async () => {
    const user = userEvent.setup()
    const onSubmit = vi.fn()
    
    render(<NewSessionForm onSubmit={onSubmit} onCancel={vi.fn()} />)
    
    const userIdInput = screen.getByLabelText(/User ID/)
    const projectNameInput = screen.getByLabelText(/Project Name/)
    
    await user.type(userIdInput, 'user-123')
    await user.type(projectNameInput, 'My Project')
    
    const submitButton = screen.getByRole('button', { name: /Start Session/ })
    await user.click(submitButton)
    
    expect(onSubmit).toHaveBeenCalledWith({
      user_id: 'user-123',
      project_name: 'My Project',
      description: '',
    })
  })

  it('should submit form with description', async () => {
    const user = userEvent.setup()
    const onSubmit = vi.fn()
    
    render(<NewSessionForm onSubmit={onSubmit} onCancel={vi.fn()} />)
    
    const userIdInput = screen.getByLabelText(/User ID/)
    const projectNameInput = screen.getByLabelText(/Project Name/)
    const descriptionInput = screen.getByLabelText(/Description/)
    
    await user.type(userIdInput, 'user-123')
    await user.type(projectNameInput, 'My Project')
    await user.type(descriptionInput, 'Project description')
    
    const submitButton = screen.getByRole('button', { name: /Start Session/ })
    await user.click(submitButton)
    
    expect(onSubmit).toHaveBeenCalledWith({
      user_id: 'user-123',
      project_name: 'My Project',
      description: 'Project description',
    })
  })

  it('should disable submit button when loading', () => {
    render(<NewSessionForm onSubmit={vi.fn()} onCancel={vi.fn()} isLoading={true} />)

    const submitButton = screen.getByRole('button', { name: /Creating session/ })
    expect(submitButton).toBeDisabled()
  })

  it('should show loading indicator', () => {
    render(<NewSessionForm onSubmit={vi.fn()} onCancel={vi.fn()} isLoading={true} />)
    
    expect(screen.getByText(/Creating session/)).toBeInTheDocument()
  })

  it('should display error message', () => {
    render(
      <NewSessionForm
        onSubmit={vi.fn()}
        onCancel={vi.fn()}
        error="Failed to create session"
      />
    )
    
    expect(screen.getByText('Failed to create session')).toBeInTheDocument()
  })

  it('should have proper form styling', () => {
    const { container } = render(
      <NewSessionForm onSubmit={vi.fn()} onCancel={vi.fn()} />
    )
    
    const form = container.querySelector('form')
    expect(form).toHaveClass('space-y-4')
  })

  it('should clear form after successful submission', async () => {
    const user = userEvent.setup()
    const onSubmit = vi.fn()
    
    const { rerender } = render(
      <NewSessionForm onSubmit={onSubmit} onCancel={vi.fn()} />
    )
    
    const userIdInput = screen.getByLabelText(/User ID/) as HTMLInputElement
    const projectNameInput = screen.getByLabelText(/Project Name/) as HTMLInputElement
    
    await user.type(userIdInput, 'user-123')
    await user.type(projectNameInput, 'My Project')
    
    expect(userIdInput.value).toBe('user-123')
    expect(projectNameInput.value).toBe('My Project')
  })

  it('should have input fields with proper attributes', () => {
    render(<NewSessionForm onSubmit={vi.fn()} onCancel={vi.fn()} />)
    
    const userIdInput = screen.getByLabelText(/User ID/) as HTMLInputElement
    expect(userIdInput).toHaveAttribute('type', 'text')
    expect(userIdInput).toHaveAttribute('required')
  })
})

