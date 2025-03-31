import React, { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/useAuth";
import { toast } from "react-toastify";

type Props = { children: React.ReactNode };

const ProtectedRoute = ({ children }: Props) => {
  const navigate = useNavigate();
  const { isLoggedIn } = useAuth();

  useEffect(() => {
    if (!isLoggedIn()) {
      toast.warning("Must be logged in to access this page");
      navigate("/login");
    }
  }, [isLoggedIn, navigate]);

  return <>{children}</>;
};

export default ProtectedRoute;
