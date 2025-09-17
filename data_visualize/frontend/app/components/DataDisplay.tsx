import * as React from "react";
import { DataDialogueDisplay } from "./DataDialogueDisplay";
import { DataResultStatistics } from "./DataResultStatistics";
import { useState} from "react";

export const DataDisplay: React.FC = () => {
  // return <DataResultStatistics/>;
  const [activeTab, setActiveTab] = useState<"dialogue" | "statistics">(
    "statistics"
  );

  return <div className="mt-0 h-full flex flex-col border-b border-blue-300">
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
        <div style={{ backgroundColor: "#f0f4f8", height: "95%" }}>
          {activeTab === "dialogue" ? (
            <DataDialogueDisplay />
          ) : (
            <DataResultStatistics numRecordPerTable={10} />
          )}
        </div>
      </div>

};
