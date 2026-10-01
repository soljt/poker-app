import {
  createContext,
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";
import { User } from "../models/User";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import React from "react";
import {
  demoLoginAPI,
  loginAPI,
  logoutAPI,
  registerAPI,
} from "../services/AuthService";
import { getTurnstileToken } from "../services/turnstile";
import {
  admin_api,
  auth_api,
  game_api,
  leaderboard_api,
} from "../services/api";
import { useLocation } from "react-router-dom";

// type for context
type UserContextType = {
  user: User | null;
  token: string | null;
  registerUser: (username: string, password: string) => void;
  loginUser: (username: string, password: string) => void;
  loginDemoUser: () => Promise<void>;
  logout: () => void;
  isLoggedIn: () => boolean;
  refreshUser: () => void;
};

// required by ts
type Props = { children: React.ReactNode };

// required by ts
const UserContext = createContext<UserContextType>({} as UserContextType);

// provider called once and then forgotten
export const UserProvider = ({ children }: Props) => {
  const navigate = useNavigate();
  const location = useLocation();
  const [token, setToken] = useState<string | null>(
    getCookie("csrf_access_token") || null
  );
  const [user, setUser] = useState<User | null>(null);
  // localStorage.getItem("user")
  // ? JSON.parse(localStorage.getItem("user") || "") // would throw an error if we tried to JSON.parse("")
  // :
  const [isReady, setIsReady] = useState(false);

  function getCookie(name: string) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop()?.split(";").shift();
  }

  const fetchMe = useCallback(async () => {
    try {
      // see if we have the credentials
      const token = getCookie("csrf_access_token") || null;
      auth_api.defaults.headers.common["X-CSRF-TOKEN"] = token;
      game_api.defaults.headers.common["X-CSRF-TOKEN"] = token;
      admin_api.defaults.headers.common["X-CSRF-TOKEN"] = token;
      leaderboard_api.defaults.headers.common["X-CSRF-TOKEN"] = token;
      const response = await auth_api.post("/who_am_i", {}); // can throw error
      // localStorage.setItem("user", JSON.stringify(response.data.user));
      setUser(response.data.user);
      setToken(token);
    } catch {
      // should only catch 401 unauth
      setUser(null);
      // localStorage.removeItem("user");
      localStorage.removeItem("game_id"); // do not let the user store a game if they fail to auth
      setToken(null);
    }
  }, []);
  // on load, try to fetch user info from server
  useEffect(() => {
    fetchMe();
    setIsReady(true);
  }, [location, fetchMe]);

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

    const refreshUser = () => {
      fetchMe();
    };

    // once the backend has set the cookies, pick up the csrf token and fetch the user
    const finishLogin = async () => {
      const token = getCookie("csrf_access_token");
      setToken(token ? token : null);
      auth_api.defaults.headers.common["X-CSRF-TOKEN"] = token;
      game_api.defaults.headers.common["X-CSRF-TOKEN"] = token;

      const res = await auth_api.post("/who_am_i", {});
      // localStorage.setItem("user", JSON.stringify(res.data.user));
      setUser(res.data.user);
      toast.success(res.data.message);
    };

    // login the user
    const loginUser = async (username: string, password: string) => {
      await loginAPI(username, password)
        .then(async (res) => {
          if (res) {
            await finishLogin();
          }
        })
        .catch((e) => toast.warning("Server error occurred", e));
    };

    // grab a free demo account
    const loginDemoUser = async () => {
      try {
        const turnstileToken = await getTurnstileToken();
        const res = await demoLoginAPI(turnstileToken);
        if (res) {
          await finishLogin();
          toast.success(res.data.message);
        }
      } catch {
        toast.warning("Couldn't start a demo session - try again");
      }
    };

    const isLoggedIn = () => {
      return !!user;
    };

    const logout = async () => {
      await logoutAPI().then((res) => {
        toast.success(res?.data.message);
        setUser(null);
        // localStorage.removeItem("user");
        setToken(null);
        navigate("/");
      });
    };
    return {
      user,
      token,
      registerUser,
      loginUser,
      loginDemoUser,
      logout,
      isLoggedIn,
      refreshUser,
    };
  }, [user, token, navigate, fetchMe]);

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
