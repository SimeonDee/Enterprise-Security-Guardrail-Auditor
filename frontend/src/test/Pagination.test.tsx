import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import Pagination from "../components/Pagination";

describe("Pagination", () => {
    it("renders nothing when totalPages is 1", () => {
        const { container } = render(
            <Pagination page={1} totalPages={1} onPageChange={vi.fn()} />
        );
        expect(container.innerHTML).toBe("");
    });

    it("renders page info", () => {
        render(<Pagination page={2} totalPages={5} onPageChange={vi.fn()} />);
        expect(screen.getByText("Page 2 of 5")).toBeInTheDocument();
    });

    it("disables Previous on first page", () => {
        render(<Pagination page={1} totalPages={3} onPageChange={vi.fn()} />);
        expect(screen.getByText("Previous")).toBeDisabled();
        expect(screen.getByText("Next")).not.toBeDisabled();
    });

    it("disables Next on last page", () => {
        render(<Pagination page={3} totalPages={3} onPageChange={vi.fn()} />);
        expect(screen.getByText("Next")).toBeDisabled();
        expect(screen.getByText("Previous")).not.toBeDisabled();
    });

    it("calls onPageChange on click", () => {
        const onChange = vi.fn();
        render(<Pagination page={2} totalPages={5} onPageChange={onChange} />);
        fireEvent.click(screen.getByText("Next"));
        expect(onChange).toHaveBeenCalledWith(3);
        fireEvent.click(screen.getByText("Previous"));
        expect(onChange).toHaveBeenCalledWith(1);
    });
});
