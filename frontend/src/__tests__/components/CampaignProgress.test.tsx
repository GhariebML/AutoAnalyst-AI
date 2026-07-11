import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { CampaignProgress } from '../../components/CampaignProgress'
import type { TaskResponse } from '../../types'

describe('CampaignProgress', () => {
  it('does not render when no status and not loading', () => {
    const { container } = render(
      <CampaignProgress status={null} isLoading={false} error={null} />
    )

    expect(container.firstChild).toBeNull()
  })

  it('shows pending status', () => {
    const status: TaskResponse = {
      taskId: 'test-123',
      status: 'pending',
      progress: 0,
      message: 'Pending...',
    }

    render(<CampaignProgress status={status} isLoading={false} error={null} />)

    expect(screen.getByRole('heading', { name: /Mission Initialization/i })).toBeInTheDocument()
    expect(screen.getByText(/test-123/i)).toBeInTheDocument()
  })

  it('shows in_progress status with spinner', () => {
    const status: TaskResponse = {
      taskId: 'test-123',
      status: 'in_progress',
      progress: 50,
      message: 'Generating Campaign...',
    }

    render(<CampaignProgress status={status} isLoading={true} error={null} />)

    expect(screen.getByRole('heading', { name: /Neural Processing Active/i })).toBeInTheDocument()
    expect(screen.getByText('50')).toBeInTheDocument()
  })

  it('shows completed status with checkmark', () => {
    const status: TaskResponse = {
      taskId: 'test-123',
      status: 'completed',
      progress: 100,
      message: 'Campaign Generated Successfully',
    }

    render(<CampaignProgress status={status} isLoading={false} error={null} />)

    expect(screen.getByRole('heading', { name: /Orchestration Complete/i })).toBeInTheDocument()
    expect(screen.getByText('100')).toBeInTheDocument()
  })

  it('shows failed status with error message', () => {
    const status: TaskResponse = {
      taskId: 'test-123',
      status: 'failed',
      progress: 0,
      message: 'Campaign Generation Failed',
    }
 
    render(
      <CampaignProgress
        status={status}
        isLoading={false}
        error="API connection timeout"
      />
    )
 
    expect(screen.getByRole('heading', { name: /Protocol Override Required/i })).toBeInTheDocument()
    expect(screen.getByText(/API connection timeout/i)).toBeInTheDocument()
  })
 
  it('displays progress bar with correct width', () => {
    const status: TaskResponse = {
      taskId: 'test-123',
      status: 'in_progress',
      progress: 75,
      message: '',
    }
 
    const { container } = render(
      <CampaignProgress status={status} isLoading={true} error={null} />
    )
 
    const progressFill = container.querySelector('[style*="width: 75%"]')
    expect(progressFill).toBeInTheDocument()
  })
 
  it('displays error message when provided', () => {
    const status: TaskResponse = {
      taskId: 'test-123',
      status: 'failed',
      progress: 0,
      message: '',
    }
 
    render(
      <CampaignProgress
        status={status}
        isLoading={false}
        error="Network error occurred"
      />
    )
 
    expect(screen.getByText(/Network error occurred/i)).toBeInTheDocument()
  })

  it('shows loading spinner when isLoading is true', () => {
    const { container } = render(
      <CampaignProgress status={null} isLoading={true} error={null} />
    )

    const spinner = container.querySelector('svg')
    expect(spinner).toBeInTheDocument()
  })
})
