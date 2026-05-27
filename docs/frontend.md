# Frontend Architecture

## Tech Stack

- **React 19** + TypeScript
- **Vite 6** — build tooling & dev server
- **TailwindCSS 3** — utility-first styling
- **React Query** (`@tanstack/react-query`) — server state management
- **React Router DOM 7** — client-side routing
- **Recharts** — bar chart on dashboard
- **Axios** — HTTP client
- **Vitest** + React Testing Library — tests

## Project Structure

```
frontend/src/
├── main.tsx                # Entry point — QueryClient + BrowserRouter
├── App.tsx                 # Route definitions
├── index.css               # Tailwind imports
├── components/             # Reusable UI components
│   ├── Layout.tsx          # Shell — header, nav, footer, <Outlet>
│   ├── RiskScoreBadge.tsx  # Color-coded risk score pill
│   ├── SeverityBadge.tsx   # Color-coded severity label
│   ├── StatusBadge.tsx     # Scan status indicator
│   ├── LoadingSpinner.tsx  # Spinner with message
│   ├── ErrorMessage.tsx    # Error display with retry button
│   └── Pagination.tsx      # Page navigation controls
├── pages/                  # Route-level page components
│   ├── Dashboard.tsx       # Stats cards + severity chart + recent scans
│   ├── Scans.tsx           # Paginated scan history table
│   ├── ScanDetail.tsx      # Scan detail with findings grouped by severity
│   ├── NewScan.tsx         # Upload file or paste content to scan
│   └── Guardrails.tsx      # List of configured guardrail rules
├── services/
│   └── api.ts              # Axios client — all API calls
├── types/
│   └── api.ts              # TypeScript interfaces matching backend schemas
└── test/
    ├── setup.ts            # Jest-DOM matchers + cleanup
    ├── test-utils.tsx      # TestWrapper (QueryClient + MemoryRouter)
    └── *.test.tsx           # Component tests
```

## Pages

### Dashboard (`/`)
- Summary stat cards: total scans, violations, avg risk score, critical count
- Severity bar chart (Recharts)
- Recent scans table with risk score badges

### Scan History (`/scans`)
- Paginated table with name, file, type, violations, risk, status
- Pagination controls (10 per page)
- Link to new scan page

### New Scan (`/scans/new`)
- Two modes via toggle: **Upload File** or **Paste Content**
- Upload mode: drag-to-select `.tf` file → sends to `POST /scans/upload`
- Paste mode: text area + metadata → sends to `POST /scans/`
- React Query mutations with cache invalidation

### Scan Detail (`/scans/:id`)
- Summary cards: risk score, violation count, severity breakdown
- Findings grouped by severity (critical → high → medium → low → info)
- Each finding shows message, resource, line number, remediation

### Guardrails (`/guardrails`)
- Card list of configured rules with severity badges

## Data Fetching

All pages use React Query (`useQuery` / `useMutation`):
- Automatic loading and error state handling
- Cache invalidation on mutations (new scans invalidate scan list + dashboard)
- Single retry on failure, no refetch on window focus

## API Integration

The API client in `services/api.ts` uses Axios with base URL `/api/v1`. Vite's dev server proxies `/api` requests to `http://localhost:8000`.

Key functions:
- `getDashboardSummary()` — `GET /dashboard/summary`
- `getScans(page, pageSize)` — `GET /scans/` (paginated)
- `getScan(id)` — `GET /scans/{id}`
- `createScan(payload)` — `POST /scans/`
- `uploadScan(file, name)` — `POST /scans/upload` (multipart)
- `deleteScan(id)` — `DELETE /scans/{id}`
- `getGuardrails()` — `GET /guardrails/`

## Testing

- 24 tests across 7 test files
- All reusable components have 100% coverage
- Tests use `TestWrapper` providing QueryClient + MemoryRouter
- Run: `npm test` or `npx vitest run --coverage`

## Development

```bash
cd frontend
npm install
npm run dev        # Dev server on :5173 (proxies /api to :8000)
npm test           # Run tests
npm run build      # Production build
```
