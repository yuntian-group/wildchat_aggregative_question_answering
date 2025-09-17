import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import type { RootState } from "../../store";

export const LANGUAGE_NAME = "Language";
export const COUNTRY_NAME = "Country";
export const USER_NAME = "User";
export const KEYWORDS_NAME = "Keywords";
export const KEYWORDS_AGGREGATED_NAME = "Keywords Aggregated";

export interface CategoryState {
  selected_language: string[];
  selected_country: string[];
  selected_user: string[];
  selected_keywords: string[];
  selected_keywords_aggregated: string[];
}

const initialState: CategoryState = {
  selected_language: [],
  selected_country: [],
  selected_user: [],
  selected_keywords: [],
  selected_keywords_aggregated: [],
};

interface CategoryPayload {
  category: string;
  value: string[];
}

export const categorySlice = createSlice({
  name: "category",
  initialState,
  reducers: {
    selectCategory: (state, action: PayloadAction<CategoryPayload>) => {
      const category = action.payload.category;
      if (category === LANGUAGE_NAME) {
        state.selected_language = state.selected_language.concat(
          action.payload.value
        );
      } else if (category === COUNTRY_NAME) {
        state.selected_country = state.selected_country.concat(
          action.payload.value
        );
      } else if (category === USER_NAME) {
        state.selected_user = state.selected_user.concat(action.payload.value);
      } else if (category === KEYWORDS_NAME) {
        state.selected_keywords = state.selected_keywords.concat(
          action.payload.value
        );
      } else if (category === KEYWORDS_AGGREGATED_NAME) {
        state.selected_keywords_aggregated = state.selected_keywords_aggregated.concat(
          action.payload.value
        );
      }
    },
    deselectCategory: (state, action: PayloadAction<CategoryPayload>) => {
      const category = action.payload.category;
      if (category === LANGUAGE_NAME) {
        state.selected_language = state.selected_language.filter(
          (l) => !action.payload.value.includes(l)
        );
      } else if (category === COUNTRY_NAME) {
        state.selected_country = state.selected_country.filter(
          (l) => !action.payload.value.includes(l)
        );
      } else if (category === USER_NAME) {
        state.selected_user = state.selected_user.filter(
          (l) => !action.payload.value.includes(l)
        );
      } else if (category === KEYWORDS_NAME) {
        state.selected_keywords = state.selected_keywords.filter(
          (l) => !action.payload.value.includes(l)
        );
      } else if (category === KEYWORDS_AGGREGATED_NAME) {
        state.selected_keywords_aggregated = state.selected_keywords_aggregated.filter(
          (l) => !action.payload.value.includes(l)
        );
      }
    },
  },
});

export const { selectCategory, deselectCategory } = categorySlice.actions;

export const selectedCategory = (state: RootState) => state.category;

export default categorySlice.reducer;
