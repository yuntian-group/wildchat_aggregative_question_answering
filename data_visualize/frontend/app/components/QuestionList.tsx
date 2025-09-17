"use client"
import React from 'react';
import { RootState } from "@/lib/store";
import { useAppSelector, useAppDispatch } from "@/lib/hooks";
import { fetchQuestionData } from '@/lib/features/questionDataFetch/questionDataFetchSlice';
import {fetchDialogueContextByQuestionHash } from '@/lib/features/dialogueDataFetch/dialogueDataFetchSlice';
import {QuestionTypeFilter} from "./QuestionTypeFilter";

type QuestionListProps = {};

const QuestionList: React.FC<QuestionListProps> = ({}) => {
    const questionList = useAppSelector((state: RootState) => state.questionListFetch.data);
    const questionListStatus = useAppSelector((state: RootState) => state.questionListFetch.status);

    const dispatch = useAppDispatch();

    const handleClick = (questionItem: any) => {
        console.log("Clicked question:", questionItem);
        dispatch(fetchQuestionData(questionItem.hash));
        dispatch(fetchDialogueContextByQuestionHash(questionItem.hash));
    };

    if (questionListStatus !== 'idle') {
        return (
            <div className="w-1/5 h-full flex items-center justify-center border-r border-gray-300 p-4 max-h-full">
                Loading...
            </div>
        );
    }

    return (
        <div className="w-1/5 h-full overflow-hidden border-r border-gray-300 max-h-full">
            <div style={{height: "5%"}}>
                <QuestionTypeFilter />
            </div>
            <div className="overflow-y-auto p-2" style={{height: "95%"}}>
            <ul>
                {questionList.map((question_item, index) => (
                    <li
                        key={index}
                        onClick={() => handleClick(question_item)}
                        className="mb-2 p-3 bg-white border border-gray-300 hover:bg-blue-50 hover:border-blue-300 cursor-pointer transition ease-in-out duration-150"
                    >
                        <div>{question_item.question}</div>
                        <div className="text-xs text-gray-500">
                            hash: {question_item.hash}
                        </div>
                    </li>
                ))}
            </ul>
            </div>
        </div>
    );
};

export default QuestionList;