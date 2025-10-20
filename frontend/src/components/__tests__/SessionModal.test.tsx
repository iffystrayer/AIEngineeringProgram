import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { SessionModal } from '../SessionModal'

describe('SessionModal Component', () => {
  const mockSessions = [
    {
      session_id: 'session-1',
      user_id: 'user-1',
      project_name: 'Project A',
      description: 'First project',
      status: 'in_progress',
      created_at: '2025-10-20T10:00:00Z',
    },
    {
      session_id: 'session-2',
      user_id: 'user-1',
      project_name: 'Project B',
      description: 'Second project',
      status: 'completed',
      created_at: '2025-10-19T10:00:00Z',
    },
  ]

  it('should not render when isOpen is false', () => {
    const { container } = render(
      <SessionModal
        isOpen={false}
        sessions={mockSessions}
        onSelect={vi.fn()}
        onClose={vi.fn()}
      />
    )
    
    expect(container.querySelector('.fixed')).not.toBeInTheDocument()
  })

  it('should render modal when isOpen is true', () => {
    render(
      <SessionModal
        isOpen={true}
        sessions={mockSessions}
        onSelect={vi.fn()}
        onClose={vi.fn()}
      />
    )
    
    expect(screen.getByText('Select Session')).toBeInTheDocument()
  })

  it('should display all sessions', () => {
    render(
      <SessionModal
        isOpen={true}
        sessions={mockSessions}
        onSelect={vi.fn()}
        onClose={vi.fn()}
      />
    )
    
    expect(screen.getByText('Project A')).toBeInTheDocument()
    expect(screen.getByText('Project B')).toBeInTheDocument()
  })

  it('should display session descriptions', () => {
    render(
      <SessionModal
        isOpen={true}
        sessions={mockSessions}
        onSelect={vi.fn()}
        onClose={vi.fn()}
      />
    )
    
    expect(screen.getByText('First project')).toBeInTheDocument()
    expect(screen.getByText('Second project')).toBeInTheDocument()
  })

  it('should display session status', () => {
    render(
      <SessionModal
        isOpen={true}
        sessions={mockSessions}
        onSelect={vi.fn()}
        onClose={vi.fn()}
      />
    )
    
    expect(screen.getByText(/in_progress/)).toBeInTheDocument()
    expect(screen.getByText(/completed/)).toBeInTheDocument()
  })

  it('should call onSelect when session is clicked', async () => {
    const user = userEvent.setup()
    const onSelect = vi.fn()
    
    render(
      <SessionModal
        isOpen={true}
        sessions={mockSessions}
        onSelect={onSelect}
        onClose={vi.fn()}
      />
    )
    
    const sessionButton = screen.getByText('Project A').closest('button')
    await user.click(sessionButton!)
    
    expect(onSelect).toHaveBeenCalledWith(mockSessions[0])
  })

  it('should call onClose when close button is clicked', async () => {
    const user = userEvent.setup()
    const onClose = vi.fn()
    
    render(
      <SessionModal
        isOpen={true}
        sessions={mockSessions}
        onSelect={vi.fn()}
        onClose={onClose}
      />
    )
    
    const closeButton = screen.getByRole('button', { name: /Close/ })
    await user.click(closeButton)
    
    expect(onClose).toHaveBeenCalled()
  })

  it('should call onClose when backdrop is clicked', async () => {
    const user = userEvent.setup()
    const onClose = vi.fn()
    
    const { container } = render(
      <SessionModal
        isOpen={true}
        sessions={mockSessions}
        onSelect={vi.fn()}
        onClose={onClose}
      />
    )
    
    const backdrop = container.querySelector('.fixed.inset-0')
    await user.click(backdrop!)
    
    expect(onClose).toHaveBeenCalled()
  })

  it('should show empty state when no sessions', () => {
    render(
      <SessionModal
        isOpen={true}
        sessions={[]}
        onSelect={vi.fn()}
        onClose={vi.fn()}
      />
    )
    
    expect(screen.getByText(/No sessions found/)).toBeInTheDocument()
  })

  it('should show loading state', () => {
    render(
      <SessionModal
        isOpen={true}
        sessions={mockSessions}
        isLoading={true}
        onSelect={vi.fn()}
        onClose={vi.fn()}
      />
    )
    
    expect(screen.getByText(/Loading/)).toBeInTheDocument()
  })

  it('should have proper modal styling', () => {
    const { container } = render(
      <SessionModal
        isOpen={true}
        sessions={mockSessions}
        onSelect={vi.fn()}
        onClose={vi.fn()}
      />
    )
    
    const modal = container.querySelector('.fixed')
    expect(modal).toHaveClass('inset-0')
    expect(modal).toHaveClass('z-50')
  })

  it('should render session items with proper structure', () => {
    const { container } = render(
      <SessionModal
        isOpen={true}
        sessions={mockSessions}
        onSelect={vi.fn()}
        onClose={vi.fn()}
      />
    )
    
    const sessionItems = container.querySelectorAll('[data-testid^="session-item-"]')
    expect(sessionItems).toHaveLength(2)
  })
})

