import { useParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { getScan } from "../services/api";
import type { Violation } from "../types/api";
import RiskScoreBadge from "../components/RiskScoreBadge";
import SeverityBadge from "../components/SeverityBadge";
import StatusBadge from "../components/StatusBadge";
import LoadingSpinner from "../components/LoadingSpinner";
import ErrorMessage from "../components/ErrorMessage";

const SEVERITY_ORDER = ["critical", "high", "medium", "low", "info"];

function groupBySeverity(violations: Violation[]) {
    const groups: Record<string, Violation[]> = {};
    for (const v of violations) {
        const key = v.severity.toLowerCase();
        if (!groups[key]) groups[key] = [];
        groups[key].push(v);
    }
    return SEVERITY_ORDER.filter((s) => groups[s]).map((s) => ({
        severity: s,
        violations: groups[s],
    }));
}

export default function ScanDetail() {
    const { id } = useParams<{ id: string }>();

    const { data: scan, isLoading, error, refetch } = useQuery({
        queryKey: ["scan", id],
        queryFn: () => getScan(Number(id)),
        enabled: !!id,
    });

    if (isLoading) return <LoadingSpinner message="Loading scan details..." />;
    if (error) return <ErrorMessage message="Failed to load scan details" onRetry={() => refetch()} />;
    if (!scan) return null;

    const grouped = groupBySeverity(scan.violations);

    return (
        <div>
            <Link to="/scans" className="text-blue-600 hover:underline text-sm">
                &larr; Back to Scans
            </Link>

            <div className="mt-4 mb-6">
                <div className="flex items-center gap-3">
                    <h1 className="text-2xl font-bold">{scan.name}</h1>
                    <StatusBadge status={scan.status} />
                </div>
                <div className="flex flex-wrap gap-4 mt-2 text-sm text-gray-500">
                    <span>
                        File: <span className="font-mono">{scan.file_name}</span>
                    </span>
                    <span>
                        Type: <span className="capitalize">{scan.file_type}</span>
                    </span>
                    {scan.completed_at && (
                        <span>Completed: {new Date(scan.completed_at).toLocaleString()}</span>
                    )}
                </div>
            </div>

            {/* Summary cards */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
                <div className="bg-white rounded-lg shadow p-4 text-center">
                    <p className="text-sm text-gray-500">Risk Score</p>
                    <div className="mt-2">
                        <RiskScoreBadge score={scan.risk_score} />
                    </div>
                </div>
                <div className="bg-white rounded-lg shadow p-4 text-center">
                    <p className="text-sm text-gray-500">Violations</p>
                    <p className="text-3xl font-bold mt-1">{scan.total_violations}</p>
                </div>
                <div className="bg-white rounded-lg shadow p-4 text-center">
                    <p className="text-sm text-gray-500">Severity Breakdown</p>
                    <div className="flex justify-center gap-2 mt-2">
                        {grouped.map((g) => (
                            <span key={g.severity} className="text-xs">
                                <SeverityBadge severity={g.severity} /> {g.violations.length}
                            </span>
                        ))}
                    </div>
                </div>
            </div>

            {/* Findings grouped by severity */}
            <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-lg font-semibold mb-4">
                    Findings ({scan.violations.length})
                </h2>
                {scan.violations.length === 0 ? (
                    <div className="text-center py-8">
                        <p className="text-green-600 text-lg font-medium">
                            ✅ No violations found
                        </p>
                        <p className="text-gray-500 text-sm mt-1">This scan is clean!</p>
                    </div>
                ) : (
                    <div className="space-y-6">
                        {grouped.map((group) => (
                            <div key={group.severity}>
                                <div className="flex items-center gap-2 mb-3">
                                    <SeverityBadge severity={group.severity} />
                                    <span className="text-sm text-gray-500">
                                        {group.violations.length} finding
                                        {group.violations.length !== 1 ? "s" : ""}
                                    </span>
                                </div>
                                <div className="space-y-3">
                                    {group.violations.map((v) => (
                                        <div key={v.id} className="border rounded-lg p-4">
                                            <p className="font-medium">{v.message}</p>
                                            <p className="text-sm text-gray-500 mt-1">
                                                Resource:{" "}
                                                <span className="font-mono">{v.resource_name}</span>
                                                {v.line_number && (
                                                    <> &middot; Line {v.line_number}</>
                                                )}
                                                {v.file_path && (
                                                    <> &middot; {v.file_path}</>
                                                )}
                                            </p>
                                            <div className="mt-3 bg-blue-50 rounded p-3 text-sm">
                                                <p className="font-medium text-blue-800">
                                                    Remediation:
                                                </p>
                                                <p className="text-blue-700">{v.remediation}</p>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}
