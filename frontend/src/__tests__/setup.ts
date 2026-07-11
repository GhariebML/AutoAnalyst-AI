import '@testing-library/jest-dom'
import { afterAll, afterEach, beforeAll } from 'vitest'
import { setupServer } from 'msw/node'
import { http, HttpResponse } from 'msw'

Object.defineProperty(navigator, 'clipboard', {
  configurable: true,
  writable: true,
  value: {
    writeText: () => Promise.resolve(),
  },
})

HTMLAnchorElement.prototype.click = () => {}

// Mock API server setup
const server = setupServer(
  // POST /api/campaigns
  http.post('http://127.0.0.1:8000/api/campaigns', () => {
    return HttpResponse.json(
      {
        taskId: 'test-task-123',
        status: 'pending',
        progress: 0,
        message: 'Campaign generation queued',
      },
      { status: 202 }
    )
  }),

  // GET /api/tasks/:taskId
  http.get('http://127.0.0.1:8000/api/tasks/:taskId', ({ params }) => {
    return HttpResponse.json({
      taskId: params.taskId,
      status: 'in_progress',
      progress: 50,
      message: 'Campaign generation in progress',
    })
  }),

  // GET /api/campaigns/:id/content
  http.get('http://127.0.0.1:8000/api/campaigns/:id/content', () => {
    return HttpResponse.json({
      ads: [
        {
          platform: 'Facebook',
          headline: 'Test Ad',
          body: 'Test body',
          cta: 'Click here',
          performance: 'Expected CTR: 3.2%',
        },
      ],
      emailSequences: [
        {
          subject: 'Test Email',
          preview: 'Test preview',
          body: 'Test body',
          sequence: 1,
        },
      ],
      socialPosts: [
        {
          platform: 'LinkedIn',
          content: 'Test post',
          hashtags: ['#test', '#demo'],
        },
      ],
      summary: 'Test summary',
    })
  }),

  // GET /api/campaigns/:id/design-assets
  http.get('http://127.0.0.1:8000/api/campaigns/:id/design-assets', () => {
    return HttpResponse.json({
      assets: [
        {
          id: 1,
          campaign_id: 'test-campaign-1',
          brief_json: { color: 'blue', mood: 'professional' },
          image_url: 'https://picsum.photos/600/400?random=1',
          created_at: '2024-01-15T10:00:00Z',
        },
        {
          id: 2,
          campaign_id: 'test-campaign-1',
          brief_json: { color: 'red', mood: 'energetic' },
          image_url: 'https://picsum.photos/600/400?random=2',
          created_at: '2024-01-15T10:05:00Z',
        },
        {
          id: 3,
          campaign_id: 'test-campaign-1',
          brief_json: { color: 'green', mood: 'eco' },
          image_url: 'https://picsum.photos/600/400?random=3',
          created_at: '2024-01-15T10:10:00Z',
        },
      ],
      total: 3,
    })
  }),

  // GET /api/campaigns/:id/design-assets/download
  http.get('http://127.0.0.1:8000/api/campaigns/:id/design-assets/download', () => {
    const blobContent = new ArrayBuffer(100)
    return HttpResponse.arrayBuffer(blobContent, {
      headers: {
        'Content-Type': 'application/zip',
      },
    })
  }),

  // GET /api/design-assets/:id/download
  http.get('http://127.0.0.1:8000/api/design-assets/:id/download', () => {
    const blobContent = new ArrayBuffer(50)
    return HttpResponse.arrayBuffer(blobContent, {
      headers: {
        'Content-Type': 'image/png',
      },
    })
  })

)

beforeAll(() => server.listen({ onUnhandledRequest: 'error' }))
afterEach(() => server.resetHandlers())
afterAll(() => server.close())

export { server }
