import * as React from "react";
import { RootState } from "@/lib/store";
import { useAppSelector } from "@/lib/hooks";



export const DataDialogueDisplay: React.FC = () => {
    const dialogueData = useAppSelector((state: RootState) => state.dialogueDataFetch.data);
    const dialogueDataStatus = useAppSelector((state: RootState) => state.dialogueDataFetch.status);
    const topicToLabel = useAppSelector((state: RootState) => state.topic.all_topics);


    const showDialogueLabel = (allLabels: string[], topicToLabel: Record<string, any>) => {
        
        const allLabelSorted  = allLabels.toSorted();
        const labelNameList = allLabelSorted.map((label) => {
            const topic = topicToLabel[label];
            if (topic) {
                return topic.class_name;
            }
            return label;
        });
    
        // list of div
        return labelNameList.map((labelName, index) => (
            <div key={index} className="text-sm text-gray-700">
                {labelName}
            </div>
        ));
    
    }

    const showKeywords = (keywords: Array<Record<string, string>>, showDescription: boolean) => {

        if (showDescription) {
            return keywords.map((keyword, index) => (
                <div key={index} className="text-sm text-gray-700">
                    {keyword.value}: {keyword.keyword_type} - {keyword.description}
                </div>
            ));
        }

        return keywords.map((keyword, index) => (
            <div key={index} className="text-sm text-gray-700">
                {keyword.value}: {keyword.keyword_type}
            </div>
        ));
    }


    if (dialogueDataStatus !== "idle") {
        return (
            <div className="w-full h-full bg-gray-100 flex items-center justify-center border-r border-gray-300 p-4 max-h-full">
                Loading...
            </div>
        );
    }

    return (
        <div className="w-full h-full bg-gray-100 overflow-auto border-r border-gray-300 p-4 max-h-full">
            {dialogueData.dialogues.map((dialogue, index) => (
                <div key={index} className="mb-6 p-4 border border-gray-300 bg-white">
                    <div className="mb-2 text-sm text-gray-500">
                        <span>{dialogue.user_name}</span> |{" "}
                        <span>{new Date(dialogue.timestamp).toLocaleString()}</span> |{" "}
                        <span>{dialogue.hash}</span>
                    </div>
                    <div className="mb-4 text-gray-700">
                        {showDialogueLabel(dialogue.labels, topicToLabel)}
                    </div>
                    <div className="mb-4 text-gray-700 italic">
                        Summary: {dialogue.summary}
                    </div>
                    <div className="mb-4 text-gray-700 italic">
                        Keywords: {showKeywords(dialogue.keywords, true)}
                    </div>
                    <div className="mb-4 text-gray-700 italic">
                        Keywords Aggregated: {showKeywords(dialogue.keywords_aggregated, false)}
                    </div>
                    <div>
                        {dialogue.conversation.map((message, i) => (
                            <div key={i} className="mb-2">
                                <strong>{message.role}:</strong> <span>{message.content}</span>
                            </div>
                        ))}
                    </div>
                </div>
            ))}
        </div>
    );
};