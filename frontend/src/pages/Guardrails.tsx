import { useQuery } from "@tanstack/react-query";
import { getGuardrails } from "../services/api";
import SeverityBadge from "../components/SeverityBadge";
import LoadingSpinner from "../components/LoadingSpinner";
import ErrorMessage from "../components/ErrorMessage";

export default function Guardrails() {
    const { data: guardrails, isLoading, error, refetch } = useQuery({
        queryKey: ["guardrails"],
        queryFn: getGuardrails,
    });

    if (isLoading) return <LoadingSpinner message="Loading guardrails..." />;
    if (error) return <ErrorMessage message="Failed to load guardrails" onRetry={() => refetch()} />;

    return (
        <div>
            <h1 className="text-2xl font-bold mb-6">Security Guardrails</h1>

            {!guardrails || guardrails.length === 0 ? (
                <div className="bg-white rounded-lg shadow p-8 text-center">
                    <p className="text-gray-500">
                        No guardrails configured. Seed the database to get started.
                    </p>
                </div>
            ) : (
                <div className="grid gap-4">
                    {guardrails.map((g) => (
                        <div key={g.id} className="bg-white rounded-lg shadow p-4">
                            <div className="flex items-start justify-between">
                                <div>
                                    <h3 className="font-semibold">{g.name}</h3>
                                    <p className="text-sm text-gray-600 mt-1">
                                        {g.description}
                                    </p>
                                    <div className="flex flex-wrap gap-3 mt-2 text-xs text-gray-400">
                                        <span>
                                            Provider:{" "}
                                            <span className="uppercase">{g.provider}</span>
                                        </span>
                                        <span>
                                            Resource:{" "}
                                            <span className="font-mono">{g.resource_type}</span>
                                        </span>
                                        <span>
                                            {g.enabled ? "✅ Enabled" : "❌ Disabled"}
                                        </span>
                                    </div>
                                </div>
                                <SeverityBadge severity={g.severity} />
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
