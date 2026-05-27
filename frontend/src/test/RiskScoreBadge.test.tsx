import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import RiskScoreBadge from "../components/RiskScoreBadge";

describe("RiskScoreBadge", () => {
    it("renders green for low scores", () => {
        render(<RiskScoreBadge score={10} />);
        const badge = screen.getByText("10.0%");
        expect(badge).toBeInTheDocument();
        expect(badge.className).toContain("green");
    });

    it("renders red for high scores", () => {
        render(<RiskScoreBadge score={85} />);
        const badge = screen.getByText("85.0%");
        expect(badge).toBeInTheDocument();
        expect(badge.className).toContain("red");
    });

    it("renders yellow for medium scores", () => {
        render(<RiskScoreBadge score={50} />);
        const badge = screen.getByText("50.0%");
        expect(badge).toBeInTheDocument();
        expect(badge.className).toContain("yellow");
    });

    it("renders orange for moderate scores", () => {
        render(<RiskScoreBadge score={25} />);
        const badge = screen.getByText("25.0%");
        expect(badge).toBeInTheDocument();
        expect(badge.className).toContain("orange");
    });
});
