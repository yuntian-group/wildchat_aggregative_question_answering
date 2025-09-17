import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import { getAllCountry } from "@/lib/apis/api";

export interface CountryDataFetchState {
  data: Array<string>;
  status: 'idle' | 'loading' | 'failed'
  error?: string | null
}

const initialState: CountryDataFetchState = {
  data: [],
  status: 'idle',
  error: null
};

export const fetchCountryData = createAsyncThunk(
  "countryDataFetch/fetchCountryData",
  getAllCountry
);

export const countryDataFetchSlice = createSlice({
  name: "countryDataFetch",
  initialState,
  reducers: {
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchCountryData.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(fetchCountryData.fulfilled, (state, action) => {
        state.status = 'idle';
        state.data = action.payload;
      })
      .addCase(fetchCountryData.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.error.message; 
      });
  },
});

export default countryDataFetchSlice.reducer;