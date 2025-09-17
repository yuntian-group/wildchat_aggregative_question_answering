import React, { useState } from "react";
import { QuestionDisplay } from "./QuestionDisplay";
import { DataResultStatistics } from "./DataResultStatistics";
import { DataDialogueDisplay } from "./DataDialogueDisplay";

interface QuestionPanelProps {}

export const QuestionPanel: React.FC<QuestionPanelProps> = () => {
  const [activeTab, setActiveTab] = useState<"dialogue" | "statistics">(
    "statistics"
  );
  const mainBackgroundColor = "#f0f4f8";

  return (
    <div className="w-4/5 h-full overflow-y-auto flex flex-col">
      <QuestionDisplay />
      <div className="mt-0 h-4/5 flex flex-col border-b border-blue-300">
        <div className="flex space-x-4" style={{ height: "5%" }}>
          <button
            className={`px-4 ${
              activeTab === "statistics" ? "border-b-2 font-bold" : ""
            }`}
            onClick={() => setActiveTab("statistics")}
          >
            STATISTICS
          </button>
          <button
            className={`px-4 ${
              activeTab === "dialogue" ? "border-b-2 font-bold" : ""
            }`}
            onClick={() => setActiveTab("dialogue")}
          >
            DIALOGUES
          </button>
        </div>
        <div style={{ backgroundColor: mainBackgroundColor, height: "95%" }}>
          {activeTab === "dialogue" ? (
            <DataDialogueDisplay />
          ) : (
            <DataResultStatistics numRecordPerTable={10} />
          )}
        </div>
      </div>
    </div>
  );
};
