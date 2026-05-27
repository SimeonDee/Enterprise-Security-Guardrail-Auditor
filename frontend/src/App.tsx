import { Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import Dashboard from "./pages/Dashboard";
import Scans from "./pages/Scans";
import ScanDetail from "./pages/ScanDetail";
import NewScan from "./pages/NewScan";
import Guardrails from "./pages/Guardrails";

function App() {
    return (
        <Routes>
            <Route element={<Layout />}>
                <Route path="/" element={<Dashboard />} />
                <Route path="/scans" element={<Scans />} />
                <Route path="/scans/new" element={<NewScan />} />
                <Route path="/scans/:id" element={<ScanDetail />} />
                <Route path="/guardrails" element={<Guardrails />} />
            </Route>
        </Routes>
    );
}

export default App;
