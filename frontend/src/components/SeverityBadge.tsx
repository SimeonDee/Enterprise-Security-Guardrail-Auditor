interface Props {
    severity: string;
}

export default function SeverityBadge({ severity }: Props) {
    const colors: Record<string, string> = {
        critical: "bg-red-600 text-white",
        high: "bg-orange-500 text-white",
        medium: "bg-yellow-400 text-gray-900",
        low: "bg-blue-100 text-blue-800",
        info: "bg-gray-100 text-gray-600",
    };

    return (
        <span
            className={`inline-flex px-2 py-0.5 rounded text-xs font-semibold uppercase ${colors[severity] || colors.info
                }`}
        >
            {severity}
        </span>
    );
}
