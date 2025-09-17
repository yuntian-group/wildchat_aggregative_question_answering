"use client";

import { fetchTopicData } from "@/lib/features/topicDataFetch/topicDataFetchSlice";
import { fetchUserData } from "@/lib/features/userDataFetch/userDataFetchSlice";
import { fetchCountryData } from "@/lib/features/countryDataFetch/countryDataFetchSlice";
import { fetchLanguageData } from "@/lib/features/languageDataFetch/languageDataFetchSlice";
import { fetchKeywordsData } from "@/lib/features/keywordsDataFetch/keywordsDataFetchSlice";
import { fetchDialogueData } from "@/lib/features/dialogueDataFetch/dialogueDataFetchSlice";
import { DataDisplay } from "./components/DataDisplay";
import { TopicSelector } from "./components/TopicSelector";
import { TopFilterBar } from "./components/TopFilterBar";
import { useAppDispatch, useAppSelector } from "@/lib/hooks";
import { RootState } from "@/lib/store";
import { useEffect, useState } from "react";
import WarningModal from "./components/WarningModal"; 
import { fetchKeywordsAggregatedData } from "@/lib/features/keywordsAggregatedDataFetch/keywordsAggregatedDataFetchSlice";

export default function Home() {
  const dispatch = useAppDispatch();
  const topicData = useAppSelector((state: RootState) => state.topicDataFetch.data);
  const [showWarning, setShowWarning] = useState(false);

  const acknowledgeWarning = () => {
    sessionStorage.setItem("contentWarningAcknowledged", "true");
    setShowWarning(false);
  };

  useEffect(() => {

    const acknowledged = sessionStorage.getItem("contentWarningAcknowledged");
    if (!acknowledged) {
      setShowWarning(true);
    }

    if (topicData.length === 0) {
      dispatch(fetchTopicData());
    }
    dispatch(fetchUserData(""));
    dispatch(fetchCountryData());
    dispatch(fetchLanguageData());
    dispatch(fetchKeywordsData(""));
    dispatch(fetchKeywordsAggregatedData(""));
    dispatch(
      fetchDialogueData({
        country: [],
        region: [],
        language: [],
        topics: [],
        user_name: [],
        keywords: [],
        keywords_aggregated: [],
        start_date: "1970-01-01",
        end_date: "2050-01-01",
        page: 1,
        page_size: 10,
      })
    );
  }, []);

  return (
    <>
    {showWarning && <WarningModal onAcknowledge={acknowledgeWarning} />}
    <div className="w-screen h-full flex flex-row max-w-screen max-h-full overflow-hidden">
        <TopicSelector />
        <div className="w-4/5 h-full flex-col flex overflow-hidden">
          <TopFilterBar />
          <div className="flex flex-col w-full h-full overflow-auto">
            {/* <ActiveFilterCondtionDisplay/> */}
            <DataDisplay />
          </div>
        </div>
    </div>
    </>
  );
}
  