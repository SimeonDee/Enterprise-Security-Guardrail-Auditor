import axios from "axios";
import type {
    DashboardSummary,
    Guardrail,
    PaginatedResponse,
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

export const getScans = (page = 1, pageSize = 20) =>
    api
        .get<PaginatedResponse<Scan>>("/scans/", {
            params: { page, page_size: pageSize },
        })
        .then((r) => r.data);

export const getScan = (id: number) =>
    api.get<ScanDetail>(`/scans/${id}`).then((r) => r.data);

export const createScan = (payload: ScanCreatePayload) =>
    api.post<ScanDetail>("/scans/", payload).then((r) => r.data);

export const uploadScan = (file: File, name: string) => {
    const form = new FormData();
    form.append("file", file);
    return api
        .post<ScanDetail>(`/scans/upload?name=${encodeURIComponent(name)}`, form, {
            headers: { "Content-Type": "multipart/form-data" },
        })
        .then((r) => r.data);
};

export const deleteScan = (id: number) => api.delete(`/scans/${id}`);

export const getGuardrails = () =>
    api.get<Guardrail[]>("/guardrails/").then((r) => r.data);

export const getHealth = () => api.get("/health/").then((r) => r.data);

export default api;
