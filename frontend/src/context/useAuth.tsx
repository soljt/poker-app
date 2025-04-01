import { createContext, useLayoutEffect, useRef, useState } from "react";
import { User } from "../models/User";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import React from "react";
import { loginAPI, logoutAPI, registerAPI } from "../services/AuthService";
import { auth_api } from "../services/api";
import { createSocket } from "../socket";
import { Socket } from "socket.io-client";

// type for context
type UserContextType = {
  user: User | null;
  token: string | null;
  socket: Socket | null;
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
  const socket = useRef<Socket | null>(null);
  const [isReady, setIsReady] = useState(false);

  function getCookie(name: string) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop()?.split(";").shift();
  }

  // on load, try to fetch user info from server
  useLayoutEffect(() => {
    const fetchMe = async () => {
      try {
        // see if we have the credentials
        const token = getCookie("csrf_access_token");
        auth_api.defaults.headers.common["X-CSRF-TOKEN"] = token;
        const response = await auth_api.post("/who_am_i", {}); // can throw error
        localStorage.setItem("user", JSON.stringify(response.data.user));
        setUser(response.data.user);
        // const user = response.data.user; // user is a JSON object
        // setUser(user);

        // // backend response may have set a new cookie
        // const newToken = getCookie("csrf_access_token");
        // if (newToken && newToken !== token) {
        //   setToken(newToken);
        //   auth_api.defaults.headers.common["X-CSRF-TOKEN"] = newToken;
        // }

        // logged in user needs a socket connection
        if (!socket.current) {
          socket.current = createSocket();
        }
        return true;
      } catch {
        setUser(null);
        localStorage.setItem("user", "");
        setToken(null);
        socket.current?.disconnect();
        socket.current = null;
        return false;
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
          socket.current = createSocket();
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
      localStorage.setItem("user", "");
      setToken(null);
      socket.current?.disconnect();
      socket.current = null;
      navigate("/");
    });
  };

  return (
    <UserContext.Provider
      value={{
        user,
        token,
        socket: socket.current,
        registerUser,
        loginUser,
        logout,
        isLoggedIn,
      }}
    >
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
