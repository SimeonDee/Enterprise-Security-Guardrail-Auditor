import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getScans } from "../services/api";
import type { Scan } from "../types/api";
import RiskScoreBadge from "../components/RiskScoreBadge";

export default function Scans() {
    const [scans, setScans] = useState<Scan[]>([]);
    const [error, setError] = useState("");

    useEffect(() => {
        getScans()
            .then(setScans)
            .catch(() => setError("Failed to load scans"));
    }, []);

    if (error) return <p className="text-red-600">{error}</p>;

    return (
        <div>
            <div className="flex items-center justify-between mb-6">
                <h1 className="text-2xl font-bold">Scan History</h1>
                <Link
                    to="/scans/new"
                    className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700"
                >
                    + New Scan
                </Link>
            </div>

            {scans.length === 0 ? (
                <p className="text-gray-500">No scans found.</p>
            ) : (
                <div className="bg-white rounded-lg shadow overflow-hidden">
                    <table className="w-full text-sm">
                        <thead className="bg-gray-50">
                            <tr className="text-left text-gray-500">
                                <th className="px-4 py-3">Name</th>
                                <th className="px-4 py-3">File</th>
                                <th className="px-4 py-3">Type</th>
                                <th className="px-4 py-3">Violations</th>
                                <th className="px-4 py-3">Risk</th>
                                <th className="px-4 py-3">Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            {scans.map((scan) => (
                                <tr key={scan.id} className="border-t hover:bg-gray-50">
                                    <td className="px-4 py-3">
                                        <Link to={`/scans/${scan.id}`} className="text-blue-600 hover:underline">
                                            {scan.name}
                                        </Link>
                                    </td>
                                    <td className="px-4 py-3 font-mono text-xs">{scan.file_name}</td>
                                    <td className="px-4 py-3 capitalize">{scan.file_type}</td>
                                    <td className="px-4 py-3">{scan.total_violations}</td>
                                    <td className="px-4 py-3"><RiskScoreBadge score={scan.risk_score} /></td>
                                    <td className="px-4 py-3 capitalize">{scan.status}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
}
