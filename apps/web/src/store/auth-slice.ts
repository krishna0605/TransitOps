import { createSlice, type PayloadAction } from "@reduxjs/toolkit";

import { DEFAULT_ROLE, type AppRole } from "@/config/roles";

interface AuthState {
  role: AppRole;
}

const initialState: AuthState = { role: DEFAULT_ROLE };

const authSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {
    setRole(state, action: PayloadAction<AppRole>) {
      state.role = action.payload;
    },
  },
});

export const { setRole } = authSlice.actions;
export const authReducer = authSlice.reducer;
