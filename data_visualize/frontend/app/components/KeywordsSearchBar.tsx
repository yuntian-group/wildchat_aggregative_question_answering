import * as React from "react";
import { useState, useEffect, useMemo } from "react";
import { styled } from "@mui/material/styles";
import { RootState } from "@/lib/store";
import Fade from "@mui/material/Fade";
import {
  Paper,
  FormControl,
  FormLabel,
  IconButton,
  TextField,
  Box,
  Button,
} from "@mui/material";
import Popper from "@mui/material/Popper";
import ExpandLess from "@mui/icons-material/ExpandLess";
import ExpandMore from "@mui/icons-material/ExpandMore";
import CloseIcon from "@mui/icons-material/Close";
import { useAppDispatch, useAppSelector } from "@/lib/hooks";
import { fetchKeywordsData } from "@/lib/features/keywordsDataFetch/keywordsDataFetchSlice";
import { fetchKeywordsAggregatedData } from "@/lib/features/keywordsAggregatedDataFetch/keywordsAggregatedDataFetchSlice";
import {
  KEYWORDS_NAME,
  selectCategory,
  deselectCategory,
} from "@/lib/features/category/categorySlice";
import { selectedCategory } from "@/lib/features/category/categorySlice";
import debounce from "lodash.debounce";
import { pages } from "next/dist/build/templates/app-page";

const StyledTextField = styled(TextField)({
  "& .MuiInputBase-root": {
    color: "black", // Text color
    margin: "0 0 0 0",
  },

  "& .MuiOutlinedInput-root": {
    borderRadius: "0",
    "& fieldset": {
      borderWidth: "0 0 0 0",
      borderColor: "lightgrey",
    },
    "&:hover fieldset": {
      borderWidth: "0 0 0 0",
      borderColor: "rgb(34, 51, 103)", // Border color when hovered
      color: "rgb(34, 51, 103)",
    },
    "&.Mui-focused fieldset": {
      borderWidth: "0 0 0 0",
      borderColor: "rgb(34, 51, 103)", // Custom focus border color
      color: "rgb(34, 51, 103)",
    },
    "& .MuiInputBase-input": {
      padding: "0 0 0  0.125rem",
      margin: "0 0 0 0",
      fontSize: "1.25rem",
    },
  },
});

const StyledKeywordsTagButton = styled(Button)({
  "&.MuiButton-root": {
    borderRadius: "0",
    fontWeight: "bold",
    fontSize: "0.75rem",
    margin: "0.25rem",
    padding: "0.1rem 0.2rem 0.1rem 0.2rem",
    width: "max-content",
    minWidth: "max-content",
    textTransform: "none",
  },
});

interface KeyWordsTagsProps {
  name: string;
  isSelected: boolean;
  keywordType: string;
}

const KeyWordsTags: React.FC<KeyWordsTagsProps> = ({ name, isSelected, keywordType }) => {
  const dispatch = useAppDispatch();
  return (
    <StyledKeywordsTagButton
      sx={{
        border: isSelected
          ? "0.15rem solid rgb(0, 120, 254)"
          : "0.15rem solid rgb(34, 51, 103)",
        backgroundColor: isSelected ? "rgb(0, 120, 254)" : "white",
        color: isSelected ? "white" : "rgb(34, 51, 103)",
      }}
      onClick={() => {
        dispatch(
          isSelected
            ? deselectCategory({ category: keywordType, value: [name] })
            : selectCategory({ category: keywordType, value: [name] })
        );
      }}
    >
      {name}
    </StyledKeywordsTagButton>
  );
};

interface KeywordsSearchBarProps {
  width: string;
  keywordType: string;
}

