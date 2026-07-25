import { combineReducers, configureStore } from "@reduxjs/toolkit";
import {
  FLUSH,
  PAUSE,
  PERSIST,
  persistReducer,
  persistStore,
  PURGE,
  REGISTER,
  REHYDRATE
} from "redux-persist";
import storage from "redux-persist/lib/storage";
import { rootApi } from "@/core/api/rootApi";
import authReducer from "@/features/auth/store/authSlice";
import uiReducer from "@/store/uiSlice";

const rootReducer = combineReducers({
  auth: authReducer,
  ui: uiReducer,
  [rootApi.reducerPath]: rootApi.reducer
});

const persistedReducer = persistReducer(
  {
    key: "rpex-crm",
    storage,
    whitelist: ["ui"]
  },
  rootReducer
);

export const store = configureStore({
  reducer: persistedReducer,
  middleware: getDefaultMiddleware =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: [FLUSH, REHYDRATE, PAUSE, PERSIST, PURGE, REGISTER]
      }
    }).concat(rootApi.middleware)
});

export const persistor = persistStore(store);

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
