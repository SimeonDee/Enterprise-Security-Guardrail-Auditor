import { useState } from "react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { getScans } from "../services/api";
import RiskScoreBadge from "../components/RiskScoreBadge";
import StatusBadge from "../components/StatusBadge";
import Pagination from "../components/Pagination";
import LoadingSpinner from "../components/LoadingSpinner";
import ErrorMessage from "../components/ErrorMessage";

const PAGE_SIZE = 10;

export default function Scans() {
    const [page, setPage] = useState(1);

    const { data, isLoading, error, refetch } = useQuery({
        queryKey: ["scans", page],
        queryFn: () => getScans(page, PAGE_SIZE),
    });

    if (isLoading) return <LoadingSpinner message="Loading scans..." />;
    if (error) return <ErrorMessage message="Failed to load scans" onRetry={() => refetch()} />;
    if (!data) return null;

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

            {data.items.length === 0 ? (
                <div className="bg-white rounded-lg shadow p-8 text-center">
                    <p className="text-gray-500">No scans found.</p>
                    <Link to="/scans/new" className="text-blue-600 underline text-sm mt-2 inline-block">
                        Run your first scan
                    </Link>
                </div>
            ) : (
                <>
                    <div className="bg-white rounded-lg shadow overflow-hidden">
                        <div className="overflow-x-auto">
                            <table className="w-full text-sm">
                                <thead className="bg-gray-50">
                                    <tr className="text-left text-gray-500">
                                        <th className="px-4 py-3">Name</th>
                                        <th className="px-4 py-3">File</th>
                                        <th className="px-4 py-3 hidden sm:table-cell">Type</th>
                                        <th className="px-4 py-3">Violations</th>
                                        <th className="px-4 py-3">Risk</th>
                                        <th className="px-4 py-3">Status</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {data.items.map((scan) => (
                                        <tr key={scan.id} className="border-t hover:bg-gray-50">
                                            <td className="px-4 py-3">
                                                <Link to={`/scans/${scan.id}`} className="text-blue-600 hover:underline">
                                                    {scan.name}
                                                </Link>
                                            </td>
                                            <td className="px-4 py-3 font-mono text-xs">{scan.file_name}</td>
                                            <td className="px-4 py-3 capitalize hidden sm:table-cell">{scan.file_type}</td>
                                            <td className="px-4 py-3">{scan.total_violations}</td>
                                            <td className="px-4 py-3">
                                                <RiskScoreBadge score={scan.risk_score} />
                                            </td>
                                            <td className="px-4 py-3">
                                                <StatusBadge status={scan.status} />
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>

                    <div className="flex items-center justify-between mt-4">
                        <p className="text-sm text-gray-500">{data.total} total scans</p>
                        <Pagination
                            page={data.page}
                            totalPages={data.total_pages}
                            onPageChange={setPage}
                        />
                    </div>
                </>
            )}
        </div>
    );
}
