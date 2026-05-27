export interface DashboardSummary {
    total_scans: number;
    total_violations: number;
    average_risk_score: number;
    critical_count: number;
    high_count: number;
    medium_count: number;
    low_count: number;
    recent_scans: ScanBrief[];
}

export interface ScanBrief {
    id: number;
    name: string;
    risk_score: number;
    total_violations: number;
    status: string;
    created_at: string;
}

export interface Scan {
    id: number;
    name: string;
    status: string;
    file_type: string;
    file_name: string;
    total_violations: number;
    risk_score: number;
    created_at: string;
    completed_at: string | null;
}

export interface ScanDetail extends Scan {
    source_content: string;
    violations: Violation[];
}

export interface Violation {
    id: number;
    scan_id: number;
    guardrail_id: number | null;
    resource_name: string;
    file_path: string;
    line_number: number | null;
    severity: string;
    message: string;
    remediation: string;
    created_at: string;
}

export interface Guardrail {
    id: number;
    name: string;
    description: string;
    severity: string;
    provider: string;
    resource_type: string;
    pattern: string;
    remediation: string;
    enabled: boolean;
    created_at: string;
    updated_at: string;
}

export interface ScanCreatePayload {
    name: string;
    file_type: "terraform" | "cloudformation";
    source_content: string;
    file_name: string;
}

export interface PaginatedResponse<T> {
    items: T[];
    total: number;
    page: number;
    page_size: number;
    total_pages: number;
}
