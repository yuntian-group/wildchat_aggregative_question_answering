import * as React from "react";
import { RootState } from "@/lib/store";
import { DateRangeSelector } from "./DateRangeSelector";
import { CategorySelector } from "./CategorySelector";
import { KeywordsSearchBar } from "./KeywordsSearchBar";
import { Divider } from "@mui/material";
import { useAppSelector, useAppDispatch } from "@/lib/hooks";
import { IconButton } from "@mui/material";
import SearchIcon from "@mui/icons-material/Search";
import { fetchDialogueData } from "@/lib/features/dialogueDataFetch/dialogueDataFetchSlice";
import { selectedCategory } from "@/lib/features/category/categorySlice";
import { dateRange } from "@/lib/features/date/dateSlice";
import {
  KEYWORDS_NAME,
  KEYWORDS_AGGREGATED_NAME,
} from "@/lib/features/category/categorySlice";


const InputWidth = "22.5%";
interface TopFilterBarProps {}

export const TopFilterBar: React.FC<TopFilterBarProps> = ({}) => {
  const languageListStatus = useAppSelector(
    (state) => state.languageDataFetch.status
  );
  const countryListStatus = useAppSelector(
    (state) => state.countryDataFetch.status
  );
  const userListStatus = useAppSelector((state) => state.userDataFetch.status);
  const languageList = useAppSelector((state) => state.languageDataFetch.data);
  const countryList = useAppSelector((state) => state.countryDataFetch.data);
  const userList = useAppSelector((state) => state.userDataFetch.data);

  const dispatch = useAppDispatch();

  const [onMouseEnterSearchButton, setOnMouseEnterSearchButton] =
    React.useState<boolean>(false);

  const {
    selected_language = [],
    selected_country = [],
    selected_user = [],
    selected_keywords = [],
    selected_keywords_aggregated = [],
  } = useAppSelector((state: RootState) => selectedCategory(state) || {});
  const dateRangeData = useAppSelector((state: RootState) => dateRange(state));

  const selectedTopicList = useAppSelector((state: RootState) => state.topic);

  const handleDialogueFilterSearchPost = () => {
    const selectedTopicIdList: Array<string> = [];
    for (const topic of selectedTopicList.selected_topic_list) {
      selectedTopicIdList.push(topic.id);
    }

    const dataToPost = {
      keywords: selected_keywords,
      keywords_aggregated: selected_keywords_aggregated,
      language: selected_language,
      region: [],
      user_name: selected_user,
      country: selected_country,
      topics: selectedTopicIdList,
      start_date: dateRangeData.start_date,
      end_date: dateRangeData.end_date,
      page: 0,
      page_size: 10,
    };

    console.log(dataToPost);

    dispatch(fetchDialogueData(dataToPost));
  };

  return (
    <div
      style={{
        backgroundColor: "rgb(248, 249, 250)",
        height: "10rem",
        position: "sticky",
        display: "flex",
        flexDirection: "column",
        justifyContent: "flex-end",
        top: 0,
        padding: "0.75rem",
      }}
    >
      <div
        className="flex-row w-full h-full flex justify-between"
        style={{ maxHeight: "5rem" }}
      >
        <DateRangeSelector width={InputWidth} />
        <Divider orientation="vertical" flexItem />
        <CategorySelector
          width={InputWidth}
          name="Language"
          data={languageList}
          isDataLoaded={languageListStatus !== "loading"}
        />
        <Divider orientation="vertical" flexItem />
        <CategorySelector
          width={InputWidth}
          name="Country"
          data={countryList}
          isDataLoaded={countryListStatus !== "loading"}
        />
        <Divider orientation="vertical" flexItem />
        <CategorySelector
          width={InputWidth}
          name="User"
          data={userList}
          isDataLoaded={userListStatus !== "loading"}
        />
      </div>
      <div
        className="flex-row w-full h-full flex justify-between mt-4 align-bottom"
        style={{ maxHeight: "4rem" }}
      >
        <KeywordsSearchBar width="100%" keywordType={KEYWORDS_NAME}/>
        <KeywordsSearchBar width="100%" keywordType={KEYWORDS_AGGREGATED_NAME}/>
        <IconButton
          type="button"
          sx={{
            borderRadius: "0px",
            backgroundColor: "none", // Changed to match the theme color
            border: "0.125rem solid lightgrey", // Border for the button
            height: "100%", // Match parent height
            width: "3.5rem", // Fixed width for better proportions
            "&:hover": {
              border: "none", // Remove border on hover
              backgroundColor: "rgb(0, 120, 254)", // Slightly lighter shade for hover
            },
            "&:active": {
              border: "none",
              backgroundColor: "rgb(0, 120, 254)", // Slightly darker shade for click
            },
            transition: "background-color 0.2s", // Smooth transition for hover effect
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
          onMouseEnter={() => setOnMouseEnterSearchButton(true)}
          onMouseLeave={() => setOnMouseEnterSearchButton(false)}
          onClick={handleDialogueFilterSearchPost}
        >
          <SearchIcon
            sx={{
              fontSize: "2.25rem", // Slightly reduced size for better proportions
              color: onMouseEnterSearchButton
                ? "white" // Darker shade for hover
                : "rgba(0, 0, 0, 0.6)", // Default color
            }}
          />
        </IconButton>
      </div>
    </div>
  );
};
