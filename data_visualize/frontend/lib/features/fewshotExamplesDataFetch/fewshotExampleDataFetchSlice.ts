import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import { getAnnotationExamples } from "@/lib/apis/api";

export interface FewshotExampleDataFetchState {
  data: Record<string, any>;
  status: "idle" | "loading" | "failed" | "initial";
  error?: string | null;
}

const initialState: FewshotExampleDataFetchState = {
  data: {},
  status: "initial",
  error: null,
};

export const fetchFewshotExampleData = createAsyncThunk(
  "fewshotExampleDataFetch/getAnntationExamples",
  getAnnotationExamples
);

export const fewshotExampleDataFetchSlice = createSlice({
  name: "fewshotExampleDataFetch",
  initialState,
  reducers: {
    clearData: (state) => {
      state.data = {};
      state.status = "initial";
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchFewshotExampleData.pending, (state) => {
        state.status = "loading";
      })
      .addCase(fetchFewshotExampleData.fulfilled, (state, action) => {
        console.log("done", action.payload);
        state.status = "idle";
        state.data = action.payload;
      })
      .addCase(fetchFewshotExampleData.rejected, (state, action) => {
        state.status = "failed";
        state.error = action.error.message;
      });
  },
});

export const { clearData } = fewshotExampleDataFetchSlice.actions;
export default fewshotExampleDataFetchSlice.reducer;
