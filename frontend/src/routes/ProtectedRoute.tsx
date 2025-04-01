import React, { useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/useAuth";
import { toast } from "react-toastify";

type Props = { children: React.ReactNode };

const ProtectedRoute = ({ children }: Props) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { isLoggedIn } = useAuth();

  useEffect(() => {
    if (!isLoggedIn()) {
      toast.warning("Must be logged in to access this page");
      navigate("/login", { state: { from: location } });
    }
  }, [isLoggedIn, location, navigate]);

  return <>{isLoggedIn() && children}</>; // necessary to prevent page contents rendering
};

export default ProtectedRoute;
