Wireframes and mock provider

Files added under `frontend/src/components/wireframes/` are low-fidelity SVGs for key screens:
- `DashboardWireframe.svg`
- `NewCampaignWireframe.svg`
- `CampaignDetailsWireframe.svg`
- `DesignPreviewWireframe.svg`
- `AssetsWireframe.svg`
- `SettingsWireframe.svg`

Mock provider:
- `frontend/src/services/mockProvider.ts` exports simple async functions to submit campaigns, poll task status, fetch content, list assets, and download a dummy zip. Use this during UI development to avoid hitting backend.

Component props:
- `frontend/src/components/props.ts` contains TypeScript interfaces for primary components (CampaignFormProps, TaskListProps, AssetCardProps, etc.)

How to preview pages:
- You can import the pages into `App.tsx` or a routes file and navigate to them. Example quick test in `App.tsx`:

```tsx
import { DashboardPage } from './pages/DashboardPage'
// render <DashboardPage /> in main content area
```

Next steps:
- Wire the `mockProvider` into context or replace `campaignService` exports when running locally.
- Replace SVGs with interactive components when ready.
