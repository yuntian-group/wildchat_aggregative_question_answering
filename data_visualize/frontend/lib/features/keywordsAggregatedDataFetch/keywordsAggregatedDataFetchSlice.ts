import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import { getKeywordsAggregatedList} from "@/lib/apis/api";

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

export const fetchKeywordsAggregatedData = createAsyncThunk(
  "keywordsAggregatedDataFetch/fetchKeywordsAggregatedData",
  getKeywordsAggregatedList
);

export const keywordsDataFetchSlice = createSlice({
  name: "keywordsAggregatedDataFetch",
  initialState,
  reducers: {
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchKeywordsAggregatedData.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(fetchKeywordsAggregatedData.fulfilled, (state, action) => {
        state.status = 'idle';
        state.data = action.payload;
      })
      .addCase(fetchKeywordsAggregatedData.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.error.message; 
      });
  },
});

export default keywordsDataFetchSlice.reducer;



