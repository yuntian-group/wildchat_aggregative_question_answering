import * as React from "react";
import { useState, useEffect } from "react";
import { styled } from "@mui/material/styles";
import { RootState } from "@/lib/store";
import { useAppSelector } from "@/lib/hooks";
import { SimpleDataTable } from "./SimpleDataTable";
import { Box, Typography, Paper } from "@mui/material";
import { PureComponent } from "react";
import Grid from "@mui/material/Grid2";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

export interface DataResultStatisticsProps {
  numRecordPerTable?: number;
}

export const DataResultStatistics: React.FC<DataResultStatisticsProps> = ({
  numRecordPerTable = 10,
}) => {
  const dialogueData = useAppSelector(
    (state: RootState) => state.dialogueDataFetch.data
  );
  const dialogueDataStatus = useAppSelector(
    (state: RootState) => state.dialogueDataFetch.status
  );

  const topicToTaxonomyMap = useAppSelector(
    (state: RootState) => state.topic.all_topics
  );

  const getPercentageList = (
    data: Record<string, string | number>[],
    fieldName: string
  ) => {
    return data.map((entry: any) => entry[fieldName]);
  };

  const levelZeroStatistics = dialogueData["label_stats_level_0"];
  //   const levelOneStatistics = dialogueData["label_stats_level_1"];

  const isDataLoaded = dialogueDataStatus === "idle";

  if (dialogueDataStatus === "initial") {
    return <div>INIT</div>;
  }

  if (!isDataLoaded || dialogueData === undefined || dialogueData.size === 0) {
    return <div>loading...</div>;
  }
  // translate topic ids to topic names
  const levelZeroStatisticsTranslated = levelZeroStatistics.map(
    (entry: any) => {
      return {
        ...entry,
        topic: topicToTaxonomyMap[entry.topic_id].class_name,
      };
    }
  );

  const languageStatistics = dialogueData["language_stats"];
  const countryStatistics = dialogueData["country_stats"];
  const userStatistics = dialogueData["user_stats"];
  const keywordStatistics = dialogueData["keyword_stats"];
  const keywordAggregatedStatistics = dialogueData["keyword_aggregated_stats"];
  const timeStatistics = dialogueData["time_stats"];
  const dialogueCount = dialogueData["dialogue_count"];
  const tokenCount = dialogueData["token_count"];

  const mainBackgroundColor = "#f0f4f8";
  const gridBackgroundColor = "#fff";

  return (
    <Box sx={{ flexGrow: 1, backgroundColor: mainBackgroundColor }}>
      <Grid
        container
        spacing={1}
        alignItems="stretch"
        sx={{
          // This applies a max height to each row
          margin: "1rem",
          "& > .MuiGrid2-root": {
            display: "flex",
            flexDirection: "column",
            overflow: "auto",
          },
        }}
      >
        <Grid
          size={4}
          container 
          spacing={1}
          sx={{
            display: "flex",
            flexDirection: "column",
            flexGrow: 1,
            backgroundColor: mainBackgroundColor,
          }}
        >
          <Grid
            size={12}
            sx={{
              display: "flex",
              flexDirection: "row",
              flexGrow: 1,
              justifyContent: "space-around",
              alignItems: "center",
              backgroundColor: gridBackgroundColor,
            }}
          >
            <Box sx={{ textAlign: "center" }}>
              <Typography variant="h6" fontWeight="bold" gutterBottom>
                Dialogue Count
              </Typography>
              <Typography variant="h4" color="primary" fontWeight="bold">
                {dialogueCount}
              </Typography>
            </Box>
            <Box sx={{ textAlign: "center" }}>
              <Typography variant="h6" fontWeight="bold" gutterBottom>
                Token Count
              </Typography>
              <Typography variant="h4" color="primary" fontWeight="bold">
                {tokenCount}
              </Typography>
            </Box>
          </Grid>
          <Grid
            size={12}
            sx={{
              flex: "1",
              flexGrow: 1,
              backgroundColor: gridBackgroundColor,
              maxHeight: "20rem",
              width: "100%",
            }}
          >
            <Typography
              variant="h6"
              align="center"
              color="back"
              fontWeight="bold"
              gutterBottom
              sx={{ height: "15%", paddingTop: "1rem" }}
            >
              Distribution Over Time
            </Typography>
            <ResponsiveContainer width="100%" height="80%">
              <LineChart data={timeStatistics}
              margin={{ top: 5, right: 40,  bottom: 5 }}>
            
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  dataKey="date"
                  fontFamily="inherit"
                  tick={{ fontSize: "0.625rem" }}
                />
                <YAxis tick={{ fontSize: "0.625rem"  }} />
                <Tooltip />
                <Line
                  type="monotone"
                  dataKey="count"
                  stroke="rgb(0, 120, 254)"
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </Grid>
        </Grid>

        <Grid size={4}>
          <SimpleDataTable
            sx={{
              flex: "1",
              minWidth: "10%",
              backgroundColor: gridBackgroundColor,
              padding: "0.5rem",
              boxSizing: "border-box",
            }}
            title="Topic Statistics"
            data={levelZeroStatisticsTranslated}
            columnNames={["topic", "count"]}
            percentage={getPercentageList(levelZeroStatistics, "percentage")}
            rowsPerPage={numRecordPerTable}
          />
        </Grid>
        <Grid size={4}>
          <SimpleDataTable
            sx={{
              flex: "1",
              minWidth: "10%",
              backgroundColor: gridBackgroundColor,
              padding: "0.5rem",
              boxSizing: "border-box",
            }}
            title="Country / Region Statistics"
            data={countryStatistics}
            columnNames={["country/reigon", "count"]}
            percentage={getPercentageList(countryStatistics, "percentage")}
            rowsPerPage={numRecordPerTable}
          />
        </Grid>
        <Grid size={4}>
          <SimpleDataTable
            sx={{
              flex: "1",
              backgroundColor: gridBackgroundColor,
              padding: "0.5rem",
              boxSizing: "border-box",
            }}
            title="Language Statistics"
            data={languageStatistics}
            columnNames={["language", "count"]}
            percentage={getPercentageList(languageStatistics, "percentage")}
            rowsPerPage={numRecordPerTable}
          />
        </Grid>
        <Grid size={4}>
          <SimpleDataTable
            sx={{
              flex: "1",
              backgroundColor: gridBackgroundColor,
              padding: "0.5rem",
              boxSizing: "border-box",
            }}
            title="User Statistics"
            data={userStatistics}
            columnNames={["user_name", "count"]}
            percentage={getPercentageList(userStatistics, "percentage")}
            rowsPerPage={numRecordPerTable}
          />
        </Grid>
        <Grid size={4}>
          <SimpleDataTable
            sx={{
              flex: "1",
              backgroundColor: gridBackgroundColor,
              padding: "0.5rem",
              boxSizing: "border-box",
            }}
            title="Aggregated Keyword Statistics"
            data={keywordAggregatedStatistics}
            columnNames={["keyword_aggregated", "count"]}
            percentage={getPercentageList(keywordAggregatedStatistics, "percentage")}
            rowsPerPage={numRecordPerTable}
          />
        </Grid>
        <Grid size={4}>
          <SimpleDataTable
            sx={{
              flex: "1",
              backgroundColor: gridBackgroundColor,
              padding: "0.5rem",
              boxSizing: "border-box",
            }}
            title="Keyword Statistics"
            data={keywordStatistics}
            columnNames={["keyword", "count"]}
            percentage={getPercentageList(keywordStatistics, "percentage")}
            rowsPerPage={numRecordPerTable}
          />
        </Grid>
      </Grid>
    </Box>
  );
};
