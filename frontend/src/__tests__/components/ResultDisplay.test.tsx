import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { ResultDisplay } from '../../components/ResultDisplay'
import type { ContentOutput } from '../../types'

describe('ResultDisplay', () => {
  const mockContent: ContentOutput = {
    ads: [
      {
        platform: 'Facebook',
        headline: 'Test Headline',
        body: 'Test body content',
        cta: 'Click Here',
        performance: 'Expected CTR: 3.2%',
      },
    ],
    emailSequences: [
      {
        subject: 'Welcome Email',
        preview: 'Welcome to our service',
        body: 'Thank you for signing up',
        sequence: 1,
      },
    ],
    socialPosts: [
      {
        platform: 'LinkedIn',
        content: 'Exciting announcement!',
        hashtags: ['#marketing', '#ai'],
        imagePrompt: 'Professional business meeting',
      },
    ],
    summary: 'Campaign summary',
  }

  it('does not render when content is null', () => {
    const { container } = render(
      <ResultDisplay content={null} />
    )

    expect(container.firstChild).toBeNull()
  })

  it('renders with campaign results header', () => {
    render(<ResultDisplay content={mockContent} />)

    expect(screen.getByRole('heading', { name: /Campaign Intelligence/i })).toBeInTheDocument()
  })

  it('renders ad content correctly', () => {
    render(<ResultDisplay content={mockContent} />)

    expect(screen.getByText(/Ad Creatives/i)).toBeInTheDocument()
    expect(screen.getByText('Test Headline')).toBeInTheDocument()
  })

  it('renders email sequences correctly', () => {
    render(<ResultDisplay content={mockContent} />)
    expect(screen.getByText(/Email Automations/i)).toBeInTheDocument()
  })

  it('renders social posts correctly', () => {
    render(<ResultDisplay content={mockContent} />)
    expect(screen.getByText(/Social Media & Feed/i)).toBeInTheDocument()
  })

  it('calls onDownload when export button is clicked', () => {
    const mockDownload = vi.fn()
    render(
      <ResultDisplay
        content={mockContent}
        onDownload={mockDownload}
      />
    )

    const exportBtn = screen.getByRole('button', { name: /Export Campaign Brief/i })
    fireEvent.click(exportBtn)

    expect(mockDownload).toHaveBeenCalled()
  })

  it('handles empty content arrays gracefully', () => {
    const emptyContent: ContentOutput = {
      ads: [],
      emailSequences: [],
      socialPosts: [],
      summary: '',
    }

    render(<ResultDisplay content={emptyContent} />)

    expect(screen.getByText(/Ad Creatives/i)).toBeInTheDocument()
    // It should just render empty panels without crashing
    expect(screen.queryByText('Test Headline')).not.toBeInTheDocument()
  })
})
