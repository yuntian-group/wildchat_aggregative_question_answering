import React, { useState, useRef, useEffect } from "react";
import { styled } from "@mui/material/styles";
import Checkbox from "@mui/material/Checkbox";
import { useAppDispatch, useAppSelector } from "@/lib/hooks";
import { fetchQuestionList } from "@/lib/features/questionListFetch/questionListFetchSlice";
import { updateQuestionListFilter } from "@/lib/features/questionListFilter/questionFilterSlice";

import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import ExpandLessIcon from "@mui/icons-material/ExpandLess";

interface QuestionTypeFilterProps {}

interface FilterOption {
  condition: string;
  target: string;
}

const StyledCheckbox = styled(Checkbox)({
  borderColor: "rgb(34, 51, 103)",
  color: "rgb(34, 51, 103)",
  "&.Mui-checked": {
    color: "rgb(34, 51, 103)",
  },
  margin: 0,
  padding: 0,
});

const conditionToMongodbFieldName: Record<string, string> = {
  "topic": "label_level_1",
  "subtopic": "label_level_2",
  "location": "country",
  "language": "language",
  "time": "time_week",
  "user": "user_name",
  "user pair": "user_name,user_name",
  "user triplet": "user_name,user_name,user_name",
  "keywords_raw": "keywords",
  "keywords": "keywords_aggregated",
  "joint_topic": "label_level_1,label_level_1",
  "joint_subtopic": "label_level_2,label_level_2",
}

export const QuestionTypeFilter: React.FC<QuestionTypeFilterProps> = () => {
  const conditionOptions: string[] = [
    "topic",
    "subtopic",
    "location",
    "language",
    "time",
    "user",
    "user pair",
    "user triplet",
    "keywords",
    "joint_topic",
    "joint_subtopic"
  ];
  const targetOptions: string[] = [
    "topic",
    "subtopic",
    "location",
    "language",
    "user",
    "time",
    "keywords"
  ];


  const [dropdownOpen, setDropdownOpen] = useState(false);

  const dispatch = useAppDispatch();

  const dispatchRequset = (conditions: string[], target: string[]) => {
    // map to mongodb field name

    conditions = conditions.map((condition) => conditionToMongodbFieldName[condition]);
    target = target.map((target) => conditionToMongodbFieldName[target]);

    // concat conditions with `,`      
    const conditionStr = conditions.join(",");
    const targetStr = target[0];

    console.log(conditionStr, targetStr);
    dispatch(fetchQuestionList({ condition : conditionStr, target: targetStr }));
  }

  const filterState = useAppSelector((state) => state.questionListFilter);

  const containerRef = useRef<HTMLDivElement>(null);

  const displayLabel = (selected: string[]): string => {
    return `(${selected.length})`;
  };

  const conditionsLabel = displayLabel(filterState.conditions);
  const targetsLabel = displayLabel(filterState.target);

  const applyFilters = () => {
    dispatchRequset(filterState.conditions, filterState.target);
    setDropdownOpen(false);
  };

  const clearFilters = () => {
    dispatchRequset([], []);
    setDropdownOpen(false);
  };

  const handleConditionChange = (condition: string) => {
    if (filterState.conditions.includes(condition)) {
      dispatch(updateQuestionListFilter({operator: 'remove', field: 'conditions', value: condition}));
    } else {
      dispatch(updateQuestionListFilter({operator: 'add', field: 'conditions', value: condition}));
    }
  }

  const handleTargetChange = (target: string) => {
    if (filterState.target.includes(target)) {
      dispatch(updateQuestionListFilter({operator: 'remove', field: 'target', value: target}));
    } else {
      dispatch(updateQuestionListFilter({operator: 'add', field: 'target', value: target}));
    }
  }

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownOpen &&
        containerRef.current &&
        !containerRef.current.contains(event.target as Node)
      ) {
        setDropdownOpen(false);
      }
    };

    document.addEventListener("click", handleClickOutside);
    return () => {
      document.removeEventListener("click", handleClickOutside);
    };
  }, [dropdownOpen]);

  return (
    <div
      ref={containerRef}
      className="relative w-full h-full flex items-center justify-center"
      style={{ backgroundColor: "rgb(230, 230, 230)" }}
    >
      <div className="w-full flex flex-col items-center">
        <div className="w-full md:w-4/5">
          <button
            onClick={() => setDropdownOpen(!dropdownOpen)}
            className="w-full px-1 py-1 text-sm flex flex-row items-center justify-between border-b-2 border-gray-300 hover:border-black active:border-black"
          >
            <div style={{ fontFamily: "inherit", fontWeight: "bold" }}>
              CONDITION {conditionsLabel}
            </div>
            <div style={{ fontFamily: "inherit", fontWeight: "bold" }}>
              TARGET {targetsLabel}
            </div>
            {dropdownOpen ? <ExpandLessIcon /> : <ExpandMoreIcon />}
          </button>
          {dropdownOpen && (
            <div className="absolute w-full md:w-4/5 mt-1 p-2 flex flex-col bg-white border border-gray-300 z-10">
              <div className="flex flex-row">
                <div className="w-1/2">
                  <div className="font-bold p-1">Condition</div>
                  <ul>
                    {conditionOptions.map((option) => (
                      <li key={option} className="p-1">
                        <label className="flex items-center space-x-2 cursor-pointer">
                          <StyledCheckbox
                            checked={filterState.conditions.includes(option)}
                            onChange={() => {handleConditionChange(option)}}
                            size="small"
                          />
                          <span>{option}</span>
                        </label>
                      </li>
                    ))}
                  </ul>
                </div>
                <div className="w-1/2">
                  <div className="font-bold p-1">Target</div>
                  <ul>
                    {targetOptions.map((option) => (
                      <li key={option} className="p-1">
                        <label className="flex items-center space-x-2 cursor-pointer">
                          <StyledCheckbox
                            checked={filterState.target.includes(option)}
                            onChange={() => {handleTargetChange(option)}}
                            size="small"
                          />
                          <span>{option}</span>
                        </label>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
              <div className="mt-4 flex justify-end space-x-2">
                <button
                  onClick={clearFilters}
                  style={{
                    backgroundColor: "rgb(34, 51, 103)",
                    color: "white",
                  }}
                  className="px-3 py-1 text-sm bg-red-500 hover:bg-red-600"
                >
                  Clear
                </button>
                <button
                  onClick={applyFilters}
                  style={{
                    backgroundColor: "rgb(34, 51, 103)",
                    color: "white",
                  }}
                  className="px-3 py-1 text-sm bg-green-500 hover:bg-green-600"
                >
                  Apply
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
