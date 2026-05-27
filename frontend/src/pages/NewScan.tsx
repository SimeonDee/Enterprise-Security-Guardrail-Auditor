import { useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { createScan, uploadScan } from "../services/api";
import type { ScanCreatePayload } from "../types/api";

type Mode = "paste" | "upload";

export default function NewScan() {
    const navigate = useNavigate();
    const queryClient = useQueryClient();
    const fileRef = useRef<HTMLInputElement>(null);
    const [mode, setMode] = useState<Mode>("upload");
    const [name, setName] = useState("");
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [form, setForm] = useState<ScanCreatePayload>({
        name: "",
        file_type: "terraform",
        source_content: "",
        file_name: "",
    });

    const pasteMutation = useMutation({
        mutationFn: createScan,
        onSuccess: (result) => {
            queryClient.invalidateQueries({ queryKey: ["scans"] });
            queryClient.invalidateQueries({ queryKey: ["dashboard"] });
            navigate(`/scans/${result.id}`);
        },
    });

    const uploadMutation = useMutation({
        mutationFn: ({ file, scanName }: { file: File; scanName: string }) =>
            uploadScan(file, scanName),
        onSuccess: (result) => {
            queryClient.invalidateQueries({ queryKey: ["scans"] });
            queryClient.invalidateQueries({ queryKey: ["dashboard"] });
            navigate(`/scans/${result.id}`);
        },
    });

    const isLoading = pasteMutation.isPending || uploadMutation.isPending;
    const error = pasteMutation.error || uploadMutation.error;

    const handlePasteSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        pasteMutation.mutate({ ...form });
    };

    const handleUploadSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!selectedFile) return;
        uploadMutation.mutate({ file: selectedFile, scanName: name || selectedFile.name.replace(/\.[^.]+$/, "") });
    };

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0] ?? null;
        setSelectedFile(file);
        if (file && !name) setName(file.name.replace(/\.[^.]+$/, ""));
    };

    return (
        <div className="max-w-2xl mx-auto">
            <h1 className="text-2xl font-bold mb-6">New Security Scan</h1>

            {/* Mode toggle */}
            <div className="flex gap-2 mb-6">
                <button
                    onClick={() => setMode("upload")}
                    className={`px-4 py-2 rounded-lg text-sm font-medium ${mode === "upload" ? "bg-blue-600 text-white" : "bg-gray-100 text-gray-700 hover:bg-gray-200"}`}
                >
                    Upload File
                </button>
                <button
                    onClick={() => setMode("paste")}
                    className={`px-4 py-2 rounded-lg text-sm font-medium ${mode === "paste" ? "bg-blue-600 text-white" : "bg-gray-100 text-gray-700 hover:bg-gray-200"}`}
                >
                    Paste Content
                </button>
            </div>

            {error && (
                <div className="mb-4 bg-red-50 border border-red-200 rounded-lg p-3 text-red-700 text-sm">
                    Scan failed. Please check your input and try again.
                </div>
            )}

            {mode === "upload" ? (
                <form onSubmit={handleUploadSubmit} className="space-y-4 bg-white p-6 rounded-lg shadow">
                    <div>
                        <label className="block text-sm font-medium mb-1">Scan Name</label>
                        <input
                            type="text"
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                            className="w-full border rounded-lg px-3 py-2 text-sm"
                            placeholder="e.g. Production infra audit"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium mb-1">Terraform File (.tf)</label>
                        <div
                            onClick={() => fileRef.current?.click()}
                            className="border-2 border-dashed rounded-lg p-8 text-center cursor-pointer hover:border-blue-400 hover:bg-blue-50 transition-colors"
                        >
                            {selectedFile ? (
                                <p className="text-sm font-medium text-gray-700">
                                    <span className="font-mono">{selectedFile.name}</span>{" "}
                                    <span className="text-gray-400">({(selectedFile.size / 1024).toFixed(1)} KB)</span>
                                </p>
                            ) : (
                                <p className="text-sm text-gray-500">Click to select a .tf file</p>
                            )}
                        </div>
                        <input
                            ref={fileRef}
                            type="file"
                            accept=".tf"
                            onChange={handleFileSelect}
                            className="hidden"
                        />
                    </div>

                    <button
                        type="submit"
                        disabled={isLoading || !selectedFile}
                        className="w-full bg-blue-600 text-white py-2 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {isLoading ? "Scanning..." : "Upload & Scan"}
                    </button>
                </form>
            ) : (
                <form onSubmit={handlePasteSubmit} className="space-y-4 bg-white p-6 rounded-lg shadow">
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
                        <label className="block text-sm font-medium mb-1">File Name</label>
                        <input
                            type="text"
                            value={form.file_name}
                            onChange={(e) => setForm({ ...form, file_name: e.target.value })}
                            required
                            className="w-full border rounded-lg px-3 py-2 text-sm font-mono"
                            placeholder="main.tf"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium mb-1">File Type</label>
                        <select
                            value={form.file_type}
                            onChange={(e) => setForm({ ...form, file_type: e.target.value as "terraform" | "cloudformation" })}
                            className="w-full border rounded-lg px-3 py-2 text-sm"
                        >
                            <option value="terraform">Terraform (.tf)</option>
                            <option value="cloudformation">CloudFormation (.yaml/.json)</option>
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm font-medium mb-1">Configuration Content</label>
                        <textarea
                            value={form.source_content}
                            onChange={(e) => setForm({ ...form, source_content: e.target.value })}
                            rows={12}
                            required
                            className="w-full border rounded-lg px-3 py-2 font-mono text-sm"
                            placeholder="Paste your Terraform or CloudFormation config here..."
                        />
                    </div>

                    <button
                        type="submit"
                        disabled={isLoading || !form.source_content || !form.name}
                        className="w-full bg-blue-600 text-white py-2 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {isLoading ? "Scanning..." : "Run Scan"}
                    </button>
                </form>
            )}
        </div>
    );
}
