import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import { getAllLanguage } from "@/lib/apis/api";

export interface LanguageDataFetchState {
  data: Array<string>;
  status: 'idle' | 'loading' | 'failed'
  error?: string | null
}

const initialState: LanguageDataFetchState = {
  data: [],
  status: 'idle',
  error: null
};

export const fetchLanguageData = createAsyncThunk(
  "languageDataFetch/fetchLanguageData",
  getAllLanguage
);

export const languageDataFetchSlice = createSlice({
  name: "languageDataFetch",
  initialState,
  reducers: {
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchLanguageData.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(fetchLanguageData.fulfilled, (state, action) => {
        state.status = 'idle';
        state.data = action.payload;
      })
      .addCase(fetchLanguageData.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.error.message; 
      });
  },
});

export default languageDataFetchSlice.reducer;
