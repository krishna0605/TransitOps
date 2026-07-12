import { createSlice, type PayloadAction } from "@reduxjs/toolkit";

export type DraftsState = Record<string, Record<string, unknown>>;

interface UiState {
  sidebarOpen: boolean;
  drafts: DraftsState;
}

const initialState: UiState = {
  sidebarOpen: true,
  drafts: {},
};

const uiSlice = createSlice({
  name: "ui",
  initialState,
  reducers: {
    setSidebarOpen(state, action: PayloadAction<boolean>) {
      state.sidebarOpen = action.payload;
    },
    saveDraft(
      state,
      action: PayloadAction<{ key: string; value: Record<string, unknown> }>,
    ) {
      state.drafts[action.payload.key] = action.payload.value;
    },
    clearDraft(state, action: PayloadAction<string>) {
      delete state.drafts[action.payload];
    },
  },
});

export const { clearDraft, saveDraft, setSidebarOpen } = uiSlice.actions;
export const uiReducer = uiSlice.reducer;
