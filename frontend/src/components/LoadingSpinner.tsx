export default function LoadingSpinner({ message = "Loading..." }: { message?: string }) {
    return (
        <div className="flex flex-col items-center justify-center py-12 text-gray-500">
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-gray-300 border-t-blue-600" />
            <p className="mt-3 text-sm">{message}</p>
        </div>
    );
}
