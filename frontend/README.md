# Frontend — Enterprise Security Guardrail Auditor

React single-page application providing the security dashboard, scan management, and guardrail configuration UI.

## Tech Stack

- **React 19** with functional components and hooks
- **Vite 6** — build tool with HMR
- **TypeScript** — strict type checking
- **Tailwind CSS 3** — utility-first styling
- **Recharts** — data visualization (severity charts)
- **React Query** (`@tanstack/react-query`) — server state management
- **React Router DOM 7** — client-side routing
- **Axios** — HTTP client

## Setup

```bash
npm ci
```

## Run

```bash
npm run dev       # Development server with HMR → http://localhost:5173
npm run build     # Production build
npm run preview   # Preview production build
```

## Test

```bash
npm test          # Run all tests (Vitest + RTL)
npm run test:watch  # Watch mode
```

24 tests across 7 test files, components at 100% coverage.

## Pages

| Page | Route | Description |
|------|-------|-------------|
| Dashboard | `/` | Stats cards, severity bar chart, recent scans |
| Scans | `/scans` | Paginated scan history table |
| New Scan | `/scans/new` | Upload `.tf` file or paste content |
| Scan Detail | `/scans/:id` | Findings grouped by severity, risk score badge |
| Guardrails | `/guardrails` | Security rule management |

## Components

| Component | Purpose |
|-----------|---------|
| `Layout` | Page shell with navigation header |
| `RiskScoreBadge` | Color-coded risk score indicator (green/yellow/red) |
| `SeverityBadge` | Severity label with color coding |
| `StatusBadge` | Scan status indicator |
| `Pagination` | Page navigation with prev/next |
| `LoadingSpinner` | Loading state indicator |
| `ErrorMessage` | Error display with retry button |

## Architecture

```
src/
├── components/          # Reusable UI components
│   ├── Layout.tsx
│   ├── RiskScoreBadge.tsx
│   ├── SeverityBadge.tsx
│   ├── StatusBadge.tsx
│   ├── Pagination.tsx
│   ├── LoadingSpinner.tsx
│   └── ErrorMessage.tsx
├── pages/               # Route-level pages
│   ├── Dashboard.tsx
│   ├── Scans.tsx
│   ├── ScanDetail.tsx
│   ├── NewScan.tsx
│   └── Guardrails.tsx
├── services/
│   └── api.ts           # Axios client + typed API functions
├── types/
│   └── api.ts           # TypeScript interfaces
├── test/
│   └── test-utils.tsx   # TestWrapper (QueryClient + MemoryRouter)
├── App.tsx              # Route definitions
└── main.tsx             # Entry point (React Query + Router providers)
```

## Data Flow

```
User Action → React Query Mutation/Query → Axios → Backend API
                    ↓
            Cache + UI State Update → Re-render
```

- **Queries** (`useQuery`): Dashboard stats, scan list, scan detail, guardrails
- **Mutations** (`useMutation`): Create scan, upload file, delete scan
- **Pagination**: Controlled by `page` state, passed to `getScans(page)`

## API Integration

All API calls go through `src/services/api.ts`:

```typescript
getScans(page, pageSize)     // Paginated scan list
getScan(id)                  // Scan detail + violations
createScan(payload)          // JSON scan creation
uploadScan(file, name)       // Multipart file upload
deleteScan(id)               // Delete scan
getGuardrails()              // List all rules
getDashboardSummary()        // Aggregated dashboard stats
```

## Styling

Tailwind CSS 3 utility classes throughout. No custom CSS files. Responsive grid layouts for dashboard and scan pages.
