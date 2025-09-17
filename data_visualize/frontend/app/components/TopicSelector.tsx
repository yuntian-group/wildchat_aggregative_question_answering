import React from "react";
import List from "@mui/material/List";
import ListSubheader from "@mui/material/ListSubheader";
import { NestedCheckboxes } from "./NestedCheckbox";
import { useAppSelector } from "@/lib/hooks";

interface TopicSelectorProps {}

export const TopicSelector: React.FC<TopicSelectorProps> = () => {

  const dataFetchStatus = useAppSelector((state) => state.topicDataFetch.status);
  const taxonomy = useAppSelector((state) => state.topicDataFetch.data);

  return (
    <div className="w-1/5 h-full overflow-y-auto">
      <List
        subheader={
          <ListSubheader
            component="div"
            sx={{
              fontSize: "1.125rem",
              fontFamily: "inherit",
              color: "white",
              backgroundColor: "rgb(0, 120, 254)",
            }}
          >
            Topic List
          </ListSubheader>
        }
      >
        {dataFetchStatus === "loading" && <div>Loading...</div>}
        {dataFetchStatus === "failed" && <div>Failed to load data.</div>}
        {dataFetchStatus === "idle" && taxonomy.map((item) => {
          return <NestedCheckboxes content={item} key={item.index} />;
        })}
      </List>
    </div>
  );
};
