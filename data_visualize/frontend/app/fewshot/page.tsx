"use client";
import React from "react";
import { useEffect } from "react";
import { RootState } from "@/lib/store";
import { useAppSelector, useAppDispatch } from "@/lib/hooks";
import { fetchTopicData } from "@/lib/features/topicDataFetch/topicDataFetchSlice";
import { fetchFewshotExampleData } from "@/lib/features/fewshotExamplesDataFetch/fewshotExampleDataFetchSlice";
import { AnnotationExampleDisplay } from "@/app/components/AnnotationExampleDisplay";

export default function Home() {
  const dispatch = useAppDispatch();
  const topicData = useAppSelector(
    (state: RootState) => state.topicDataFetch.data
  );
  useEffect(() => {
    dispatch(fetchFewshotExampleData());
    if (topicData.length === 0) {
      dispatch(fetchTopicData());
    }
  }, []);

  return (
    <div className="w-full h-full flex flex-row max-w-full max-h-full overflow-hidden">
      <AnnotationExampleDisplay />
    </div>
  );
}
