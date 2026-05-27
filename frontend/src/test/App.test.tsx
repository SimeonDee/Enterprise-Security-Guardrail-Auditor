import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import App from "../App";
import { TestWrapper } from "./test-utils";

describe("App", () => {
    it("renders the layout with navigation", () => {
        render(
            <TestWrapper>
                <App />
            </TestWrapper>
        );
        expect(screen.getAllByText(/Guardrail Auditor/i).length).toBeGreaterThan(0);
        expect(screen.getByText("Dashboard")).toBeInTheDocument();
        expect(screen.getByText("Scans")).toBeInTheDocument();
        expect(screen.getByText("Guardrails")).toBeInTheDocument();
    });
});
