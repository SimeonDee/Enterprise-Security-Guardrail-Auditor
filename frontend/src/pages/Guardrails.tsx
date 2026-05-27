import { useEffect, useState } from "react";
import { getGuardrails } from "../services/api";
import type { Guardrail } from "../types/api";
import SeverityBadge from "../components/SeverityBadge";

export default function Guardrails() {
    const [guardrails, setGuardrails] = useState<Guardrail[]>([]);
    const [error, setError] = useState("");

    useEffect(() => {
        getGuardrails()
            .then(setGuardrails)
            .catch(() => setError("Failed to load guardrails"));
    }, []);

    if (error) return <p className="text-red-600">{error}</p>;

    return (
        <div>
            <h1 className="text-2xl font-bold mb-6">Security Guardrails</h1>

            {guardrails.length === 0 ? (
                <p className="text-gray-500">No guardrails configured. Seed the database to get started.</p>
            ) : (
                <div className="grid gap-4">
                    {guardrails.map((g) => (
                        <div key={g.id} className="bg-white rounded-lg shadow p-4">
                            <div className="flex items-start justify-between">
                                <div>
                                    <h3 className="font-semibold">{g.name}</h3>
                                    <p className="text-sm text-gray-600 mt-1">{g.description}</p>
                                    <div className="flex gap-3 mt-2 text-xs text-gray-400">
                                        <span>Provider: <span className="uppercase">{g.provider}</span></span>
                                        <span>Resource: <span className="font-mono">{g.resource_type}</span></span>
                                        <span>{g.enabled ? "✅ Enabled" : "❌ Disabled"}</span>
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
