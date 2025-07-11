import React from "react";
import { useLocation } from "react-router-dom";
import { useAuth } from "../context/useAuth"; // adjust path as needed

const BackgroundDecider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const location = useLocation();
  const { user } = useAuth();

  const isHer = user?.username === "kenna";
  const isSpecialLanding = location.pathname === "/";

  let backgroundClass = "";

  if (isHer) {
    if (isSpecialLanding) {
      backgroundClass = "big-handmade-hearts-bg";
    } else {
      backgroundClass = "pale-hearts-bg";
    }
  } else {
    backgroundClass = "";
  }

  return <div className={backgroundClass}>{children}</div>;
};

export default BackgroundDecider;
