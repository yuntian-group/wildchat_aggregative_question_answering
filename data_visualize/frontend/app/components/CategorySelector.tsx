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
  Button,
} from "@mui/material";
import Popper from "@mui/material/Popper";
import ExpandLess from "@mui/icons-material/ExpandLess";
import ExpandMore from "@mui/icons-material/ExpandMore";
import SearchIcon from "@mui/icons-material/Search";
import CloseIcon from "@mui/icons-material/Close";
import { useAppDispatch, useAppSelector } from "@/lib/hooks";
import {
  selectCategory,
  deselectCategory,
  selectedCategory,
  LANGUAGE_NAME,
  COUNTRY_NAME,
  USER_NAME,
} from "@/lib/features/category/categorySlice";
import debounce from "lodash.debounce";
import { fetchUserData } from "@/lib/features/userDataFetch/userDataFetchSlice";

const StyledTextField = styled(TextField)({
  "& .MuiInputBase-root": {
    color: "black", // Text color
    margin: "0 0 0 0.25rem",
  },

  "& .MuiOutlinedInput-root": {
    borderRadius: "0",
    "& fieldset": {
      borderWidth: "0 0 1px 0",
      borderColor: "lightgrey",
    },
    "&:hover fieldset": {
      borderWidth: "0 0 1px 0",
      borderColor: "rgb(34, 51, 103)", // Border color when hovered
      color: "rgb(34, 51, 103)",
    },
    "&.Mui-focused fieldset": {
      borderWidth: "0 0 1px 0",
      borderColor: "rgb(34, 51, 103)", // Custom focus border color
      color: "rgb(34, 51, 103)",
    },
    "& .MuiInputBase-input": {
      padding: "0 0 0  0.125rem",
      margin: "0 0 0 0",
      fontSize: "1.0rem",
    },
  },
});

const StyledTagButton = styled(Button)({
  "&.MuiButton-root": {
    border: "0.15rem solid",
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

interface TagsProps {
  categoryTypeName: string;
  name: string;
  isSelected: boolean;
}

const Tags: React.FC<TagsProps> = ({ categoryTypeName, name, isSelected }) => {
  const dispatch = useAppDispatch();
  return (
    <StyledTagButton
      sx={{
        backgroundColor: isSelected ? "rgb(34, 51, 103)" : "white",
        color: isSelected ? "white" : "rgb(34, 51, 103)",
      }}
      onClick={() => {
        if (isSelected) {
          dispatch(
            deselectCategory({ category: categoryTypeName, value: [name] })
          );
        } else {
          dispatch(
            selectCategory({ category: categoryTypeName, value: [name] })
          );
        }
      }}
    >
      {name}
    </StyledTagButton>
  );
};

interface CategorySelectorProps {
  width: string;
  name: string;
  data: Array<string>;
  isDataLoaded: boolean;
}

export const CategorySelector: React.FC<CategorySelectorProps> = ({
  width,
  name,
  data,
  isDataLoaded,
}) => {
  const { selected_language, selected_country, selected_user, selected_keywords } = useAppSelector(
    (state: RootState) => selectedCategory(state)
  );

  const categoryMap: { [key: string]: string[] } = {
    [LANGUAGE_NAME]: selected_language,
    [COUNTRY_NAME]: selected_country,
    [USER_NAME]: selected_user,
  };
  const selected = categoryMap[name];
  const [anchorEl, setAnchorEl] = React.useState<HTMLButtonElement | null>(
    null
  );
  const [open, setOpen] = React.useState(false);

  const [searchText, setSearchText] = React.useState<string>("");
  const [filteredData, setFilteredData] = React.useState<Array<string>>(data);
  const [mouseOnHover, setMouseOnHover] = React.useState(false);

  const formControlRef = React.useRef<HTMLInputElement>(null);
  const popperRef = React.useRef<HTMLDivElement>(null);
  const dispatch = useAppDispatch();

  const clearAllSelected = () => {
    dispatch(deselectCategory({ category: name, value: selected }));
  }

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

  const id = open ? `category-selector-${name}` : undefined;
  const cancel_id = `cancel-category-selectoy-cancel-${name}`;

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

  const maxSearchTextLength = 30;
  const allowedCharacters = /^[a-zA-Z0-9\-]*$/;
  const debouncedDelay = 200;

  const handleSearch = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchText(event.target.value);
    if (event.target.value === "") {
      setFilteredData(data);
    } else {
      const filtered = data.filter((name) =>
        name.toLowerCase().includes(searchText.toLowerCase())
      );
      setFilteredData(filtered);
    }
  };

  const debouncedAsyncSearch = useMemo(() => {
    return debounce((searchText: string) => {
      dispatch(fetchUserData(searchText));
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
    if (allowedCharacters.test(curSearchText)) {
      setSearchText(curSearchText);
      debouncedAsyncSearch(curSearchText);
    }
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

  const [buttonWidth, setButtonWidth] = useState(0);

  // Measure button's width when it changes or on mount
  useEffect(() => {
    if (formControlRef.current) {
      setButtonWidth(formControlRef.current.offsetWidth);
    }

    // Optionally, recalculate on window resize
    const handleResize = () => {
      if (formControlRef.current) {
        setButtonWidth(formControlRef.current.offsetWidth);
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
      <FormControl
        ref={formControlRef}
        sx={{
          width: width,
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
          {name}
          {` (${selected.length})`}
        </FormLabel>
        <div
          className="flex flex-row flex-wrap overflow-y-auto flex-begin overflow-x-hidden"
          style={{ height: "80%", maxHeight: "80%", width: "85%", maxWidth: "85%" }}
        >
          {selected.map((categoryName, categoryIndex) => (
            <Tags
              categoryTypeName={name}
              key={categoryIndex}
              name={categoryName}
              isSelected={true}
            />
          ))}
        </div>
        {selected.length > 0 && mouseOnHover && (
          <IconButton
            aria-describedby={cancel_id}
            type="button"
            sx={{ borderRadius: "0px", height: "50%", width: "7.5%" }}
            onClick={clearAllSelected}
          >
            <CloseIcon sx={{fontSize: "1rem", color: "lightgrey"}}/>
          </IconButton>
        )}
        <IconButton
          aria-describedby={id}
          type="button"
          onClick={handleClick}
          sx={{ borderRadius: "0px", height: "50%" , width: "7.5%"}}
        >
          {open ? <ExpandLess /> : <ExpandMore />}
        </IconButton>
        
      </FormControl>
      
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
                width: buttonWidth,
              }}
            >
              <div className="flex flex-row" style={{ alignItems: "flex-end" }}>
                <SearchIcon
                  sx={{ transform: "scaleX(-1)", color: "lightgrey" }}
                />
                <StyledTextField
                  sx={{ width: "100%" }}
                  slotProps={{ 
                    htmlInput: { 
                      maxLength: maxSearchTextLength, 
                    } 
                  }} 
                  onChange={
                    name === USER_NAME ? handleAsyncRequestSearch : handleSearch
                  }
                  value={searchText}
                />
              </div>
              <div className="flex flex-row mt-2 ml-1 mr-1 space-between flex-wrap overflow-auto">
                {!isDataLoaded? (
                  <div>Loading...</div>
                ) : (
                  filteredData.map((categoryName, categoryIndex) => (
                    <Tags
                      categoryTypeName={name}
                      key={categoryIndex}
                      name={categoryName}
                      isSelected={selected.includes(categoryName)}
                    />
                  ))
                )}
              </div>
            </Paper>
          </Fade>
        )}
      </Popper>
    </React.Fragment>
  );
};
