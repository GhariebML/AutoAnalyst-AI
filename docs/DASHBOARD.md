# AdPilot Dashboard Documentation

## Overview

The AdPilot Dashboard is a modern React + TypeScript web application that provides a user-friendly interface for submitting marketing campaign briefs and viewing generated campaign assets.

## Architecture

### Tech Stack

- **Frontend Framework:** React 18 with TypeScript
- **Build Tool:** Vite (fast development server)
- **Styling:** Tailwind CSS
- **Form Management:** React Hook Form
- **HTTP Client:** Axios
- **Testing:** Vitest + React Testing Library
- **Icons:** Lucide React

### Project Structure

```
frontend/
├── src/
│   ├── components/           # React components
│   │   ├── CampaignBriefForm.tsx
│   │   ├── CampaignProgress.tsx
│   │   └── ResultDisplay.tsx
│   ├── hooks/                # Custom React hooks
│   │   └── useTaskPolling.ts
│   ├── services/             # API integration
│   │   └── api.ts
│   ├── types/                # TypeScript interfaces
│   │   └── index.ts
│   ├── __tests__/            # Test files
│   │   ├── setup.ts
│   │   └── components/
│   ├── App.tsx               # Main app component
│   └── main.tsx              # Entry point
├── index.html                # HTML entry point
├── vite.config.ts            # Vite configuration
├── vitest.config.ts          # Vitest configuration
└── tsconfig.json             # TypeScript config
```

## Components

### CampaignBriefForm

Collects campaign requirements from users.

**Props:**
```typescript
interface CampaignBriefFormProps {
  onSubmit: (taskId: string) => void;
  isLoading?: boolean;
}
```

**Features:**
- Form validation using React Hook Form
- Required fields: Business name, product name, description, target audience, budget, duration, tone
- Error messages for invalid inputs
- Submit button disabled during loading
- API error handling with user-friendly messages

**Example:**
```typescript
<CampaignBriefForm
  onSubmit={(taskId) => console.log('Task:', taskId)}
  isLoading={false}
/>
```

### CampaignProgress

Displays real-time campaign generation progress.

**Props:**
```typescript
interface CampaignProgressProps {
  status: TaskResponse | null;
  isLoading: boolean;
  error: string | null;
}
```

**Features:**
- Status icons (pending, in_progress, completed, failed)
- Progress bar with percentage
- Real-time updates via polling
- Error message display
- Task ID tracking

**Example:**
```typescript
const { status, loading, error } = useTaskPolling(taskId);

<CampaignProgress
  status={status}
  isLoading={loading}
  error={error}
/>
```

### ResultDisplay

Shows generated campaign assets in a tabbed interface.

**Props:**
```typescript
interface ResultDisplayProps {
  content: ContentOutput | null;
  campaignId: string;
  onDownload?: () => void;
}
```

**Features:**
- Three tabs: Ads, Email Sequences, Social Posts
- Copy-to-clipboard for each asset
- Platform badges for easy identification
- Download button for bulk asset export
- Responsive grid layout

**Example:**
```typescript
<ResultDisplay
  content={results}
  campaignId={campaignId}
  onDownload={handleDownload}
/>
```

## Custom Hooks

### useTaskPolling

Polls the backend for task status updates.

**Usage:**
```typescript
const { status, loading, error } = useTaskPolling(taskId, 5000);
```

**Parameters:**
- `taskId`: Task ID (null to disable polling)
- `interval`: Polling interval in milliseconds (default: 5000)

**Returns:**
```typescript
{
  status: TaskResponse | null,      // Current task status
  loading: boolean,                 // Is polling active
  error: string | null              // Error message if any
}
```

**Behavior:**
- Auto-stops polling when task completes or fails
- Auto-cleans up interval on unmount
- Skips polling if taskId is null

## API Integration

The dashboard communicates with the backend via REST endpoints. See the `src/services/api.ts` file for implementation.

### Endpoints

#### Submit Campaign
**POST /api/campaigns**
```typescript
campaignService.submitCampaign(brief: CampaignBrief): Promise<TaskResponse>
```

#### Get Task Status
**GET /api/tasks/{taskId}**
```typescript
campaignService.getTaskStatus(taskId: string): Promise<TaskResponse>
```

#### Get Campaign Content
**GET /api/campaigns/{campaignId}/content**
```typescript
campaignService.getCampaignContent(campaignId: string): Promise<ContentOutput>
```

