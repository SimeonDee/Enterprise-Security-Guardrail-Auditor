import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import ErrorMessage from "../components/ErrorMessage";

describe("ErrorMessage", () => {
    it("renders error message", () => {
        render(<ErrorMessage message="Something went wrong" />);
        expect(screen.getByText("Something went wrong")).toBeInTheDocument();
    });

    it("renders retry button when onRetry is provided", () => {
        const onRetry = vi.fn();
        render(<ErrorMessage message="Error" onRetry={onRetry} />);
        const btn = screen.getByText("Try again");
        fireEvent.click(btn);
        expect(onRetry).toHaveBeenCalledOnce();
    });

    it("does not render retry button without onRetry", () => {
        render(<ErrorMessage message="Error" />);
        expect(screen.queryByText("Try again")).not.toBeInTheDocument();
    });
});
