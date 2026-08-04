import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import ArticleCard from "../../components/ArticleCard";

// next/link — test muhitida oddiy <a> sifatida ishlaydi
vi.mock("next/link", () => ({
  default: ({ href, children, ...rest }) => (
    <a href={typeof href === "string" ? href : "/"} {...rest}>
      {children}
    </a>
  ),
}));

const article = {
  id: 1,
  title: "Test dars",
  slug: "test-dars",
  summary: "Qisqa xulosa",
  content: "Bu dars matni",
  category: { name: "Moliya", slug: "moliya" },
  published_at: "2026-08-04T00:00:00Z",
  image_url: null,
};

describe("ArticleCard", () => {
  it("sarlavha va kategoriyani ko'rsatadi", () => {
    render(<ArticleCard article={article} />);
    expect(screen.getByText("Test dars")).toBeInTheDocument();
    expect(screen.getAllByText("Moliya").length).toBeGreaterThan(0);
  });

  it("dars sahifasiga to'g'ri havola beradi", () => {
    render(<ArticleCard article={article} />);
    const links = screen.getAllByRole("link");
    expect(links.length).toBeGreaterThan(0);
    expect(links[0]).toHaveAttribute("href", "/moliya/test-dars");
  });

  it("compact rejimda ham ishlaydi", () => {
    render(<ArticleCard article={article} compact />);
    expect(screen.getByText("Test dars")).toBeInTheDocument();
  });
});
