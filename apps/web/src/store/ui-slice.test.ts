import { describe, expect, it } from "vitest";

import { createAppStore } from "@/store/store";
import { clearDraft, saveDraft, setSidebarOpen } from "@/store/ui-slice";

describe("UI state", () => {
  it("persists sidebar state and recoverable drafts", () => {
    const store = createAppStore();
    store.dispatch(setSidebarOpen(false));
    store.dispatch(saveDraft({ key: "trip", value: { source: "Depot" } }));

    expect(store.getState().ui).toEqual({
      sidebarOpen: false,
      drafts: { trip: { source: "Depot" } },
    });

    store.dispatch(clearDraft("trip"));
    expect(store.getState().ui.drafts).toEqual({});
  });
});
