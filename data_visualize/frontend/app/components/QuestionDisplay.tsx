import { useAppSelector } from "@/lib/hooks";

interface QuestionPanelProps {}

export const QuestionDisplay: React.FC<QuestionPanelProps> = () => {
  const questionData = useAppSelector((state) => state.questionDataFetch.data);
  const questionDataStatus = useAppSelector(
    (state) => state.questionDataFetch.status
  );

  if (questionDataStatus === "loading") {
    return (
      <div className="w-full h-1/5 flex justify-center items-center">
        <svg
          className="animate-spin h-8 w-8 text-blue-500"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          ></circle>
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
          ></path>
        </svg>
      </div>
    );
  }

  console.log("Question data:", questionData);

  return (
    <div className="w-full overflow-y-auto h-1/5" style={{ backgroundColor: "white" }}>
      <div className="p-4">
        <div className="text-l font-semibold">{questionData.question}</div>
      </div>
    {(() => {
      const getColor = (weight: number): string => {
        // Clamp weight to the [0, 1] range
        weight = Math.max(0, Math.min(weight, 1));
        const stops = [
        { weight: 0, color: [230, 230, 230] }, // lightgrey
        { weight: 0.25, color: [135, 206, 250] },
        { weight: 0.5, color: [0, 120, 254] },
        { weight: 0.75, color: [0, 82, 204] },
        { weight: 1, color: [34, 51, 103] },
        ];
        let lower = stops[0],
        upper = stops[stops.length - 1];
        for (let i = 0; i < stops.length - 1; i++) {
        if (weight >= stops[i].weight && weight <= stops[i + 1].weight) {
          lower = stops[i];
          upper = stops[i + 1];
          break;
        }
        }
        const range = upper.weight - lower.weight;
        const factor = range === 0 ? 0 : (weight - lower.weight) / range;
        const interpolated = lower.color.map((start, i) =>
        Math.round(start + factor * (upper.color[i] - start))
        );
        return `rgb(${interpolated[0]}, ${interpolated[1]}, ${interpolated[2]})`;
      };
        return (
          <div className="grid grid-cols-5 grid-rows-2 gap-2 w-full p-2">
            {questionData.options.map((option, index) => (
              <div
                key={index}
                className="flex flex-row justify-between items-center p-2"
                style={{
                  backgroundColor: getColor(questionData.option_weights[index]),
                  color: questionData.option_weights[index] > 0.25 ? "white" : "black",
                }}
              >
                <div className="flex flex-row items-center">
                <span className="text-sm font-bold">
                  {String.fromCharCode(65 + index)}.
                </span>
                <div className="text-sm ml-2">{option}</div>
                </div>
                <div className="text-xs" style={{ color: questionData.option_weights[index] > 0.25 ? "white" : "black" }}>
                  {!isNaN(questionData.option_weights[index])
                    ? questionData.option_weights[index].toFixed(3)
                    : questionData.option_weights[index]}
                </div>
              </div>
            ))}
          </div>
        );
      })()}
    </div>
  );
};
