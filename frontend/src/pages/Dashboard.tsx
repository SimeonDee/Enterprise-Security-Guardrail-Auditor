import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { getDashboardSummary } from "../services/api";
import RiskScoreBadge from "../components/RiskScoreBadge";
import StatusBadge from "../components/StatusBadge";
import LoadingSpinner from "../components/LoadingSpinner";
import ErrorMessage from "../components/ErrorMessage";
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    Tooltip,
    ResponsiveContainer,
    Cell,
} from "recharts";

const SEVERITY_COLORS: Record<string, string> = {
    critical: "#dc2626",
    high: "#f97316",
    medium: "#eab308",
    low: "#3b82f6",
};

export default function Dashboard() {
    const { data: summary, isLoading, error, refetch } = useQuery({
        queryKey: ["dashboard"],
        queryFn: getDashboardSummary,
    });

    if (isLoading) return <LoadingSpinner message="Loading dashboard..." />;
    if (error) return <ErrorMessage message="Failed to load dashboard data" onRetry={() => refetch()} />;
    if (!summary) return null;

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
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
                <StatCard label="Total Scans" value={summary.total_scans} />
                <StatCard label="Total Violations" value={summary.total_violations} />
                <StatCard label="Avg Risk Score" value={`${summary.average_risk_score.toFixed(1)}%`} />
                <StatCard label="Critical Issues" value={summary.critical_count} accent />
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
                    <p className="text-gray-500">
                        No scans yet.{" "}
                        <Link to="/scans/new" className="text-blue-600 underline">
                            Run your first scan
                        </Link>
                    </p>
                ) : (
                    <div className="overflow-x-auto">
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
                                        <td className="py-2">
                                            <StatusBadge status={scan.status} />
                                        </td>
                                        <td className="py-2">{scan.total_violations}</td>
                                        <td className="py-2">
                                            <RiskScoreBadge score={scan.risk_score} />
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </div>
    );
}

function StatCard({ label, value, accent }: { label: string; value: string | number; accent?: boolean }) {
    return (
        <div className="bg-white rounded-lg shadow p-4">
            <p className="text-sm text-gray-500">{label}</p>
            <p className={`text-2xl font-bold mt-1 ${accent ? "text-red-600" : ""}`}>{value}</p>
        </div>
    );
}
