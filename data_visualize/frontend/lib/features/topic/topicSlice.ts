import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import type { RootState } from "../../store";
import { Taxonomy } from "../topicDataFetch/topicDataFetchSlice";

export interface topicWithId {
  id: string;
  name: string;
}

export interface TopicState {
  all_topics: Record<string, Taxonomy>;
  selected_topics: Record<string, boolean>;
  is_partial_selected: Record<string, boolean>;
  selected_topic_list: Array<topicWithId>;
}

const initialState: TopicState = {
  all_topics: {},
  selected_topics: {},
  is_partial_selected: {},
  selected_topic_list: [],
};

const updateSelectedLists = (state: TopicState) => {
  state.selected_topic_list = [];
  for (const key of Object.keys(state.selected_topics).sort()) {
    // first check leve 1 topics
    if (key.indexOf(".") === -1) {
      if (state.selected_topics[key]){
        state.selected_topic_list.push({id: key, name: state.all_topics[key].class_name});
        state.is_partial_selected[key] = false;
      } else {
        // if the parent topic is not selected, then all subtopics should be checked
        let selectCount = 0;
        const curTaxonomy = state.all_topics[key];
        for (const subtopic of curTaxonomy.sub_classes) {
          const subtopicIndex = `${key}.${subtopic.index}`;
          if (state.selected_topics[subtopicIndex]) {
            state.selected_topic_list.push({id: subtopicIndex, name: subtopic.class_name});
            selectCount++;
          } 
        }

        if (selectCount > 0 && selectCount < curTaxonomy.sub_classes.length) {
          state.is_partial_selected[key] = true;
        } else {
          state.is_partial_selected[key] = false;
        }

      }
    }
  }
};

export const topicSlice = createSlice({
  name: "topic",
  initialState,
  reducers: {
    setTaxonomyData: (state, action: PayloadAction<Array<Taxonomy>>) => {
      const taxonomy = action.payload;
      for (const topic of taxonomy) {
        state.selected_topics[topic.index] = false;
        state.all_topics[topic.index] = topic;
        for (const subtopic of topic.sub_classes) {
          const subtopicIndex = `${topic.index}.${subtopic.index}`;
          state.selected_topics[subtopicIndex] = false;
          state.all_topics[subtopicIndex] = subtopic;
        }
      }
    },
    selectTopic: (state, action: PayloadAction<topicWithId>) => {
      const curTopicToSelect = action.payload;
      state.selected_topics[curTopicToSelect.id] = true;
      const curTaxonomy = state.all_topics[curTopicToSelect.id];
      for (const subtopic of curTaxonomy.sub_classes) {
        const subtopicIndex = `${curTopicToSelect.id}.${subtopic.index}`;
        state.selected_topics[subtopicIndex] = true;
      }
      updateSelectedLists(state);
    },
    deselectTopic: (state, action: PayloadAction<topicWithId>) => {
      const curTopicToDeselect = action.payload;
      state.selected_topics[curTopicToDeselect.id] = false;
      const curTaxonomy = state.all_topics[curTopicToDeselect.id];
      for (const subtopic of curTaxonomy.sub_classes) {
        const subtopicIndex = `${curTopicToDeselect.id}.${subtopic.index}`;
        state.selected_topics[subtopicIndex] = false;
      }
      updateSelectedLists(state);
    },
    selectSubtopic: (state, action: PayloadAction<topicWithId>) => {
      const curSubTopicToSelect = action.payload;
      state.selected_topics[curSubTopicToSelect.id] = true;
      const topicIndex = curSubTopicToSelect.id.split(".")[0];
      const curTaxonomy = state.all_topics[topicIndex];
      const subtopics = curTaxonomy.sub_classes;
      const allSubTopicsSelected = subtopics.every(
        (subtopic) => state.selected_topics[`${topicIndex}.${subtopic.index}`]
      );
      if (allSubTopicsSelected) {
        state.selected_topics[topicIndex] = true;
      }
      updateSelectedLists(state);
    },
    deselectSubTopic: (state, action: PayloadAction<topicWithId>) => {
      const curSubTopicToDeselect = action.payload;
      state.selected_topics[curSubTopicToDeselect.id] = false;
      const parentTopicIndex = curSubTopicToDeselect.id.split(".")[0];
      state.selected_topics[parentTopicIndex] = false;
      updateSelectedLists(state);
    },
  },
});

export const { selectTopic, deselectTopic, selectSubtopic, deselectSubTopic, setTaxonomyData } = topicSlice.actions;

export const selectedTopics = (state: RootState) => state.topic.selected_topics;
export const selectedTopicList = (state: RootState) => state.topic.selected_topic_list;
export const isPartialSelected = (state: RootState) => state.topic.is_partial_selected;
export const allTopics = (state: RootState) => state.topic.all_topics;

export default topicSlice.reducer;
