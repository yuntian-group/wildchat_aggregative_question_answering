import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import { getKeywordsList } from "@/lib/apis/api";

export interface KeywordsDataFetchState {
  data: Array<string>;
  status: 'idle' | 'loading' | 'failed'
  error?: string | null
}

const initialState: KeywordsDataFetchState = {
  data: [],
  status: 'idle',
  error: null
};

export const fetchKeywordsData = createAsyncThunk(
  "keywordsDataFetch/fetchKeywordsData",
  getKeywordsList
);

export const keywordsDataFetchSlice = createSlice({
  name: "keywordsDataFetch",
  initialState,
  reducers: {
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchKeywordsData.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(fetchKeywordsData.fulfilled, (state, action) => {
        state.status = 'idle';
        state.data = action.payload;
      })
      .addCase(fetchKeywordsData.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.error.message; 
      });
  },
});

export default keywordsDataFetchSlice.reducer;



