"use client";

import Checkbox from "@mui/material/Checkbox";
import ListItemButton from "@mui/material/ListItemButton";
import ExpandLess from "@mui/icons-material/ExpandLess";
import ExpandMore from "@mui/icons-material/ExpandMore";
import Collapse from "@mui/material/Collapse";
import React from "react";
import List from "@mui/material/List";
import Typography from "@mui/material/Typography";
import { styled } from "@mui/material";
import { selectTopic, deselectTopic, selectSubtopic, deselectSubTopic, selectedTopics, isPartialSelected } from "@/lib/features/topic/topicSlice";
import { useAppDispatch, useAppSelector } from "@/lib/hooks";
import { Taxonomy } from "@/lib/features/topicDataFetch/topicDataFetchSlice";

interface NestedCheckboxesProps {
  content: Taxonomy;
}

const StyledCheckbox = styled(Checkbox)(({ theme }) => ({
  padding: 0, // Remove default padding
  marginRight: theme.spacing(1), // Add some spacing to the right
  // color of the checkbox
  color: "rgb(34, 51, 103)",
  "&.Mui-checked": {
    color: "rgb(34, 51, 103)",
  },
  borderRadius: 0,
}));

const SingleCheckbox: React.FC<NestedCheckboxesProps> = ({ content }) => {
  const isSelected = useAppSelector(selectedTopics)[content.index];
  const dispatch = useAppDispatch();
  return (
    <ListItemButton>
      <StyledCheckbox
        checked={isSelected}
        onChange={(e) => {
          handleSubtopicCheckboxChange(e, content.index, content.class_name, dispatch);
        }}
        sx={{ "& .MuiSvgIcon-root": { fontSize: "1.125rem" }, marginLeft: "0.125rem" }}
      />
      <Typography sx={{ fontSize: "0.813rem", fontFamily: "inherit" }}>
        {content.class_name}
      </Typography>
    </ListItemButton>
  );
};

const handleSubtopicCheckboxChange = (
  event: React.ChangeEvent<HTMLInputElement>,
  topicKey: string,
  topicName: string,
  dispatch: any
) => {
  if (event.target.checked) {
    dispatch(selectSubtopic({ id: topicKey, name: topicName }));
  } else {
    dispatch(deselectSubTopic({ id: topicKey, name: topicName }));
  }
}


const handleCheckboxChange = (
  event: React.ChangeEvent<HTMLInputElement>,
  topicKey: string,
  topicName: string,
  dispatch: any
) => {
  if (event.target.checked) {
    dispatch(selectTopic({ id: topicKey, name: topicName }));
  } else {
    dispatch(deselectTopic({ id: topicKey, name: topicName }));
  }
};


export const NestedCheckboxes: React.FC<NestedCheckboxesProps> = ({
  content,
}) => {
  const [isOpen, setIsOpen] = React.useState(false);
  const dispatch = useAppDispatch();
  const isSelected = useAppSelector(selectedTopics)[content.index];
  const isPartiallySelected = useAppSelector(isPartialSelected)[content.index];

  if (content.sub_classes && content.sub_classes.length > 0) {

    return (
      <React.Fragment>
        <ListItemButton key={content.index}>
          <StyledCheckbox
            sx={{ "& .MuiSvgIcon-root": { fontSize: "1.25rem" } }}
            checked={isSelected}
            indeterminate={isPartiallySelected}
            onChange={(e) => {
              handleCheckboxChange(e, content.index, content.class_name, dispatch);
            }}
          />
          <Typography
            sx={{
              fontSize: "0.8125rem",
              fontFamily: "inherit",
              fontWeight: 900,
              cursor: "pointer",
              userSelect: "none",
            }}
          >
            {content.class_name}
          </Typography>
          {isOpen ? (
            <ExpandLess onClick={() => setIsOpen(false)} />
          ) : (
            <ExpandMore onClick={() => setIsOpen(true)} />
          )}
        </ListItemButton>
        <Collapse in={isOpen} timeout="auto" unmountOnExit>
          <List component="div" disablePadding>
            {content.sub_classes.map((item) => {
              return <SingleCheckbox content={{
                ...item,
                index: content.index + "." + item.index
              }} key={content.index + "." + item.index} />;
            })}
          </List>
        </Collapse>
      </React.Fragment>
    );
  }

  return (
    <ListItemButton>
      <StyledCheckbox
        sx={{ "& .MuiSvgIcon-root": { fontSize: 20 } }}
        onChange={(e) => {
          handleCheckboxChange(e, content.index, content.class_name, dispatch);
        }}
      />
      <Typography sx={{ fontSize: 13, fontFamily: "inherit", fontWeight: 900 }}>
        {content.class_name}
      </Typography>
    </ListItemButton>
  );
};
