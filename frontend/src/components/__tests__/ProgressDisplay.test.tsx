import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { ProgressDisplay } from '../ProgressDisplay'

describe('ProgressDisplay Component', () => {
  const mockProgress = {
    session_id: 'test-session-123',
    current_stage: 2,
    questions_answered: 5,
    charter_status: 'generating',
    total_questions: 20,
    started_at: '2025-10-20T10:00:00Z',
  }

  it('should render progress display with current stage', () => {
    render(<ProgressDisplay progress={mockProgress} />)
    
    expect(screen.getByText(/Stage 2/)).toBeInTheDocument()
  })

  it('should render questions answered count', () => {
    render(<ProgressDisplay progress={mockProgress} />)
    
    expect(screen.getByText(/5 of 20/)).toBeInTheDocument()
  })

  it('should render charter status', () => {
    render(<ProgressDisplay progress={mockProgress} />)

    expect(screen.getByText('Generating project charter...')).toBeInTheDocument()
  })

  it('should render progress bar', () => {
    render(<ProgressDisplay progress={mockProgress} />)
    
    const progressBar = screen.getByRole('progressbar')
    expect(progressBar).toBeInTheDocument()
  })

  it('should calculate progress percentage correctly', () => {
    render(<ProgressDisplay progress={mockProgress} />)
    
    const progressBar = screen.getByRole('progressbar')
    expect(progressBar).toHaveAttribute('aria-valuenow', '25')
  })

  it('should render stage names', () => {
    render(<ProgressDisplay progress={mockProgress} />)

    expect(screen.getByText('Value Quantification')).toBeInTheDocument()
  })

  it('should highlight current stage', () => {
    const { container } = render(<ProgressDisplay progress={mockProgress} />)
    
    const stageItems = container.querySelectorAll('[data-testid^="stage-"]')
    expect(stageItems[1]).toHaveClass('bg-indigo-600')
  })

  it('should show completed stages', () => {
    const { container } = render(<ProgressDisplay progress={mockProgress} />)
    
    const stageItems = container.querySelectorAll('[data-testid^="stage-"]')
    expect(stageItems[0]).toHaveClass('bg-green-600')
  })

  it('should show pending stages', () => {
    const { container } = render(<ProgressDisplay progress={mockProgress} />)
    
    const stageItems = container.querySelectorAll('[data-testid^="stage-"]')
    expect(stageItems[2]).toHaveClass('bg-gray-300')
  })

  it('should render with null progress', () => {
    render(<ProgressDisplay progress={null} />)
    
    expect(screen.getByText(/No progress data/)).toBeInTheDocument()
  })

  it('should update when progress changes', () => {
    const { rerender } = render(<ProgressDisplay progress={mockProgress} />)
    
    expect(screen.getByText(/Stage 2/)).toBeInTheDocument()
    
    const updatedProgress = { ...mockProgress, current_stage: 3 }
    rerender(<ProgressDisplay progress={updatedProgress} />)
    
    expect(screen.getByText(/Stage 3/)).toBeInTheDocument()
  })

  it('should render stage names correctly', () => {
    const { container } = render(<ProgressDisplay progress={mockProgress} />)

    // Check that stage numbers are rendered
    for (let i = 1; i <= 5; i++) {
      expect(container.querySelector(`[data-testid="stage-${i}"]`)).toBeInTheDocument()
    }
  })

  it('should render charter status badge', () => {
    const { container } = render(<ProgressDisplay progress={mockProgress} />)

    const badge = container.querySelector('.badge')
    expect(badge).toBeInTheDocument()
    expect(badge).toHaveTextContent('Generating')
  })

  it('should show completed status', () => {
    const completedProgress = { ...mockProgress, charter_status: 'completed' }
    render(<ProgressDisplay progress={completedProgress} />)

    expect(screen.getByText('Completed')).toBeInTheDocument()
  })

  it('should show error status', () => {
    const errorProgress = { ...mockProgress, charter_status: 'error' }
    render(<ProgressDisplay progress={errorProgress} />)

    expect(screen.getByText(/Error generating charter/)).toBeInTheDocument()
  })
})

