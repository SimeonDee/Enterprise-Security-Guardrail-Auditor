import { Link, Outlet, useLocation } from "react-router-dom";

const navItems = [
    { to: "/", label: "Dashboard" },
    { to: "/scans", label: "Scans" },
    { to: "/scans/new", label: "New Scan" },
    { to: "/guardrails", label: "Guardrails" },
];

export default function Layout() {
    const location = useLocation();

    return (
        <div className="min-h-screen flex flex-col">
            <header className="bg-gray-900 text-white shadow-lg">
                <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
                    <Link to="/" className="text-xl font-bold tracking-tight">
                        🛡️ Guardrail Auditor
                    </Link>
                    <nav className="flex gap-6">
                        {navItems.map((item) => (
                            <Link
                                key={item.to}
                                to={item.to}
                                className={`text-sm font-medium transition-colors ${location.pathname === item.to
                                        ? "text-blue-400"
                                        : "text-gray-300 hover:text-white"
                                    }`}
                            >
                                {item.label}
                            </Link>
                        ))}
                    </nav>
                </div>
            </header>
            <main className="flex-1 max-w-7xl mx-auto px-4 py-8 w-full">
                <Outlet />
            </main>
            <footer className="bg-gray-100 text-center text-sm text-gray-500 py-4">
                Enterprise Security Guardrail Auditor &mdash; MVP v0.1.0
            </footer>
        </div>
    );
}
