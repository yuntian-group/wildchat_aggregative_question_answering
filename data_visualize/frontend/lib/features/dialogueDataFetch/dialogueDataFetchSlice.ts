import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import { getDialgoues, getDialogueContextByQuestionHash} from "@/lib/apis/api";

export interface DialogueDataFetchState {
  data: any;
  status: 'idle' | 'loading' | 'failed' | 'initial';
  error?: string | null;
}

const initialState: DialogueDataFetchState = {
  data: {},
  status: 'initial',
  error: null
};

export const fetchDialogueData = createAsyncThunk(
  "dialogueDataFetch/fetchDialogueData",
  getDialgoues
);

export const fetchDialogueContextByQuestionHash = createAsyncThunk(
  "dialogueDataFetch/fetchDialogueContextByQuestionHash",
  getDialogueContextByQuestionHash
);

export const dialogueDataFetchSlice = createSlice({
  name: "dialogueDataFetch",
  initialState,
  reducers: {
    clearData: (state) => {
      state.data = {};
      state.status = 'initial';
      state.error = null;
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchDialogueData.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(fetchDialogueData.fulfilled, (state, action) => {
        console.log("done", action.payload);
        state.status = 'idle';
        state.data = action.payload;
      })
      .addCase(fetchDialogueData.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.error.message;
      })
      .addCase(fetchDialogueContextByQuestionHash.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(fetchDialogueContextByQuestionHash.fulfilled, (state, action) => {
        state.status = 'idle';
        state.data = action.payload;
      })
      .addCase(fetchDialogueContextByQuestionHash.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.error.message;
      });
  }
});

export const { clearData } = dialogueDataFetchSlice.actions;
export default dialogueDataFetchSlice.reducer;
