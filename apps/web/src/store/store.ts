import { configureStore } from "@reduxjs/toolkit";

import { authReducer } from "@/store/auth-slice";
import { uiReducer } from "@/store/ui-slice";

export const createAppStore = () =>
  configureStore({
    reducer: {
      auth: authReducer,
      ui: uiReducer,
    },
  });

export type AppStore = ReturnType<typeof createAppStore>;
export type RootState = ReturnType<AppStore["getState"]>;
export type AppDispatch = AppStore["dispatch"];
