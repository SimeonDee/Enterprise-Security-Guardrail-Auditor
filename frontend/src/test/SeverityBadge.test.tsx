import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import SeverityBadge from "../components/SeverityBadge";

describe("SeverityBadge", () => {
    it("renders critical severity", () => {
        render(<SeverityBadge severity="critical" />);
        const badge = screen.getByText("critical");
        expect(badge).toBeInTheDocument();
        expect(badge.className).toContain("red");
    });

    it("renders high severity", () => {
        render(<SeverityBadge severity="high" />);
        const badge = screen.getByText("high");
        expect(badge).toBeInTheDocument();
        expect(badge.className).toContain("orange");
    });

    it("renders medium severity", () => {
        render(<SeverityBadge severity="medium" />);
        expect(screen.getByText("medium")).toBeInTheDocument();
    });

    it("renders low severity", () => {
        render(<SeverityBadge severity="low" />);
        expect(screen.getByText("low")).toBeInTheDocument();
    });

    it("renders unknown severity with fallback", () => {
        render(<SeverityBadge severity="unknown" />);
        expect(screen.getByText("unknown")).toBeInTheDocument();
    });
});