#### Download Assets
**GET /api/campaigns/{campaignId}/design-assets/download**
```typescript
campaignService.downloadDesignAssets(campaignId: string): Promise<Blob>
```

## State Management

The dashboard uses **React hooks** for state management:

- `useState` – Local component state
- `useEffect` – Side effects and polling
- `useTaskPolling` – Task status polling hook
- React Hook Form – Form state and validation

For complex scenarios, consider adding:
- **React Query** – Server state caching and synchronization
- **Zustand** – Lightweight global state
- **Redux Toolkit** – Complex state management

## Styling

### Tailwind CSS

All components use Tailwind CSS utility classes for styling. Key design tokens:

- **Colors:** Blue (primary), Purple (secondary), Gray (neutral)
- **Spacing:** 4px base unit (p-4 = 16px)
- **Typography:** System fonts with fallbacks
- **Responsiveness:** Mobile-first breakpoints (sm, md, lg, xl)

### Accessibility (WCAG AA)

- Color contrast ratios ≥ 4.5:1 for text
- Semantic HTML (button, form, fieldset)
- ARIA labels where needed
- Keyboard navigation support
- Focus indicators on interactive elements

## Testing

### Setup

Tests use **Vitest** + **React Testing Library** + **MSW** (Mock Service Worker).

```bash
# Run all tests
npm test

# Run with UI
npm test:ui

# Generate coverage report
npm coverage
```

### Test Structure

```typescript
describe('ComponentName', () => {
  it('should render with correct content', () => {
    render(<ComponentName />)
    expect(screen.getByText('expected text')).toBeInTheDocument()
  })

  it('should handle user interactions', async () => {
    const user = userEvent.setup()
    render(<ComponentName />)
    await user.click(screen.getByRole('button'))
    expect(handleClick).toHaveBeenCalled()
  })
})
```

### Mock API Server (MSW)

All API calls are mocked in `src/__tests__/setup.ts` using MSW. This allows tests to run without a backend server.

## Getting Started

### Prerequisites

- Node.js 16+
- npm or pnpm

### Installation

```bash
cd frontend
npm install
```

### Development Server

```bash
npm run dev
```

Open http://localhost:3000 in your browser. Vite provides hot module replacement (HMR) for instant updates.

### Build for Production

```bash
npm run build
```

Outputs optimized static files to `dist/` directory.

### Type Checking

```bash
npm run type-check
```

Validates TypeScript without emitting JavaScript.

### Linting

```bash
npm run lint
```

Checks code style using ESLint.

## Environment Variables

Create a `.env` file:

```env
VITE_API_URL=http://localhost:8000/api
```

Prefix env variables with `VITE_` to expose them to the frontend.

## Deployment

### Static Hosting (Netlify, Vercel, etc.)

1. Build: `npm run build`
2. Deploy `dist/` folder to static host
3. Configure API_URL for production backend

### Docker

```dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Integration with FastAPI Backend

The FastAPI backend can serve the frontend:

```python
from fastapi.staticfiles import StaticFiles

app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static")
```

## Common Issues

### CORS Errors

**Problem:** Requests blocked by browser CORS policy.

**Solution:**
1. Ensure backend has CORS middleware enabled
2. Check VITE_API_URL matches backend host
3. Verify backend allows frontend origin

### API Calls Failing

**Problem:** 404 or connection errors.

**Solution:**
1. Confirm backend is running: `curl http://localhost:8000/healthz`
2. Check API endpoint paths in `src/services/api.ts`
3. Verify network tab in browser DevTools

### Build Fails

**Problem:** TypeScript or ESLint errors.

**Solution:**
```bash
rm -rf node_modules dist
npm install
npm run type-check
npm run lint
```

## Performance Optimization

- **Code Splitting:** Vite automatically splits chunks
- **Image Optimization:** Use native `<img>` with srcset
- **CSS:** Tailwind CSS purges unused styles
- **Lazy Loading:** Use React.lazy for route splitting
- **Caching:** Configure service worker for offline support

## Contributing

1. Create feature branch: `git checkout -b feature/dashboard-enhancement`
2. Make changes and test: `npm test`
3. Lint and type-check: `npm run lint && npm run type-check`
4. Commit: `git commit -m "feat: description"`
5. Push and open PR

## Resources

- [React Documentation](https://react.dev)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [Vite Guide](https://vitejs.dev/guide/)
- [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/)

---

**Last Updated:** May 2026  
**Maintainer:** Sleem
