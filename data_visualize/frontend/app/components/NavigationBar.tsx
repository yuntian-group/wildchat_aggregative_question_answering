import React, { FC } from "react";
import Link from "next/link";
import { Typography } from "@mui/material";

const linkStyle = {
  color: "white",
  fontFamily: "inherit",
  fontSize: "1.25rem",
  cursor: "pointer",
  paddingX: "0.5rem",
    paddingY: "0.5rem",
  height: "100%",
  borderRadius: "0",
  transition: "background-color 0.3s",
  "&:hover": {
    backgroundColor: "rgba(255, 255, 255, 0.2)",
  },
  "&:active": {
    backgroundColor: "rgba(255, 255, 255, 0.3)",
  },
};

const NavigationBar: FC = () => {
  return (
    <div
      className="w-full sticky"
      style={{ backgroundColor: "rgb(34, 51, 103)", height: "5%"}}
    >
      <div className="container w-full h-full">
        <div className="flex items-center h-full justify-start mx-4">
          <ul className="hidden md:flex gap-x-6 items-center text-white">
            <li>
              <div className="flex items-center">
                <img
                  src="/favicon.ico"
                  alt="WildChat Icon"
                  style={{
                    width: "2.5rem",
                    height: "2.5rem",
                    marginRight: "1.5rem",
                  }}
                />
                <Typography
                  sx={{
                    color: "white",
                    fontWeight: "bold",
                    fontFamily: "inherit",
                    fontSize: "1.5rem",
                  }}
                >
                  WildChat Visualize
                </Typography>
              </div>
            </li>
            <li>
              <Link href="/" passHref >
                <Typography sx={linkStyle}>
                  Explorer
                </Typography>
              </Link>
            </li>
            <li>
              <Link href="/dataview" passHref>
                <Typography sx={linkStyle}>
                  QA Data
                </Typography>
              </Link>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default NavigationBar;
