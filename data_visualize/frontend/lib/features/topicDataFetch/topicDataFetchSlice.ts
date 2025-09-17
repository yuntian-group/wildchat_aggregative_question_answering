import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import { getTaxonomy } from "@/lib/apis/api";
import { setTaxonomyData } from "../topic/topicSlice";

export interface Taxonomy {
  class_name: string;
  index: string;
  sub_classes: Array<Taxonomy>;
}

export interface TopicDataFetchState {
  data: Array<Taxonomy>;
  status: 'idle' | 'loading' | 'failed'
  error?: string | null
}

const initialState: TopicDataFetchState = {
  data: [],
  status: 'idle',
  error: null
};

export const fetchTopicData = createAsyncThunk(
  "topicDataFetch/fetchTopicData",
  async (_, {dispatch}) => {
    const data = await getTaxonomy();
    dispatch(setTaxonomyData(data));
    return data;
  }
);

export const topicDataFetchSlice = createSlice({
  name: "topicDataFetch",
  initialState,
  reducers: {
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchTopicData.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(fetchTopicData.fulfilled, (state, action) => {
        state.status = 'idle';
        state.data = action.payload;
      })
      .addCase(fetchTopicData.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.error.message; 
      });
  },
});

export default topicDataFetchSlice.reducer;