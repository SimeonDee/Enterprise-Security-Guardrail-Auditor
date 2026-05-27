import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { getScan } from "../services/api";
import type { ScanDetail as ScanDetailType } from "../types/api";
import RiskScoreBadge from "../components/RiskScoreBadge";
import SeverityBadge from "../components/SeverityBadge";

export default function ScanDetail() {
    const { id } = useParams<{ id: string }>();
    const [scan, setScan] = useState<ScanDetailType | null>(null);
    const [error, setError] = useState("");

    useEffect(() => {
        if (id) {
            getScan(Number(id))
                .then(setScan)
                .catch(() => setError("Failed to load scan details"));
        }
    }, [id]);

    if (error) return <p className="text-red-600">{error}</p>;
    if (!scan) return <p className="text-gray-500">Loading...</p>;

    return (
        <div>
            <Link to="/scans" className="text-blue-600 hover:underline text-sm">&larr; Back to Scans</Link>

            <div className="mt-4 mb-6">
                <h1 className="text-2xl font-bold">{scan.name}</h1>
                <div className="flex gap-4 mt-2 text-sm text-gray-500">
                    <span>File: <span className="font-mono">{scan.file_name}</span></span>
                    <span>Type: <span className="capitalize">{scan.file_type}</span></span>
                    <span>Status: <span className="capitalize">{scan.status}</span></span>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
                <div className="bg-white rounded-lg shadow p-4 text-center">
                    <p className="text-sm text-gray-500">Risk Score</p>
                    <p className="text-3xl font-bold mt-1"><RiskScoreBadge score={scan.risk_score} /></p>
                </div>
                <div className="bg-white rounded-lg shadow p-4 text-center">
                    <p className="text-sm text-gray-500">Violations</p>
                    <p className="text-3xl font-bold mt-1">{scan.total_violations}</p>
                </div>
                <div className="bg-white rounded-lg shadow p-4 text-center">
                    <p className="text-sm text-gray-500">Completed</p>
                    <p className="text-sm font-medium mt-2">{scan.completed_at || "—"}</p>
                </div>
            </div>

            {/* Violations list */}
            <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-lg font-semibold mb-4">Violations ({scan.violations.length})</h2>
                {scan.violations.length === 0 ? (
                    <p className="text-green-600 font-medium">No violations found. Clean scan!</p>
                ) : (
                    <div className="space-y-4">
                        {scan.violations.map((v) => (
                            <div key={v.id} className="border rounded-lg p-4">
                                <div className="flex items-start justify-between">
                                    <div>
                                        <p className="font-medium">{v.message}</p>
                                        <p className="text-sm text-gray-500 mt-1">
                                            Resource: <span className="font-mono">{v.resource_name}</span>
                                            {v.line_number && <> &middot; Line {v.line_number}</>}
                                        </p>
                                    </div>
                                    <SeverityBadge severity={v.severity} />
                                </div>
                                <div className="mt-3 bg-blue-50 rounded p-3 text-sm">
                                    <p className="font-medium text-blue-800">Remediation:</p>
                                    <p className="text-blue-700">{v.remediation}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}
