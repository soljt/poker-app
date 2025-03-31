import { createContext, useEffect, useState } from "react";
import { User } from "../models/User";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import React from "react";
import { loginAPI, logoutAPI, registerAPI } from "../services/AuthService";
import { auth_api } from "../services/api";

// type for context
type UserContextType = {
  user: User | null;
  registerUser: (username: string, password: string) => void;
  loginUser: (username: string, password: string) => void;
  logout: () => void;
  isLoggedIn: () => boolean;
};

// required by ts
type Props = { children: React.ReactNode };

// required by ts
const UserContext = createContext<UserContextType>({} as UserContextType);

// provider called once and then forgotten
export const UserProvider = ({ children }: Props) => {
  const navigate = useNavigate();
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [isReady, setIsReady] = useState(false);

  function getCookie(name: string) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop()?.split(";").shift();
  }

  // on load, try to fetch user info from server
  useEffect(() => {
    const fetchMe = async () => {
      try {
        const response = await auth_api.post("/who_am_i", {});
        const token = getCookie("csrf_access_token");
        if (token) {
          setToken(token);
          auth_api.defaults.headers.common["X-CSRF-TOKEN"] = token;
        }
        const user = response.data.user; // user is a JSON object
        setUser(user);
      } catch {
        setUser(null);
        setToken(null);
        // toast.error("Could not get user, from: ");
      }
    };
    fetchMe();
    setIsReady(true);
  }, [token]);

  // register a new user
  const registerUser = async (username: string, password: string) => {
    await registerAPI(username, password)
      .then((res) => {
        if (res) {
          toast.success(res.data.message);
          navigate("/login");
        }
      })
      .catch((e) => toast.warning("Server error occurred", e));
  };

  // login the user
  const loginUser = async (username: string, password: string) => {
    await loginAPI(username, password)
      .then((res) => {
        if (res) {
          console.log(res.data);
          const token = getCookie("csrf_access_token");
          setToken(token ? token : null);
          auth_api.defaults.headers.common["X-CSRF-TOKEN"] = token;
          toast.success(res.data.message);
          navigate("/");
        }
      })
      .catch((e) => toast.warning("Server error occurred", e));
  };

  const isLoggedIn = () => {
    return !!user;
  };

  const logout = async () => {
    await logoutAPI().then((res) => {
      toast.success(res?.data.message);
      setUser(null);
      setToken(null);
      navigate("/");
    });
  };

  return (
    <UserContext.Provider
      value={{ user, registerUser, loginUser, logout, isLoggedIn }}
    >
      {
        isReady ? (
          children
        ) : (
          <div>Loading...</div>
        ) /* necessary to deal with all the async/await - if it has children, it's ready */
      }
    </UserContext.Provider>
  );
};

export const useAuth = () => React.useContext(UserContext);
