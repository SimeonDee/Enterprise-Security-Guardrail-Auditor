interface Props {
    message: string;
    onRetry?: () => void;
}

export default function ErrorMessage({ message, onRetry }: Props) {
    return (
        <div className="rounded-lg bg-red-50 border border-red-200 p-4 text-center">
            <p className="text-red-700">{message}</p>
            {onRetry && (
                <button
                    onClick={onRetry}
                    className="mt-2 text-sm text-red-600 underline hover:text-red-800"
                >
                    Try again
                </button>
            )}
        </div>
    );
}
