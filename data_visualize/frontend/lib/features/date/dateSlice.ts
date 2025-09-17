import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import type { RootState } from "../../store";

export const LANGUAGE_NAME = "Language";
export const COUNTRY_NAME = "Country";
export const USER_NAME = "User";

export interface DateRangeState {
    start_date: string;
    end_date: string;
}

const initialState: DateRangeState= {
    start_date: "2023-04-08",
    end_date: "2024-04-30",
};

interface DateRangePayload {
    start_date: string;
    end_date: string;
}

export const dateRangeSlice = createSlice({
  name: "category",
  initialState,
  reducers: {
    updateDateRange: (state, action: PayloadAction<DateRangePayload>) => {   
      state.start_date = action.payload.start_date;
      state.end_date = action.payload.end_date;
    }
  },
});

export const { updateDateRange } = dateRangeSlice.actions;

export const dateRange = (state: RootState) => state.dateRange;

export default dateRangeSlice.reducer;
