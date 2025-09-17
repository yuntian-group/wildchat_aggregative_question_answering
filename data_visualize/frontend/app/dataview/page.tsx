"use client";

import { fetchQuestionList } from "@/lib/features/questionListFetch/questionListFetchSlice";
import { fetchQuestionData } from "@/lib/features/questionDataFetch/questionDataFetchSlice";
import { fetchTopicData } from "@/lib/features/topicDataFetch/topicDataFetchSlice";
import { useAppDispatch, useAppSelector } from "@/lib/hooks";
import { RootState } from "@/lib/store";

import { useEffect, useState} from "react";
import QuestionList from "../components/QuestionList";
import { QuestionPanel } from "../components/QuestionPanel";
import WarningModal from "../components/WarningModal"; 


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
    dispatch(fetchQuestionList({}));
    dispatch(fetchQuestionData(""));
  }, []);

  return (
    <>
    {showWarning && <WarningModal onAcknowledge={acknowledgeWarning} />}
    <div className="w-full h-full flex flex-row max-w-full max-h-full overflow-hidden">
      <QuestionList />
      <QuestionPanel />
    </div>
    </>
  );
}
