# AdPilot Dashboard Frontend

A modern React + TypeScript dashboard for the AdPilot marketing campaign automation platform.

## 📋 Features

- **Campaign Brief Form** – Submit marketing briefs with business details, audience, budget, and goals
- **Real-time Progress Tracking** – Live polling of campaign generation status
- **Results Display** – Tabbed view of generated ads, emails, and social posts
- **Copy & Download** – One-click copy-to-clipboard and bulk asset downloads
- **Responsive Design** – Mobile-first UI with Tailwind CSS
- **WCAG AA Compliant** – Accessible color contrasts and semantic HTML

## 🚀 Getting Started

### Prerequisites

- Node.js 16+ and npm/yarn/pnpm
- Backend API running on `http://localhost:8000`

### Installation

```bash
cd frontend
npm install
```

### Environment Setup

Create a `.env` file:

```env
VITE_API_URL=http://localhost:8000/api
```

Or use the provided `.env.example` as a template.

### Development

```bash
npm run dev
```

The app will start on `http://localhost:3000` with hot reload enabled.

### Build for Production

```bash
npm run build
npm run preview
```

## 📁 Project Structure

```
frontend/
├── public/               # Static assets
├── src/
│   ├── components/       # React components
│   │   ├── CampaignBriefForm.tsx
│   │   ├── CampaignProgress.tsx
│   │   └── ResultDisplay.tsx
│   ├── hooks/            # Custom React hooks
│   │   └── useTaskPolling.ts
│   ├── services/         # API integration
│   │   └── api.ts
│   ├── types/            # TypeScript types
│   │   └── index.ts
│   ├── App.tsx           # Main app component
│   ├── main.tsx          # Entry point
│   ├── index.css         # Global styles
│   └── App.css           # App-specific styles
├── index.html            # HTML entry point
├── package.json          # Dependencies
├── tsconfig.json         # TypeScript config
├── vite.config.ts        # Vite build config
├── tailwind.config.js    # Tailwind CSS config
└── .eslintrc.cjs         # ESLint config
```

## 🎨 Components

### CampaignBriefForm
Captures campaign requirements from users:
- Business name, product name & description
- Target audience & goals
- Budget & campaign duration
- Brand tone selection

### CampaignProgress
Shows real-time generation status:
- Status indicator (pending, in_progress, completed, failed)
- Progress bar with percentage
- Task ID and status details
- Error messages if applicable

### ResultDisplay
Displays generated campaign content:
- **Tab 1:** Ad Content (headline, body, CTA, performance)
- **Tab 2:** Email Sequences (subject, preview, body)
- **Tab 3:** Social Posts (platform, content, hashtags)
- Copy-to-clipboard and bulk download buttons

## 🔌 API Integration

The frontend communicates with the backend via RESTful endpoints:

- `POST /api/campaigns` – Submit a brief
- `GET /api/tasks/{taskId}` – Poll task status
- `GET /api/campaigns/{id}/content` – Fetch campaign results
- `GET /api/campaigns/{id}/design-assets/download` – Download design zip

See [docs/DASHBOARD.md](../docs/DASHBOARD.md) for full API specs.

## 🧪 Testing

```bash
# Run unit tests
npm run test

# Run type-checking
npm run type-check

# Lint code
npm run lint
```

## 🐳 Docker

To run the frontend in a container (typically served by the backend):

```dockerfile
# Multi-stage build
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

## 📚 Dependencies

- **React 18** – UI library
- **React Hook Form** – Form state management
- **Axios** – HTTP client
- **Tailwind CSS** – Utility-first styling
- **Lucide React** – Icon library
- **Vite** – Build tool
- **TypeScript** – Type safety
- **ESLint** – Code linting

## 🤝 Contributing

1. Create a feature branch: `git checkout -b feature/dashboard-enhancement`
2. Make changes and test thoroughly
3. Run linting and type-check: `npm run lint && npm run type-check`
4. Commit with clear messages: `git commit -m "feat: add new component"`
5. Push and open a PR for review

## 📖 Documentation

- [DASHBOARD.md](../docs/DASHBOARD.md) – Detailed architecture and state management
- [CONTENT.md](../docs/CONTENT.md) – Content generation API specs
- [USAGE.md](../docs/USAGE.md) – Full platform usage guide

## ⚡ Performance Optimizations

- Code splitting via Vite's dynamic imports
- Lazy component loading with React.lazy
- Memoization for expensive computations
- Efficient polling with cleanup on unmount
- Tailwind CSS purging (unused styles removed in production)

## 🐛 Troubleshooting

**CORS Errors?**
- Ensure the backend is running on port 8000
- Check VITE_API_URL in `.env`
- Backend must have CORS middleware enabled

**API calls failing?**
- Verify backend is healthy: `curl http://localhost:8000/api/healthz`
- Check browser DevTools Network tab for actual response

**Styling not showing?**
- Clear `node_modules` and `dist`: `rm -rf node_modules dist && npm install`
- Rebuild Tailwind cache: `npm run build`

## 📞 Support

For issues or questions, please check the main [README.md](../README.md) or contact the team.

---

**Latest Update:** May 2026  
**Maintainer:** Sleem
