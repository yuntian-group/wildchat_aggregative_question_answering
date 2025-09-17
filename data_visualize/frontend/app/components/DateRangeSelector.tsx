import * as React from "react";
import dayjs, { Dayjs } from "dayjs";
import { useState, useEffect } from "react";
import Fade from "@mui/material/Fade";
import { styled } from "@mui/material/styles";
import {
  TextField,
  Paper,
  FormControl,
  FormLabel,
  IconButton,
} from "@mui/material";
import Popper from "@mui/material/Popper";
import { PickersLayout } from "@mui/x-date-pickers/PickersLayout";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import { LocalizationProvider } from "@mui/x-date-pickers/LocalizationProvider";
import { DatePicker } from "@mui/x-date-pickers/DatePicker";
import ExpandLess from "@mui/icons-material/ExpandLess";
import ExpandMore from "@mui/icons-material/ExpandMore";
import { useAppSelector, useAppDispatch } from "@/lib/hooks";
import { updateDateRange } from "@/lib/features/date/dateSlice";

const StyledTextField = styled(TextField)({
  "& .MuiInputBase-root": {
    color: "black", // Text color
  },
  "& .MuiOutlinedInput-root": {
    borderRadius: "0",
    "& fieldset": {},
    "&:hover fieldset": {
      borderColor: "rgb(34, 51, 103)", // Border color when hovered
      color: "rgb(34, 51, 103)",
    },
    "&.Mui-focused fieldset": {
      borderColor: "rgb(34, 51, 103)", // Custom focus border color
      color: "rgb(34, 51, 103)",
    },
  },
});

const StyledPaper = styled(Paper)({
  color: "#1565c0",
  borderRadius: "0",
  borderWidth: "0",
  borderColor: "#2196f3",
  border: "0px solid",
  backgroundColor: "rgb(219 234 254)",
  boxShadow: "none",
});

const StyledPickersLayout = styled(PickersLayout)({
  ".MuiPickersDay-root": {
    borderRadius: "0",
    borderWidth: "0",
    fontFamily: "inherit",
  },
  ".MuiPickersYear-yearButton": {
    borderRadius: "0",
    borderWidth: "0",
    fontFamily: "inherit",
  },
});

interface CustomDatePickerProps {
  startDate: Dayjs | null;
  setStartDate: React.Dispatch<React.SetStateAction<Dayjs | null>>;
  endDate: Dayjs | null;
  setEndDate: React.Dispatch<React.SetStateAction<Dayjs | null>>;
}

function CustomDatePicker({
  startDate,
  setStartDate,
  endDate,
  setEndDate,
}: CustomDatePickerProps) {
  return (
    <LocalizationProvider dateAdapter={AdapterDayjs}>
      <DatePicker
        label="Start Date"
        sx={{ marginBottom: "5%" }}
        value={startDate}
        onChange={(newDate) => {
          setStartDate(newDate);
        }}
        slots={{
          textField: StyledTextField,
          desktopPaper: StyledPaper,
          layout: StyledPickersLayout,
        }}
      />
      <DatePicker
        label="End Date"
        value={endDate}
        onChange={(newDate) => {
          setEndDate(newDate);
        }}
        slots={{
          textField: StyledTextField,
          desktopPaper: StyledPaper,
          layout: StyledPickersLayout,
        }}
      />
    </LocalizationProvider>
  );
}

interface DateRangeSelectorProps {
  width: string;
}

export const DateRangeSelector: React.FC<DateRangeSelectorProps> = ({
  width,
}) => {
  const { start_date, end_date } = useAppSelector((state) => state.dateRange);
  const [anchorEl, setAnchorEl] = React.useState<HTMLButtonElement | null>(
    null
  );
  const [open, setOpen] = React.useState(false);

  const dateInputRef = React.useRef<HTMLInputElement>(null);
  const popperRef = React.useRef<HTMLDivElement>(null);

  const [startDate, setStartDate] = useState<Dayjs | null>(dayjs(start_date));
  const [endDate, setEndDate] = useState<Dayjs | null>(dayjs(end_date));
  const dispatch = useAppDispatch();

  const handleInputFocus = () => {
    if (open) {
      return;
    }
    if (!dateInputRef.current) {
      return;
    }
    setAnchorEl(dateInputRef.current);
    setOpen(true);
  };

  const handleClick = () => {
    if (!dateInputRef.current) {
      return;
    }
    setAnchorEl(dateInputRef.current);
    setOpen((prev) => !prev);
  };

  const id = open ? "simple-popper" : undefined;
  const [buttonWidth, setButtonWidth] = useState(0);

  // Measure button's width when it changes or on mount
  useEffect(() => {
    if (dateInputRef.current) {
      setButtonWidth(dateInputRef.current.offsetWidth);
    }

    // Optionally, recalculate on window resize
    const handleResize = () => {
      if (dateInputRef.current) {
        setButtonWidth(dateInputRef.current.offsetWidth);
      }
    };

    window.addEventListener("resize", handleResize);

    // Cleanup on unmount
    return () => {
      window.removeEventListener("resize", handleResize);
    };
  }, [open]); // Recalculate width if the popper state changes


  const handleClickOutside = (event: MouseEvent) => {

    const target = event.target as Node;
    const isDatePickerElement = !!(
      target instanceof Element && 
      target.closest('.MuiPickersPopper-root, .MuiPaper-root')
    );

    if (!dateInputRef.current?.contains(target) &&
      !popperRef.current?.contains(target) &&
      !isDatePickerElement
    ) {
      setOpen(false); // Close popper when clicked outside
    }
  };

  useEffect(() => {
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  return (
    <React.Fragment>
      <FormControl
        ref={dateInputRef}
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
          Date Range
        </FormLabel>
        <div
          className="align-middle flex-grow text-center font-inherit lg:text-lg md:text-sm sm:text-xs xs:text-xs"
          style={{
            color: "rgb(34, 51, 103)",
            fontWeight: "bold",
          }}
        >
          {startDate?.format("YYYY/MM/DD") +
            " - " +
            endDate?.format("YYYY/MM/DD")}
        </div>
        <IconButton
          aria-describedby={id}
          type="button"
          onClick={handleClick}
          className="font-bold"
          sx={{ borderRadius: "0px", height: "50%" }}
        >
          {open ? <ExpandLess /> : <ExpandMore />}
        </IconButton>
      </FormControl>
      <Popper
        open={open}
        anchorEl={anchorEl}
        placement="bottom-start"
        transition
        sx={{ width: buttonWidth }}
      >
        {({ TransitionProps }) => (
          <Fade {...TransitionProps} timeout={300}>
            <Paper
              ref={popperRef}
              sx={{
                padding: "1em",
                display: "flex",
                flexDirection: "column",
                backgroundColor: "white",
                borderRadius: "0px",
                borderWidth: "1px",
                borderColor: "lightgrey",
                boxShadow: "none",
              }}
            >
              <CustomDatePicker
                startDate={startDate}
                setStartDate={setStartDate}
                endDate={endDate}
                setEndDate={setEndDate}
              />
              <button
                onClick={() => {
                  setOpen(false);
                  dispatch(
                    updateDateRange({
                      start_date: startDate
                        ? startDate.format("YYYY-MM-DD")
                        : "",
                      end_date: endDate ? endDate.format("YYYY-MM-DD") : "",
                    })
                  );
                }}
                className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 h-max mt-4"
              >
                Done
              </button>
            </Paper>
          </Fade>
        )}
      </Popper>
    </React.Fragment>
  );
};
