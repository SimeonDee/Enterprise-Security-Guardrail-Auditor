const STATUS_STYLES: Record<string, string> = {
    completed: "bg-green-100 text-green-800",
    running: "bg-blue-100 text-blue-800",
    pending: "bg-gray-100 text-gray-800",
    failed: "bg-red-100 text-red-800",
};

export default function StatusBadge({ status }: { status: string }) {
    return (
        <span
            className={`inline-flex px-2 py-0.5 rounded text-xs font-semibold capitalize ${STATUS_STYLES[status] || STATUS_STYLES.pending}`}
        >
            {status}
        </span>
    );
}
