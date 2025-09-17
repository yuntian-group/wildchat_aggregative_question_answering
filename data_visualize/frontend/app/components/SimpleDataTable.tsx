import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import { useEffect, useState } from "react";
import { Box, Pagination, SxProps, Theme} from "@mui/material";
import styled from "@mui/material/styles/styled";

interface SimpleDataTableProps {
  columnNames: string[];
  data: Record<string, string | number>[];
  percentage: number[];
  title?: string;
  sx?: SxProps<Theme>;
  rowsPerPage?: number;
}

const StyledTableCell = styled(TableCell)(() => ({
  padding: "0.25rem",
  color: "rgb(34, 51, 103)",
  whiteSpace: "nowrap",
}));

const StyledTableTitleCell = styled(TableCell)(() => ({
  padding: "0.25rem",
  color: "black",
  fontWeight: "bold",
  textAlign: "left",
  whiteSpace: "nowrap",
}));

export const SimpleDataTable: React.FC<SimpleDataTableProps> = ({
  columnNames,
  data,
  percentage,
  title,
  sx,
  rowsPerPage = 13,
}) => {
  const [isMounted, setIsMounted] = useState(false);
  const [page, setPage] = useState(0);

  useEffect(() => {
    setIsMounted(true);
    return () => {
      setIsMounted(false);
    };
  }, []);

  const handleChangePage = (_event: unknown, newPage: number) => {
    setPage(newPage - 1);
  };

  const pageData = data.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage);

  return (
    <Box sx={sx}>
      {/* {title && (
        <Typography variant="h6" sx={{ textAlign: "left", color: "rgba(0, 0, 0, 0.6)", fontWeight: "bold", }}>
          {title}
        </Typography>
      )} */}
      <TableContainer component={Box}>
        <Table>
          <TableHead>
            <TableRow>
              {columnNames.map((columnName) => (
                <StyledTableTitleCell key={columnName}>
                  {columnName.toUpperCase()}
                </StyledTableTitleCell>
              ))}
              <StyledTableTitleCell>PERCENTAGE</StyledTableTitleCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {pageData.map((row, index) => (
              <TableRow key={index}>
                {columnNames.map((columnName) => (
                  <StyledTableCell key={`${index}.${columnName}`}>
                    {row[columnName]}
                  </StyledTableCell>
                ))}
                <StyledTableCell sx={{ position: "relative" }}>
                  <div
                    style={{
                      left: 0,
                      top: 0,
                      bottom: 0,
                      transition: "width 0.3s ease",
                      backgroundColor:
                        percentage[index + page * rowsPerPage] > 90
                          ? "rgb(34, 51, 103)"
                          : percentage[index + page * rowsPerPage] > 75
                          ? "rgb(0, 82, 204)"
                          : percentage[index + page * rowsPerPage] > 50
                          ? "rgb(0, 120, 254)"
                          : percentage[index + page * rowsPerPage] > 25
                          ? "rgb(135, 206, 250)"
                          : "lightgrey",
                      maxWidth: "100%",
                      height: "100%",
                      color:
                        percentage[index + page * rowsPerPage] > 25
                          ? "white"
                          : "black",
                      fontWeight: "bolder",
                      textAlign: "center",
                      width: isMounted
                        ? `${percentage[index + page * rowsPerPage]}%`
                        : "0%",
                    }}
                  >
                    {percentage[index + page * rowsPerPage].toFixed(2)}%
                  </div>
                </StyledTableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
        {data.length > rowsPerPage && (
          <Box sx={{ display: "flex", justifyContent: "center", mt: 1 }}>
            <Pagination
              count={Math.ceil(data.length / rowsPerPage)}
              page={page + 1}
              onChange={handleChangePage}
              shape="rounded"
            />
          </Box>
        )}
      </TableContainer>
    </Box>
  );
};
