import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { createScan } from "../services/api";
import type { ScanCreatePayload } from "../types/api";

export default function NewScan() {
    const navigate = useNavigate();
    const [form, setForm] = useState<ScanCreatePayload>({
        name: "",
        file_type: "terraform",
        source_content: "",
        file_name: "",
    });
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError("");
        setLoading(true);
        try {
            const result = await createScan(form);
            navigate(`/scans/${result.id}`);
        } catch {
            setError("Failed to create scan. Please check your input.");
        } finally {
            setLoading(false);
        }
    };

    const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = (ev) => {
            const content = ev.target?.result as string;
            setForm((prev) => ({
                ...prev,
                source_content: content,
                file_name: file.name,
                name: prev.name || file.name.replace(/\.[^.]+$/, ""),
            }));
        };
        reader.readAsText(file);
    };

    return (
        <div className="max-w-2xl mx-auto">
            <h1 className="text-2xl font-bold mb-6">New Security Scan</h1>

            {error && <p className="text-red-600 mb-4 bg-red-50 p-3 rounded">{error}</p>}

            <form onSubmit={handleSubmit} className="space-y-4 bg-white p-6 rounded-lg shadow">
                <div>
                    <label className="block text-sm font-medium mb-1">Scan Name</label>
                    <input
                        type="text"
                        value={form.name}
                        onChange={(e) => setForm({ ...form, name: e.target.value })}
                        required
                        className="w-full border rounded-lg px-3 py-2 text-sm"
                        placeholder="e.g. Production infra audit"
                    />
                </div>

                <div>
                    <label className="block text-sm font-medium mb-1">File Type</label>
                    <select
                        value={form.file_type}
                        onChange={(e) =>
                            setForm({ ...form, file_type: e.target.value as "terraform" | "cloudformation" })
                        }
                        className="w-full border rounded-lg px-3 py-2 text-sm"
                    >
                        <option value="terraform">Terraform (.tf)</option>
                        <option value="cloudformation">CloudFormation (.yaml/.json)</option>
                    </select>
                </div>

                <div>
                    <label className="block text-sm font-medium mb-1">Upload File</label>
                    <input
                        type="file"
                        accept=".tf,.yaml,.yml,.json"
                        onChange={handleFileUpload}
                        className="w-full text-sm"
                    />
                </div>

                <div>
                    <label className="block text-sm font-medium mb-1">
                        Or paste configuration content
                    </label>
                    <textarea
                        value={form.source_content}
                        onChange={(e) => setForm({ ...form, source_content: e.target.value })}
                        rows={12}
                        className="w-full border rounded-lg px-3 py-2 font-mono text-sm"
                        placeholder="Paste your Terraform or CloudFormation config here..."
                    />
                </div>

                {form.file_name && (
                    <p className="text-sm text-gray-500">
                        File: <span className="font-mono">{form.file_name}</span>
                    </p>
                )}

                <button
                    type="submit"
                    disabled={loading || !form.source_content || !form.name}
                    className="w-full bg-blue-600 text-white py-2 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    {loading ? "Scanning..." : "Run Scan"}
                </button>
            </form>
        </div>
    );
}
