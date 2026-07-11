# Phase 2 Quick Start Guide

## 🚀 Getting Started (5 minutes)

### Backend Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Add your OpenAI API key:
   # OPENAI_API_KEY=<your-openai-key>
   ```

3. **Start the FastAPI server:**
   ```bash
   cd src
   uvicorn adpilot.api.main:app --reload --host 0.0.0.0 --port 8000
   ```

   ✅ API should be running on `http://localhost:8000`
   - OpenAPI docs: `http://localhost:8000/docs`
   - Health check: `http://localhost:8000/healthz`

### Frontend Setup

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Start development server:**
   ```bash
   npm run dev
   ```

   ✅ Dashboard should be running on `http://localhost:3000`

3. **Run tests:**
   ```bash
   npm test
   ```

## 📋 Workflow: Submit a Campaign

### 1. Open Dashboard
Navigate to `http://localhost:3000`

### 2. Fill Campaign Brief
```
Business Name:        TechCorp
Product Name:         CloudSync
Product Description:  Enterprise cloud synchronization
Target Audience:      IT managers
Budget:               $50,000
Duration:             3 months
Tone:                 Professional
```

### 3. Click "Generate Campaign"
- Task ID assigned
- Progress bar shows real-time status
- Backend generates content using Content Agent

### 4. View Results
Once completed (status = "completed"):
- **Ads Tab:** Platform-specific ad copy
- **Emails Tab:** Email sequence with subjects and body
- **Social Tab:** Social media posts with hashtags

### 5. Download Assets
Click "Download Assets" to get ZIP with all campaign materials

---

## 🔧 Key Files to Know

### Backend

| File | Purpose |
|------|---------|
| `src/adpilot/api/main.py` | FastAPI app & endpoints |
| `src/adpilot/agents/content_agent.py` | LLM content generation |
| `src/adpilot/services/llm_client.py` | OpenAI wrapper with retry logic |
| `src/adpilot/services/task_manager.py` | Task tracking |
| `src/adpilot/core/config.py` | Configuration loading |

### Frontend

| File | Purpose |
|------|---------|
| `frontend/src/App.tsx` | Main app component |
| `frontend/src/components/CampaignBriefForm.tsx` | Form input |
| `frontend/src/components/CampaignProgress.tsx` | Status tracker |
| `frontend/src/components/ResultDisplay.tsx` | Results viewer |
| `frontend/src/services/api.ts` | API client |
| `frontend/src/hooks/useTaskPolling.ts` | Status polling |

---

## 📚 API Endpoints

### Submit Campaign (POST)
```bash
curl -X POST http://localhost:8000/api/campaigns \
  -H "Content-Type: application/json" \
  -d '{
    "businessName": "TechCorp",
    "productName": "CloudSync",
    "productDescription": "...",
    "targetAudience": "...",
    "goals": ["..."],
    "budget": 50000,
    "duration": "3-months",
    "tone": "professional"
  }'
```

### Check Task Status (GET)
```bash
curl http://localhost:8000/api/tasks/{taskId}
```

### Get Campaign Content (GET)
```bash
curl http://localhost:8000/api/campaigns/{campaignId}/content
```

---

## 🧪 Testing

### Backend
```bash
# Run tests
pytest -q

# With coverage
pytest --cov=src
```

### Frontend
```bash
# Run component tests
npm test

# Watch mode
npm test -- --watch

# Coverage
npm coverage
```

---

## 🐛 Troubleshooting

### "CORS Error" or "Failed to fetch"
- ✅ Backend running on port 8000?
- ✅ Check `VITE_API_URL` in `frontend/.env`
- ✅ Backend has CORS middleware enabled

### "OpenAI API key not found"
- ✅ Add `OPENAI_API_KEY` to `.env` file
- ✅ Restart backend: `Ctrl+C` then `uvicorn ...`

### Frontend won't build
```bash
rm -rf node_modules dist
npm install
npm run build
```

### Tests failing
```bash
# Clear cache and reinstall
npm install  # frontend
pip install -r requirements.txt  # backend
```

---

## 📖 Documentation

- **[Content Agent Guide](./CONTENT.md)** – LLM integration, prompts, testing
- **[Dashboard Guide](./DASHBOARD.md)** – React components, architecture, state management
- **[Full README](../README.md)** – Project overview, features, deployment
- **[Usage Guide](./USAGE.md)** – End-to-end platform usage examples

---

## 🎯 Next Steps

1. ✅ **Phase 2.1:** Complete Content Agent LLM integration (YOU ARE HERE)
2. ⏳ **Phase 2.2:** Implement Orchestrator for multi-agent pipeline
3. ⏳ **Phase 2.3:** Add persistent database storage
4. ⏳ **Phase 2.4:** Extend API with more endpoints
5. ⏳ **Phase 2.5:** Polish React dashboard UI
6. ⏳ **Phase 2.6:** CI/CD pipeline setup

---

## ⚡ Common Commands

```bash
# Backend
uvicorn adpilot.api.main:app --reload          # Start server
pytest -q                                       # Run tests
pip install -r requirements.txt                # Install deps

# Frontend
npm run dev                                     # Dev server
npm test                                        # Tests
npm run build                                   # Production build
npm run lint                                    # Check code style
npm run type-check                              # Type validation
```

---

## 💡 Tips

- Use FastAPI docs at `/docs` for interactive API testing
- Enable React DevTools browser extension for debugging
- Check browser console for frontend errors
- Check terminal output for backend errors
- Use `CONTENT_TEMPERATURE=0.5` for more consistent output

---

## 📞 Need Help?

Check the documentation files in `docs/`:
- Content generation issues → `CONTENT.md`
- Frontend/UI issues → `DASHBOARD.md`
- General questions → `README.md` or `USAGE.md`

---

**Last Updated:** May 2026  
**Maintainer:** Sleem