export const KeywordsSearchBar: React.FC<KeywordsSearchBarProps> = ({
  width,
  keywordType,
}) => {
  const fetchDataFunction =
    keywordType === KEYWORDS_NAME ? fetchKeywordsData : fetchKeywordsAggregatedData;
  const [anchorEl, setAnchorEl] = React.useState<HTMLButtonElement | null>(
    null
  );
  const [open, setOpen] = React.useState(false);
  const data = useAppSelector(
    (state: RootState) => {
      return keywordType === KEYWORDS_NAME
        ? state.keywordsDataFetch.data
        : state.keywordsAggregatedDataFetch.data;
    }
  );
  const isDataLoaded =
    useAppSelector((state: RootState) => {
      return keywordType === KEYWORDS_NAME
        ? state.keywordsDataFetch.status
        : state.keywordsAggregatedDataFetch.status
    }) ===
    "idle";

  const [searchText, setSearchText] = React.useState<string>("");
  const [filteredData, setFilteredData] = React.useState<Array<string>>(data);
  const [mouseOnHover, setMouseOnHover] = React.useState(false);

  const formControlRef = React.useRef<HTMLInputElement>(null);
  const popperRef = React.useRef<HTMLDivElement>(null);
  const dispatch = useAppDispatch();

  const { selected_keywords = [], selected_keywords_aggregated = [] } =
    useAppSelector((state: RootState) => selectedCategory(state) || {});

  const cur_list = keywordType === KEYWORDS_NAME ? selected_keywords : selected_keywords_aggregated;

  const handleClick = () => {
    setAnchorEl(formControlRef.current);
    if (!open) {
      setFilteredData(data);
    }
    setOpen((prev) => !prev);
  };

  const handleInputFocus = () => {
    if (open) {
      return;
    }
    if (!formControlRef.current) {
      return;
    }
    setAnchorEl(formControlRef.current);
    setOpen(true);
    setFilteredData(data);
  };

  const handleClickOutside = (event: MouseEvent) => {
    if (
      event.target instanceof Node &&
      formControlRef.current &&
      !formControlRef.current.contains(event.target) &&
      popperRef.current &&
      !popperRef.current.contains(event.target)
    ) {
      setOpen(false); // Close popper when clicked outside
    }
  };

  const maxSearchTextLength = 100;
  const debouncedDelay = 200;

  const debouncedAsyncSearch = useMemo(() => {
    return debounce((searchText: string) => {
      dispatch(fetchDataFunction(searchText));
    }, debouncedDelay);
  }, [dispatch]);

  useEffect(() => {
    return () => {
      debouncedAsyncSearch.cancel();
    };
  }, [debouncedAsyncSearch]);

  const handleAsyncRequestSearch = (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const curSearchText = event.target.value;
    setSearchText(curSearchText);
    debouncedAsyncSearch(curSearchText);
  };

  useEffect(() => {
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  useEffect(() => {
    setFilteredData(data);
  }, [isDataLoaded]);

  const [popperWidth, setPopperWidth] = useState(0);

  // Measure button's width when it changes or on mount
  useEffect(() => {
    if (formControlRef.current) {
      setPopperWidth(formControlRef.current.offsetWidth);
    }

    // Optionally, recalculate on window resize
    const handleResize = () => {
      if (formControlRef.current) {
        setPopperWidth(formControlRef.current.offsetWidth);
      }
    };

    window.addEventListener("resize", handleResize);

    // Cleanup on unmount
    return () => {
      window.removeEventListener("resize", handleResize);
    };
  }, [open]); // Recalculate width if the popper state changes

  return (
    <React.Fragment>
      <Box
        sx={{
          width: width,
          height: "3.5rem",
          display: "flex",
          flexDirection: "row",
          justifyContent: "flex-end",
          alignItems: "flex-end",
        }}
      >
        <FormControl
          ref={formControlRef}
          sx={{
            width: "100%",
            height: "100%",
            display: "flex",
            flexDirection: "row",
            alignItems: "flex-end",
            justifyContent: "space-between",
            borderBottom: open
              ? "0.125rem solid rgb(34, 51, 103)"
              : "0.125rem solid lightgrey",
            ":hover": {
              borderBottom: open
                ? "0.125rem solid rgb(34, 51, 103)"
                : "0.125rem solid rgb(34, 51, 103)",
            },
            marginRight: "1rem",
          }}
          onClick={handleInputFocus}
          onMouseEnter={() => setMouseOnHover(true)}
          onMouseLeave={() => setMouseOnHover(false)}
        >
          <FormLabel
            sx={{
              position: "absolute", // Absolute positioning of label
              top: -8, // Moves the label above the Paper container
              left: 0, // Moves the label to the left
              fontSize: "0.75rem", // Adjust font size as needed
              fontWeight: "bold", // Optional: Make label bold
              backgroundColor: "rgb(248, 249, 250)", // Optional: Prevent label overlap
              padding: "0 0", // Optional: Adds slight padding around label
            }}
          >
            {keywordType === KEYWORDS_NAME ? "Keywords" : "Aggregated Keywords"}{" "}
            (
            {keywordType === KEYWORDS_NAME
              ? selected_keywords.length
              : selected_keywords_aggregated.length}
            )
          </FormLabel>
          <Box
            sx={{
              display: "flex",
              flexDirection: "row",
              width: "100%",
              maxWidth: "100%",
              justifyContent: "flex-start",
              alignItems: "end",
              flexGrow: 1,
            }}
          >
            <Box
              sx={{
                alignItems: "end",
                flexWrap: "nowrap",
                maxHeight: "2.5rem",
                overflowX: "hidden",
                overflowY: "auto",
                maxWidth: "95%",
                minWidth: 0,
              }}
            >
              {
              cur_list.map((name, index) => {
                return (
                  <KeyWordsTags
                    key={index}
                    name={name}
                    isSelected={true}
                    keywordType={keywordType}
                  />
                );
              })}
            </Box>

            <StyledTextField
              sx={{ minWidth: "5%", flexGrow: 1 }}
              onChange={handleAsyncRequestSearch}
              slotProps={{
                htmlInput: {
                  maxLength: maxSearchTextLength,
                },
              }}
            />
          </Box>
          <Box
            sx={{
              display: "flex",
              flexDirection: "row",
              alignItems: "end",
              justifyContent: "flex-end",
              width: "5rem",
              height: "100%",
            }}
          >
            {(mouseOnHover || open) && cur_list.length > 0 && (
              <IconButton type="button" sx={{ borderRadius: "0px" }}>
                <CloseIcon
                  sx={{ color: "lightgrey" }}
                  onClick={() => {
                    dispatch(
                      deselectCategory({
                        category: keywordType,
                        value: cur_list,
                      })
                    );
                  }}
                />
              </IconButton>
            )}
            <IconButton
              type="button"
              onClick={handleClick}
              className="font-bold"
              sx={{ borderRadius: "0px" }}
            >
              {open ? <ExpandLess /> : <ExpandMore />}
            </IconButton>
          </Box>
        </FormControl>
      </Box>
      <Popper open={open} anchorEl={anchorEl} placement="bottom-end" transition>
        {({ TransitionProps }) => (
          <Fade {...TransitionProps} timeout={300}>
            <Paper
              ref={popperRef}
              sx={{
                padding: "1rem",
                display: "flex",
                flexDirection: "column",
                backgroundColor: "white",
                borderRadius: "0px",
                borderWidth: "1px",
                borderColor: "lightgrey",
                boxShadow: "none",
                maxHeight: "20rem",
                width: popperWidth,
              }}
            >
              <div className="flex flex-row mt-2 ml-1 mr-1 space-between flex-wrap overflow-auto">
                {!isDataLoaded && <div>Loading...</div>}
                {isDataLoaded &&
                  filteredData.map((name, index) => {
                    return (
                      <KeyWordsTags
                        key={index}
                        name={name}
                        isSelected={cur_list.includes(name)}
                        keywordType={keywordType}
                      />
                    );
                  })}
              </div>
            </Paper>
          </Fade>
        )}
      </Popper>
    </React.Fragment>
  );
};
