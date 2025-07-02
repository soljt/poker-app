import { createContext, useEffect, useMemo, useState } from "react";
import { User } from "../models/User";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import React from "react";
import { loginAPI, logoutAPI, registerAPI } from "../services/AuthService";
import { admin_api, auth_api, game_api } from "../services/api";

// type for context
type UserContextType = {
  user: User | null;
  token: string | null;
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
  const [token, setToken] = useState<string | null>(
    getCookie("csrf_access_token") || null
  );
  const [user, setUser] = useState<User | null>(
    localStorage.getItem("user")
      ? JSON.parse(localStorage.getItem("user") || "") // would throw an error if we tried to JSON.parse("")
      : null
  );
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
        // see if we have the credentials
        const token = getCookie("csrf_access_token") || null;
        auth_api.defaults.headers.common["X-CSRF-TOKEN"] = token;
        game_api.defaults.headers.common["X-CSRF-TOKEN"] = token;
        admin_api.defaults.headers.common["X-CSRF-TOKEN"] = token;
        const response = await auth_api.post("/who_am_i", {}); // can throw error
        localStorage.setItem("user", JSON.stringify(response.data.user));
        setUser(response.data.user);
        setToken(token);
      } catch {
        // should only catch 401 unauth
        setUser(null);
        localStorage.removeItem("user");
        localStorage.removeItem("game_id"); // do not let the user store a game if they fail to auth
        setToken(null);
      }
    };
    fetchMe();
    setIsReady(true);
  }, []);

  const contextValue = useMemo(() => {
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
        .then(async (res) => {
          if (res) {
            const token = getCookie("csrf_access_token");
            setToken(token ? token : null);
            auth_api.defaults.headers.common["X-CSRF-TOKEN"] = token;
            game_api.defaults.headers.common["X-CSRF-TOKEN"] = token;

            const res = await auth_api.post("/who_am_i", {});
            localStorage.setItem("user", JSON.stringify(res.data.user));
            setUser(res.data.user);
            toast.success(res.data.message);
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
        localStorage.removeItem("user");
        setToken(null);
        navigate("/");
      });
    };
    return {
      user,
      token,
      registerUser,
      loginUser,
      logout,
      isLoggedIn,
    };
  }, [user, token, navigate]);

  return (
    <UserContext.Provider value={contextValue}>
      {
        isReady ? (
          children
        ) : (
          <div>Loading...</div>
        ) /* necessary to deal with all the async/await - if it's ready, render the children */
      }
    </UserContext.Provider>
  );
};

export const useAuth = () => React.useContext(UserContext);
