import React from "react";
import { RootState } from "@/lib/store";
import { useAppSelector } from "@/lib/hooks";
import { selectedTopicList} from "@/lib/features/topic/topicSlice";
import { selectedCategory } from "@/lib/features/category/categorySlice";
import { dateRange } from "@/lib/features/date/dateSlice";

interface ActiveFilterCondtionDisplayProps {}

export const ActiveFilterCondtionDisplay: React.FC<
  ActiveFilterCondtionDisplayProps
> = ({}) => {
  const curSelectedTopicsList = useAppSelector(selectedTopicList);
  const { selected_language, selected_country, selected_user, selected_keywords } = useAppSelector(
    (state: RootState) => selectedCategory(state)
  );
  const curDateRange = useAppSelector(dateRange);

  if (
    curSelectedTopicsList.length === 0 &&
    selected_language.length === 0 &&
    selected_country.length === 0 &&
    selected_user.length === 0 && 
    selected_keywords.length === 0
  ) {
    return (
      <React.Fragment>
        {curDateRange.start_date} - {curDateRange.end_date}
        <h1>Active Filter Conditions</h1>
        <div>No active filter conditions</div>
      </React.Fragment>
    );
  }

  return (
    <React.Fragment>
      {curDateRange.start_date} - {curDateRange.end_date}
      <h1>Active Filter Conditions</h1>
      <div>
        {curSelectedTopicsList.map((x) => (
          <div key={x.id}>{x.name}</div>
        ))}
        {selected_language.map((x) => (
          <div key={x}>{x}</div>
        ))}
        {selected_country.map((x) => (
          <div key={x}>{x}</div>
        ))}
        {selected_user.map((x) => (
          <div key={x}>{x}</div>
        ))}
        {selected_keywords.map((x) => (
          <div key={x}>{x}</div>
        ))}
      </div>
    </React.Fragment>
  );
};
