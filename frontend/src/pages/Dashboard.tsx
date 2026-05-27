import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getDashboardSummary } from "../services/api";
import type { DashboardSummary } from "../types/api";
import RiskScoreBadge from "../components/RiskScoreBadge";
import {
    BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell,
} from "recharts";

const SEVERITY_COLORS: Record<string, string> = {
    critical: "#dc2626",
    high: "#f97316",
    medium: "#eab308",
    low: "#3b82f6",
};

export default function Dashboard() {
    const [summary, setSummary] = useState<DashboardSummary | null>(null);
    const [error, setError] = useState("");

    useEffect(() => {
        getDashboardSummary()
            .then(setSummary)
            .catch(() => setError("Failed to load dashboard data"));
    }, []);

    if (error) return <p className="text-red-600">{error}</p>;
    if (!summary) return <p className="text-gray-500">Loading...</p>;

    const chartData = [
        { name: "Critical", count: summary.critical_count, color: SEVERITY_COLORS.critical },
        { name: "High", count: summary.high_count, color: SEVERITY_COLORS.high },
        { name: "Medium", count: summary.medium_count, color: SEVERITY_COLORS.medium },
        { name: "Low", count: summary.low_count, color: SEVERITY_COLORS.low },
    ];

    return (
        <div>
            <h1 className="text-2xl font-bold mb-6">Security Dashboard</h1>

            {/* Stats cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
                <StatCard label="Total Scans" value={summary.total_scans} />
                <StatCard label="Total Violations" value={summary.total_violations} />
                <StatCard
                    label="Avg Risk Score"
                    value={`${summary.average_risk_score}%`}
                />
                <StatCard label="Critical Issues" value={summary.critical_count} />
            </div>

            {/* Chart */}
            <div className="bg-white rounded-lg shadow p-6 mb-8">
                <h2 className="text-lg font-semibold mb-4">Violations by Severity</h2>
                <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={chartData}>
                        <XAxis dataKey="name" />
                        <YAxis allowDecimals={false} />
                        <Tooltip />
                        <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                            {chartData.map((entry, index) => (
                                <Cell key={index} fill={entry.color} />
                            ))}
                        </Bar>
                    </BarChart>
                </ResponsiveContainer>
            </div>

            {/* Recent scans */}
            <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-lg font-semibold mb-4">Recent Scans</h2>
                {summary.recent_scans.length === 0 ? (
                    <p className="text-gray-500">No scans yet. <Link to="/scans/new" className="text-blue-600 underline">Run your first scan</Link></p>
                ) : (
                    <table className="w-full text-sm">
                        <thead>
                            <tr className="text-left text-gray-500 border-b">
                                <th className="pb-2">Name</th>
                                <th className="pb-2">Status</th>
                                <th className="pb-2">Violations</th>
                                <th className="pb-2">Risk Score</th>
                            </tr>
                        </thead>
                        <tbody>
                            {summary.recent_scans.map((scan) => (
                                <tr key={scan.id} className="border-b last:border-0">
                                    <td className="py-2">
                                        <Link to={`/scans/${scan.id}`} className="text-blue-600 hover:underline">
                                            {scan.name}
                                        </Link>
                                    </td>
                                    <td className="py-2 capitalize">{scan.status}</td>
                                    <td className="py-2">{scan.total_violations}</td>
                                    <td className="py-2"><RiskScoreBadge score={scan.risk_score} /></td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>
        </div>
    );
}

function StatCard({ label, value }: { label: string; value: string | number }) {
    return (
        <div className="bg-white rounded-lg shadow p-4">
            <p className="text-sm text-gray-500">{label}</p>
            <p className="text-2xl font-bold mt-1">{value}</p>
        </div>
    );
}
