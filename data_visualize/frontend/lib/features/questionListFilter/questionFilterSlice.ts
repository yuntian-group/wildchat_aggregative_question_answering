import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import type { RootState } from "../../store";


export interface questionListFilterState {
  conditions: string[],
  target: string[],
}

const initialState: questionListFilterState= {
  conditions: [],
  target: [],
};

interface QuestionListFilterPayload {
  operator: 'add' | 'remove';
  field: 'conditions' | 'target';
  value: string;
}

export const questionListFilterSlice = createSlice({
  name: "category",
  initialState,
  reducers: {
    updateQuestionListFilter: (state, action: PayloadAction<QuestionListFilterPayload>) => {   
      if (action.payload.operator === 'add') {
        state[action.payload.field].push(action.payload.value);
      } else if (action.payload.operator === 'remove') {
        state[action.payload.field] = state[action.payload.field].filter((item) => item !== action.payload.value);
      }
    }
  },
});

export const {updateQuestionListFilter } =questionListFilterSlice.actions;

export const questionFilterState = (state: RootState) => state.questionListFilter;

export default questionListFilterSlice.reducer;
