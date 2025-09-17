import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import { getQuestionList } from "@/lib/apis/api";

export interface QuestionData {
    question: string;
    hash: string;
    }   

export interface QuestionListFetchState {
  data: Array<QuestionData>;
  status: 'idle' | 'loading' | 'failed'
  error?: string | null
}

const initialState: QuestionListFetchState = {
  data: [],
  status: 'idle',
  error: null
};

export const fetchQuestionList = createAsyncThunk<any, { condition?: string; target?: string }>(
  "questionListFetch/fetchQuestionList",
  async ({ condition, target }) => {
    return await getQuestionList(condition, target);
  }
);

export const questionListFetchSlice = createSlice({
  name: "questionListFetch",
  initialState,
  reducers: {
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchQuestionList.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(fetchQuestionList.fulfilled, (state, action) => {
        state.status = 'idle';
        state.data = action.payload;
      })
      .addCase(fetchQuestionList.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.error.message; 
      });
  },
});

export default questionListFetchSlice.reducer;
