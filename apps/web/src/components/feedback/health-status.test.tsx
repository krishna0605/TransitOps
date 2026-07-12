import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { HealthStatus } from "./health-status";

function renderStatus() {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={client}>
      <HealthStatus />
    </QueryClientProvider>,
  );
}

describe("HealthStatus", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  it("shows a healthy API", async () => {
    vi.mocked(fetch).mockResolvedValueOnce(
      new Response(
        JSON.stringify({
          name: "TransitOps",
          version: "0.1.0",
          environment: "test",
          status: "ok",
        }),
        { status: 200, headers: { "Content-Type": "application/json" } },
      ),
    );
    renderStatus();
    expect(await screen.findByText("API 0.1.0 · test")).toBeInTheDocument();
  });

  it("shows an unavailable API", async () => {
    vi.mocked(fetch).mockRejectedValueOnce(new Error("offline"));
    renderStatus();
    expect(await screen.findByText("unavailable")).toBeInTheDocument();
  });
});
