import { describe, it, expect, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { CampaignBriefForm } from '../../components/CampaignBriefForm'
import { campaignService } from '../../services/api'

describe('CampaignBriefForm', () => {
  it('renders form with all required fields', () => {
    const mockSubmit = vi.fn()
    render(<CampaignBriefForm onSubmit={mockSubmit} />)

    expect(screen.getByText('Campaign Brief')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('e.g. FutureCorp')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('e.g. NeuralLink v2')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('Value proposition & key features...')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('e.g. Tech enthusiasts, early adopters')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Initialize Campaign Generation/i })).toBeInTheDocument()
  })

  it('validates required fields', async () => {
    const user = userEvent.setup()
    const mockSubmit = vi.fn()
    render(<CampaignBriefForm onSubmit={mockSubmit} />)

    const submitButton = screen.getByRole('button', { name: /Initialize Campaign Generation/i })
    await user.click(submitButton)

    // wait for form validation to prevent submission
    await waitFor(() => {
      expect(mockSubmit).not.toHaveBeenCalled()
    })
  })

  it('submits form with valid data', async () => {
    const user = userEvent.setup()
    const mockSubmit = vi.fn()
    render(<CampaignBriefForm onSubmit={mockSubmit} />)

    const businessInput = screen.getByPlaceholderText('e.g. FutureCorp')
    const productInput = screen.getByPlaceholderText('e.g. NeuralLink v2')
    const descInput = screen.getByPlaceholderText('Value proposition & key features...')
    const audienceInput = screen.getByPlaceholderText('e.g. Tech enthusiasts, early adopters')
    const budgetInput = screen.getByRole('spinbutton')

    await user.type(businessInput, 'Test Business')
    await user.type(productInput, 'Test Product')
    await user.type(descInput, 'A great product')
    await user.type(audienceInput, 'Young professionals')
    await user.type(budgetInput, '5000')

    // Select duration (now defaults to 1-week, or we select 2-weeks)
    const durationSelect = screen.getByRole('combobox')
    await user.selectOptions(durationSelect, '2-weeks')

    const submitButton = screen.getByRole('button', { name: /Initialize Campaign Generation/i })
    await user.click(submitButton)

    await waitFor(() => {
      expect(mockSubmit).toHaveBeenCalled()
    })
  })

  it('displays error message on submission failure', async () => {
    const user = userEvent.setup()
    const mockSubmit = vi.fn()
    vi.spyOn(campaignService, 'submitCampaign').mockRejectedValueOnce(new Error('API error'))
    render(<CampaignBriefForm onSubmit={mockSubmit} />)

    const businessInput = screen.getByPlaceholderText('e.g. FutureCorp')
    const productInput = screen.getByPlaceholderText('e.g. NeuralLink v2')
    const descInput = screen.getByPlaceholderText('Value proposition & key features...')
    const audienceInput = screen.getByPlaceholderText('e.g. Tech enthusiasts, early adopters')
    const budgetInput = screen.getByRole('spinbutton')

    await user.type(businessInput, 'Test Business')
    await user.type(productInput, 'Test Product')
    await user.type(descInput, 'A great product')
    await user.type(audienceInput, 'Young professionals')
    await user.type(budgetInput, '5000')

    const durationSelect = screen.getByRole('combobox')
    await user.selectOptions(durationSelect, '2-weeks')

    const submitButton = screen.getByRole('button', { name: /Initialize Campaign Generation/i })
    await user.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/API error/)).toBeInTheDocument()
    })
  })

  it('disables submit button while loading', async () => {
    const mockSubmit = vi.fn()
    const { rerender } = render(<CampaignBriefForm onSubmit={mockSubmit} isLoading={false} />)

    let submitButton = screen.getByRole('button', { name: /Initialize Campaign Generation/i })
    expect(submitButton).not.toBeDisabled()

    rerender(<CampaignBriefForm onSubmit={mockSubmit} isLoading={true} />)

    submitButton = screen.getByRole('button', { name: /Initialize Campaign Generation/i })
    expect(submitButton).toBeDisabled()
  })
})
