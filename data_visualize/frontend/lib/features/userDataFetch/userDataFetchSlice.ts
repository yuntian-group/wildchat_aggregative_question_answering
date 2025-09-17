import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import { getUserList } from "@/lib/apis/api";

export interface UserDataFetchState {
  data: Array<string>;
  status: 'idle' | 'loading' | 'failed'
  error?: string | null
}

const initialState: UserDataFetchState = {
  data: [],
  status: 'idle',
  error: null
};

export const fetchUserData = createAsyncThunk(
  "userDataFetch/fetchUserData",
  getUserList
);

export const userDataFetchSlice = createSlice({
  name: "userDataFetch",
  initialState,
  reducers: {
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchUserData.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(fetchUserData.fulfilled, (state, action) => {
        state.status = 'idle';
        state.data = action.payload;
      })
      .addCase(fetchUserData.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.error.message; 
      });
  },
});

export default userDataFetchSlice.reducer;