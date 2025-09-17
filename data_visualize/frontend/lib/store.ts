import { configureStore, ThunkAction, Action } from '@reduxjs/toolkit'
import topicReducer from './features/topic/topicSlice'
import categoryReducer from './features/category/categorySlice'
import dateRangeReducer from './features/date/dateSlice'
import topicDataFetchReducer from './features/topicDataFetch/topicDataFetchSlice'
import languageDataFetchReducer from './features/languageDataFetch/languageDataFetchSlice'
import countryDataFetchReducer from './features/countryDataFetch/countryDataFetchSlice'
import userDataFetchReducer from './features/userDataFetch/userDataFetchSlice'
import keywordsDataFetchSlice from './features/keywordsDataFetch/keywordsDataFetchSlice'
import keywordsAggregatedDataFetchSlice from './features/keywordsAggregatedDataFetch/keywordsAggregatedDataFetchSlice'
import dialogueDataFetchSlice from './features/dialogueDataFetch/dialogueDataFetchSlice'
import questionListFetchSlice from './features/questionListFetch/questionListFetchSlice'
import  questionDataFetchSlice from './features/questionDataFetch/questionDataFetchSlice'
import questionFilterSlice from './features/questionListFilter/questionFilterSlice'
import fewshotExampleDataFetchSlice from './features/fewshotExamplesDataFetch/fewshotExampleDataFetchSlice'


export const makeStore = () => {
  return configureStore({
    reducer: {
      topic: topicReducer,
      category: categoryReducer,
      dateRange : dateRangeReducer,
      topicDataFetch: topicDataFetchReducer,
      languageDataFetch: languageDataFetchReducer,
      countryDataFetch: countryDataFetchReducer,
      userDataFetch: userDataFetchReducer,
      keywordsDataFetch: keywordsDataFetchSlice,
      keywordsAggregatedDataFetch: keywordsAggregatedDataFetchSlice,
      dialogueDataFetch: dialogueDataFetchSlice,
      questionListFetch: questionListFetchSlice,
      questionDataFetch: questionDataFetchSlice,
      questionListFilter: questionFilterSlice,
      fewshotExampleDataFetch: fewshotExampleDataFetchSlice
    }
  })
}

// Infer the type of makeStore
export type AppStore = ReturnType<typeof makeStore>
// Infer the `RootState` and `AppDispatch` types from the store itself
export type RootState = ReturnType<AppStore['getState']>
export type AppDispatch = AppStore['dispatch']
export type AppThunk<ReturnType = void> = ThunkAction<
  ReturnType,
  RootState,
  unknown,
  Action<string>
>
