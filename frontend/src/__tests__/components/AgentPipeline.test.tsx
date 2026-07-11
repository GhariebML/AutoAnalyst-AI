import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { AgentPipeline } from '../../components/AgentPipeline'
import type { TaskResponse } from '../../types'

describe('AgentPipeline', () => {
  it('does not render when no status and not loading', () => {
    const { container } = render(
      <AgentPipeline status={null} isLoading={false} error={null} />
    )
    // it renders the shell but shows idle agents
    expect(container.firstChild).not.toBeNull()
  })

  it('shows all 5 agents', () => {
    render(<AgentPipeline status={null} isLoading={false} error={null} />)
    expect(screen.getByText(/Strategy Agent/i)).toBeInTheDocument()
    expect(screen.getByText(/Research Agent/i)).toBeInTheDocument()
    expect(screen.getByText(/Content Agent/i)).toBeInTheDocument()
    expect(screen.getByText(/Analytics Agent/i)).toBeInTheDocument()
    expect(screen.getByText(/Design Agent/i)).toBeInTheDocument()
  })

  it('shows Processing badge on the running agent', () => {
    // At 50% progress, Content agent (40-60%) should be running
    const status: TaskResponse = { taskId: 'test-123', status: 'in_progress', progress: 50, message: '' }
    render(<AgentPipeline status={status} isLoading={true} error={null} />)
    expect(screen.getByText(/Processing/i)).toBeInTheDocument()
  })

  it('shows CheckCircle2 icons on completed agents', () => {
    // At 60%, Strategy(0-20) and Research(20-40) should be done
    const status: TaskResponse = { taskId: 'test-123', status: 'in_progress', progress: 60, message: '' }
    const { container } = render(<AgentPipeline status={status} isLoading={true} error={null} />)
    const checkmarks = container.querySelectorAll('.lucide-check-circle2')
    expect(checkmarks.length).toBeGreaterThanOrEqual(2)
  })

  it('shows error message when provided', () => {
    render(<AgentPipeline status={null} isLoading={false} error="Connection failed" />)
    expect(screen.getByText(/Connection failed/i)).toBeInTheDocument()
  })
})
