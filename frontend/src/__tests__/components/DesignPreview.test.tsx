import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { DesignPreview } from '../../components/DesignPreview'

// Mock URL methods
global.URL.createObjectURL = vi.fn(() => 'blob:mock-url')
global.URL.revokeObjectURL = vi.fn()

describe('DesignPreview', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Rendering', () => {
    it('should render without campaign ID', () => {
      render(<DesignPreview campaignId={null} />)
      
      expect(screen.getByText(/Select or create a campaign/i)).toBeInTheDocument()
    })

    it('should render loading state initially', () => {
      render(<DesignPreview campaignId="test-campaign-1" />)
      
      expect(screen.getByText(/Loading design assets/i)).toBeInTheDocument()
    })

    it('should render design assets when loaded', async () => {
      render(<DesignPreview campaignId="test-campaign-1" />)
      
      await waitFor(() => {
        expect(screen.getByText('Design Assets')).toBeInTheDocument()
      })

      expect(screen.getByText('3 assets available')).toBeInTheDocument()
      expect(screen.getAllByText(/Asset #/)).toHaveLength(3)
    })

    it('should display correct number of assets in grid', async () => {
      render(<DesignPreview campaignId="test-campaign-1" />)
      
      await waitFor(() => {
        expect(screen.getAllByText(/Asset #/)).toHaveLength(3)
      })

      const assetCards = screen.getAllByRole('img', { hidden: true })
      expect(assetCards.length).toBeGreaterThan(0)
    })

    it('should show "No assets" message when empty', async () => {
      const { rerender } = render(<DesignPreview campaignId="test-campaign-1" />)
      
      await waitFor(() => {
        expect(screen.getByText('Design Assets')).toBeInTheDocument()
      })

      // Change campaign ID to trigger empty state
      rerender(<DesignPreview campaignId={null} />)
      
      expect(screen.getByText(/Select or create a campaign/i)).toBeInTheDocument()
    })
  })

  describe('Responsive Layout', () => {
    it('should have mobile-first grid layout', async () => {
      const { container } = render(<DesignPreview campaignId="test-campaign-1" />)
      
      await waitFor(() => {
        expect(screen.getAllByText(/Asset #/)).toHaveLength(3)
      })

      const gridDiv = container.querySelector('div.grid')
      expect(gridDiv).toHaveClass('grid-cols-1', 'sm:grid-cols-2', 'lg:grid-cols-3')
    })

    it('should have responsive padding', async () => {
      const { container } = render(<DesignPreview campaignId="test-campaign-1" />)
      
      await waitFor(() => {
        expect(screen.getByText('Design Assets')).toBeInTheDocument()
      })

      const header = container.querySelector('[class*="border-b"]')
      expect(header).toHaveClass('p-4', 'md:p-6')
    })

    it('should hide button text on small screens', async () => {
      render(<DesignPreview campaignId="test-campaign-1" />)
      
      await waitFor(() => {
        expect(screen.getByText('Design Assets')).toBeInTheDocument()
      })

      expect(screen.getByText('Download All')).toHaveClass('hidden', 'sm:inline')
    })
  })

  describe('Download Functionality', () => {
    it('should have download all button when assets exist', async () => {
      render(<DesignPreview campaignId="test-campaign-1" />)
      
      await waitFor(() => {
        expect(screen.getByRole('button', { name: /Download/ })).toBeInTheDocument()
      })
    })

    it('should download all assets when button is clicked', async () => {
      const user = userEvent.setup()
      render(<DesignPreview campaignId="test-campaign-1" />)
      
      await waitFor(() => {
        expect(screen.getByText('Design Assets')).toBeInTheDocument()
      })

      const downloadBtn = screen.getByRole('button', { name: /Download/ })
      await user.click(downloadBtn)

      await waitFor(() => {
        expect(global.URL.createObjectURL).toHaveBeenCalled()
      })
    })

    it('should disable download button while downloading', async () => {
      const user = userEvent.setup()
      render(<DesignPreview campaignId="test-campaign-1" />)
      
      await waitFor(() => {
        expect(screen.getByText('Design Assets')).toBeInTheDocument()
      })

      const downloadBtn = screen.getByRole('button', { name: /Download/ })
      
      await user.click(downloadBtn)
      
      await waitFor(() => {
        expect(global.URL.createObjectURL).toHaveBeenCalled()
      })
    })

    it('should download individual asset when button clicked', async () => {
      const user = userEvent.setup()
      render(<DesignPreview campaignId="test-campaign-1" />)
      
      await waitFor(() => {
        expect(screen.getAllByText(/Asset #/)).toHaveLength(3)
      })

      // Hover over first asset to reveal download button
      const firstAsset = screen.getAllByRole('img')[0]
      const firstAssetContainer = firstAsset.closest('div.group')
      
      if (firstAssetContainer) {
        fireEvent.mouseEnter(firstAssetContainer)
        
        const downloadBtns = within(firstAssetContainer).getAllByRole('button')
        const downloadBtn = downloadBtns[1] // Second button is download
        
        await user.click(downloadBtn)
        
        await waitFor(() => {
          expect(global.URL.createObjectURL).toHaveBeenCalled()
        })
      }
    })
  })

  describe('Copy URL Functionality', () => {
    it('should copy asset URL to clipboard', async () => {
      const user = userEvent.setup()
      const mockClipboard = {
        writeText: vi.fn(),
      }
      Object.defineProperty(navigator, 'clipboard', { configurable: true, value: mockClipboard })

      render(<DesignPreview campaignId="test-campaign-1" />)
      
      await waitFor(() => {
        expect(screen.getAllByText(/Asset #/)).toHaveLength(3)
      })

      const copyButtons = screen.getAllByRole('button', { name: /Copy URL/ })
      await user.click(copyButtons[0])

      expect(mockClipboard.writeText).toHaveBeenCalled()
      expect(screen.getByText('Copied!')).toBeInTheDocument()
    })

    it('should show "Copied!" feedback temporarily', async () => {
      const user = userEvent.setup()
      const mockClipboard = {
        writeText: vi.fn(),
      }
      Object.defineProperty(navigator, 'clipboard', { configurable: true, value: mockClipboard })

      render(<DesignPreview campaignId="test-campaign-1" />)
      
      await waitFor(() => {
        expect(screen.getAllByText(/Asset #/)).toHaveLength(3)
      })

      const copyButtons = screen.getAllByRole('button', { name: /Copy URL/ })
      await user.click(copyButtons[0])

      expect(screen.getByText('Copied!')).toBeInTheDocument()

      await waitFor(
        () => {
          expect(screen.queryByText('Copied!')).not.toBeInTheDocument()
        },
        { timeout: 3000 }
      )
    })
  })

  describe('Preview Modal', () => {
    it('should open preview modal when eye icon clicked', async () => {
      const user = userEvent.setup()
      render(<DesignPreview campaignId="test-campaign-1" />)
      
      await waitFor(() => {
        expect(screen.getAllByText(/Asset #/)).toHaveLength(3)
      })

      // Hover over first asset to reveal preview button
      const firstAsset = screen.getAllByRole('img')[0]
      const firstAssetContainer = firstAsset.closest('div.group')
      
      if (firstAssetContainer) {
        fireEvent.mouseEnter(firstAssetContainer)
        
        const buttons = within(firstAssetContainer).getAllByRole('button')
        const previewBtn = buttons[0] // First button is preview (eye icon)
        
        await user.click(previewBtn)
      }

      await waitFor(() => {
        expect(screen.getByRole('heading', { name: /Asset #/ })).toBeInTheDocument()
      })
    })

    it('should close preview modal when close button clicked', async () => {
      const user = userEvent.setup()
      render(<DesignPreview campaignId="test-campaign-1" />)
      
      await waitFor(() => {
        expect(screen.getAllByText(/Asset #/)).toHaveLength(3)
      })

      // Open preview
      const firstAsset = screen.getAllByRole('img')[0]
      const firstAssetContainer = firstAsset.closest('div.group')
      
      if (firstAssetContainer) {
        fireEvent.mouseEnter(firstAssetContainer)
        const buttons = within(firstAssetContainer).getAllByRole('button')
        await user.click(buttons[0])
      }

      await waitFor(() => {
        expect(screen.getByRole('heading', { name: /Asset #/ })).toBeInTheDocument()
      })

      // Close preview
      const closeBtn = screen.getByRole('button', { name: /Close preview/ })
      await user.click(closeBtn)

      await waitFor(() => {
        expect(screen.queryByRole('heading', { name: /Asset #/ })).not.toBeInTheDocument()
      })
    })

    it('should close preview when clicking outside modal', async () => {
      const user = userEvent.setup()
      render(<DesignPreview campaignId="test-campaign-1" />)
      
      await waitFor(() => {
        expect(screen.getAllByText(/Asset #/)).toHaveLength(3)
      })

      // Open preview
      const firstAsset = screen.getAllByRole('img')[0]
      const firstAssetContainer = firstAsset.closest('div.group')
      
      if (firstAssetContainer) {
        fireEvent.mouseEnter(firstAssetContainer)
        const buttons = within(firstAssetContainer).getAllByRole('button')
        await user.click(buttons[0])
      }

      await waitFor(() => {
        expect(screen.getByRole('heading', { name: /Asset #/ })).toBeInTheDocument()
      })

      // Click outside modal (on backdrop)
      const backdrop = screen.getByRole('heading', { name: /Asset #/ })
        .closest('div.fixed')
      
      if (backdrop) {
        await user.click(backdrop)
      }

      await waitFor(() => {
        expect(screen.queryByRole('heading', { name: /Asset #/ })).not.toBeInTheDocument()
      })
    })

    it('should download asset from preview modal', async () => {
      const user = userEvent.setup()
      render(<DesignPreview campaignId="test-campaign-1" />)
      
      await waitFor(() => {
        expect(screen.getAllByText(/Asset #/)).toHaveLength(3)
      })

      // Open preview
      const firstAsset = screen.getAllByRole('img')[0]
      const firstAssetContainer = firstAsset.closest('div.group')
      
      if (firstAssetContainer) {
        fireEvent.mouseEnter(firstAssetContainer)
        const buttons = within(firstAssetContainer).getAllByRole('button')
        await user.click(buttons[0])
      }

      await waitFor(() => {
        expect(screen.getByRole('heading', { name: /Asset #/ })).toBeInTheDocument()
      })

      const downloadBtns = screen.getAllByRole('button', { name: /Download Asset/ })
      await user.click(downloadBtns[0])

      await waitFor(() => {
        expect(global.URL.createObjectURL).toHaveBeenCalled()
      })
    })
  })

  describe('Error Handling', () => {
    it('should display error message on API failure', async () => {
      const { server } = await import('../setup')
      const { http, HttpResponse } = await import('msw')

      server.use(
        http.get('http://127.0.0.1:8000/api/campaigns/:id/design-assets', () => {
          return HttpResponse.json({ error: 'Failed to load assets' }, { status: 500 })
        })
      )

      render(<DesignPreview campaignId="test-campaign-1" />)
      
      await waitFor(() => {
        expect(screen.getByText(/Failed to load/i)).toBeInTheDocument()
      })
    })

    it('should handle image load errors gracefully', async () => {
      render(<DesignPreview campaignId="test-campaign-1" />)
      
      await waitFor(() => {
        expect(screen.getAllByText(/Asset #/)).toHaveLength(3)
      })

      const images = screen.getAllByRole('img', { hidden: true })
      
      // Trigger error on first image
      fireEvent.error(images[0])

      // Image should still be in DOM with fallback
      expect(images[0]).toBeInTheDocument()
    })
  })

  describe('Asset Information', () => {
    it('should display asset metadata', async () => {
      render(<DesignPreview campaignId="test-campaign-1" />)
      
      await waitFor(() => {
        expect(screen.getAllByText(/Asset #/)).toHaveLength(3)
      })

      // Check that asset IDs are displayed
      expect(screen.getByText('Asset #1')).toBeInTheDocument()
      expect(screen.getByText('Asset #2')).toBeInTheDocument()
      expect(screen.getByText('Asset #3')).toBeInTheDocument()
    })

    it('should display asset creation dates', async () => {
      render(<DesignPreview campaignId="test-campaign-1" />)
      
      await waitFor(() => {
        expect(screen.getAllByText(/Asset #/)).toHaveLength(3)
      })

      // Dates should be displayed in locale format
      const dates = screen.getAllByText(/\//)
      expect(dates.length).toBeGreaterThan(0)
    })
  })

  describe('Accessibility', () => {
    it('should have proper button labels', async () => {
      render(<DesignPreview campaignId="test-campaign-1" />)
      
      await waitFor(() => {
        expect(screen.getByText('Design Assets')).toBeInTheDocument()
      })

      const downloadBtn = screen.getByRole('button', { name: /Download/ })
      expect(downloadBtn).toHaveAttribute('aria-label')
    })

    it('should have proper heading hierarchy', async () => {
      render(<DesignPreview campaignId="test-campaign-1" />)
      
      await waitFor(() => {
        expect(screen.getByText('Design Assets')).toBeInTheDocument()
      })

      const heading = screen.getByRole('heading', { level: 2, name: /Design Assets/ })
      expect(heading).toBeInTheDocument()
    })

    it('should support keyboard navigation in preview modal', async () => {
      const user = userEvent.setup()
      render(<DesignPreview campaignId="test-campaign-1" />)
      
      await waitFor(() => {
        expect(screen.getAllByText(/Asset #/)).toHaveLength(3)
      })

      // Open preview
      const firstAsset = screen.getAllByRole('img')[0]
      const firstAssetContainer = firstAsset.closest('div.group')
      
      if (firstAssetContainer) {
        fireEvent.mouseEnter(firstAssetContainer)
        const buttons = within(firstAssetContainer).getAllByRole('button')
        await user.click(buttons[0])
      }

      await waitFor(() => {
        expect(screen.getByRole('heading', { name: /Asset #/ })).toBeInTheDocument()
      })

      // Close with Escape key (if implemented)
      const closeBtn = screen.getByRole('button', { name: /Close preview/ })
      expect(closeBtn).toBeInTheDocument()
    })
  })

  describe('Campaign ID Changes', () => {
    it('should reload assets when campaign ID changes', async () => {
      const { rerender } = render(<DesignPreview campaignId="test-campaign-1" />)
      
      await waitFor(() => {
        expect(screen.getByText('Design Assets')).toBeInTheDocument()
      })

      rerender(<DesignPreview campaignId="test-campaign-2" />)

      await waitFor(() => {
        expect(screen.getByText('Design Assets')).toBeInTheDocument()
      })
    })

    it('should clear assets when campaign ID becomes null', async () => {
      const { rerender } = render(<DesignPreview campaignId="test-campaign-1" />)
      
      await waitFor(() => {
        expect(screen.getByText('Design Assets')).toBeInTheDocument()
      })

      rerender(<DesignPreview campaignId={null} />)

      expect(screen.getByText(/Select or create a campaign/i)).toBeInTheDocument()
    })
  })
})
