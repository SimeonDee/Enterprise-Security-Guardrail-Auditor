import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import StatusBadge from "../components/StatusBadge";

describe("StatusBadge", () => {
    it("renders completed status with green style", () => {
        render(<StatusBadge status="completed" />);
        const badge = screen.getByText("completed");
        expect(badge).toBeInTheDocument();
        expect(badge.className).toContain("green");
    });

    it("renders running status with blue style", () => {
        render(<StatusBadge status="running" />);
        const badge = screen.getByText("running");
        expect(badge.className).toContain("blue");
    });

    it("renders failed status with red style", () => {
        render(<StatusBadge status="failed" />);
        const badge = screen.getByText("failed");
        expect(badge.className).toContain("red");
    });

    it("renders pending status with gray style", () => {
        render(<StatusBadge status="pending" />);
        const badge = screen.getByText("pending");
        expect(badge.className).toContain("gray");
    });
});
