interface Props {
    page: number;
    totalPages: number;
    onPageChange: (page: number) => void;
}

export default function Pagination({ page, totalPages, onPageChange }: Props) {
    if (totalPages <= 1) return null;

    return (
        <div className="flex items-center justify-center gap-2 mt-6">
            <button
                onClick={() => onPageChange(page - 1)}
                disabled={page <= 1}
                className="px-3 py-1 text-sm rounded border disabled:opacity-40 hover:bg-gray-100"
            >
                Previous
            </button>
            <span className="text-sm text-gray-600">
                Page {page} of {totalPages}
            </span>
            <button
                onClick={() => onPageChange(page + 1)}
                disabled={page >= totalPages}
                className="px-3 py-1 text-sm rounded border disabled:opacity-40 hover:bg-gray-100"
            >
                Next
            </button>
        </div>
    );
}
