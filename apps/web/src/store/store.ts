import { configureStore } from "@reduxjs/toolkit";

import { uiReducer } from "@/store/ui-slice";

export const createAppStore = () =>
  configureStore({
    reducer: {
      ui: uiReducer,
    },
  });

export type AppStore = ReturnType<typeof createAppStore>;
export type RootState = ReturnType<AppStore["getState"]>;
export type AppDispatch = AppStore["dispatch"];
