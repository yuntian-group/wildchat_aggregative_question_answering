import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import { getQuestionByHash } from "@/lib/apis/api";

export interface QuestionData {
  question: string;
  hash: string;
  options: Array<string>;
  option_weights: Array<number>;
  condition_type: Array<string>;
  condition_value: Array<string>;
  target_type: string;
}

export interface QuestionDataFetchState {
  data: QuestionData;
  status: 'idle' | 'loading' | 'failed'
  error?: string | null
}

const initialState: QuestionDataFetchState = {
  data: {
    question: '',
    hash: '',
    options: [],
    option_weights: [],
    condition_type: [],
    condition_value: [],
    target_type: ''
  },
  status: 'idle',
  error: null
};

export const fetchQuestionData = createAsyncThunk(
  "questionDataFetch/fetchQuestionData",
  getQuestionByHash
);

export const questionDataFetchSlice = createSlice({
  name: "questionDataFetch",
  initialState,
  reducers: {
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchQuestionData.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(fetchQuestionData.fulfilled, (state, action) => {
        state.status = 'idle';
        state.data = action.payload;
      })
      .addCase(fetchQuestionData.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.error.message; 
      });
  },
});

export default questionDataFetchSlice.reducer;
