import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { LandingPage } from '../LandingPage'

describe('LandingPage Component', () => {
  it('should render the landing page with title', () => {
    render(<LandingPage />)
    
    expect(screen.getByText('U-AIP Scoping Assistant')).toBeInTheDocument()
    expect(
      screen.getByText('Universal AI Project Scoping and Framing Protocol')
    ).toBeInTheDocument()
  })

  it('should render start new project card', () => {
    render(<LandingPage />)
    
    expect(screen.getByText('Start New Project')).toBeInTheDocument()
    expect(
      screen.getByText(/Begin a new AI project evaluation/)
    ).toBeInTheDocument()
    expect(screen.getByTestId('start-new-button')).toBeInTheDocument()
  })

  it('should render resume session card', () => {
    render(<LandingPage />)
    
    expect(screen.getByText('Resume Session')).toBeInTheDocument()
    expect(
      screen.getByText(/Continue working on an existing project evaluation/)
    ).toBeInTheDocument()
    expect(screen.getByTestId('resume-button')).toBeInTheDocument()
  })

  it('should render all 5 stages', () => {
    render(<LandingPage />)
    
    expect(screen.getByText('Business Translation')).toBeInTheDocument()
    expect(screen.getByText('Value Quantification')).toBeInTheDocument()
    expect(screen.getByText('Data Feasibility')).toBeInTheDocument()
    expect(screen.getByText('User Centricity')).toBeInTheDocument()
    expect(screen.getByText('Ethical Governance')).toBeInTheDocument()
  })

  it('should call onStartNew when start button is clicked', async () => {
    const user = userEvent.setup()
    const onStartNew = vi.fn()
    
    render(<LandingPage onStartNew={onStartNew} />)
    
    const startButton = screen.getByTestId('start-new-button')
    await user.click(startButton)
    
    expect(onStartNew).toHaveBeenCalledOnce()
  })

  it('should call onResume when resume button is clicked', async () => {
    const user = userEvent.setup()
    const onResume = vi.fn()
    
    render(<LandingPage onResume={onResume} />)
    
    const resumeButton = screen.getByTestId('resume-button')
    await user.click(resumeButton)
    
    expect(onResume).toHaveBeenCalledOnce()
  })

  it('should have proper styling classes', () => {
    const { container } = render(<LandingPage />)
    
    const mainDiv = container.firstChild
    expect(mainDiv).toHaveClass('min-h-screen')
    expect(mainDiv).toHaveClass('bg-gradient-to-br')
  })

  it('should render stage numbers correctly', () => {
    render(<LandingPage />)
    
    for (let i = 1; i <= 5; i++) {
      expect(screen.getByText(i.toString())).toBeInTheDocument()
    }
  })
})

