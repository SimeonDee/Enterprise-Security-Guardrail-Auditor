import axios from "axios";
import type {
    DashboardSummary,
    Guardrail,
    Scan,
    ScanCreatePayload,
    ScanDetail,
} from "../types/api";

const api = axios.create({
    baseURL: "/api/v1",
    headers: { "Content-Type": "application/json" },
});

export const getDashboardSummary = () =>
    api.get<DashboardSummary>("/dashboard/summary").then((r) => r.data);

export const getScans = () =>
    api.get<Scan[]>("/scans/").then((r) => r.data);

export const getScan = (id: number) =>
    api.get<ScanDetail>(`/scans/${id}`).then((r) => r.data);

export const createScan = (payload: ScanCreatePayload) =>
    api.post<ScanDetail>("/scans/", payload).then((r) => r.data);

export const deleteScan = (id: number) =>
    api.delete(`/scans/${id}`);

export const getGuardrails = () =>
    api.get<Guardrail[]>("/guardrails/").then((r) => r.data);

export const getHealth = () =>
    api.get("/health/").then((r) => r.data);

export default api;
