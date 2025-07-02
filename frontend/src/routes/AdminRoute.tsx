import React, { useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/useAuth";
import { toast } from "react-toastify";
import { Roles } from "../types";

type Props = { children: React.ReactNode };

const ProtectedRoute = ({ children }: Props) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { isLoggedIn, user } = useAuth();

  useEffect(() => {
    if (!isLoggedIn()) {
      toast.warning("Must be logged in to access this page");
      navigate("/login", { state: { from: location } });
    } else if (!(user?.role === Roles.admin)) {
      toast.warning(
        "That page was for administrators ONLY! How did you even get there?"
      );
      navigate("/");
    }
  }, [isLoggedIn, location, navigate, user?.role]);

  return <>{isLoggedIn() && children}</>; // necessary to prevent page contents rendering
};

export default ProtectedRoute;
