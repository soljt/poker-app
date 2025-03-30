import { createContext, useEffect, useState } from "react";
import { User } from "../models/User";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import React from "react";
import { loginAPI, logoutAPI, registerAPI } from "../services/AuthService";
import axios from "axios";
// import api from "../services/api";
const api = "http://localhost:5000";

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
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [isReady, setIsReady] = useState(false);

  //   function getCookie(name: string) {
  //     const value = `; ${document.cookie}`;
  //     const parts = value.split(`; ${name}=`);
  //     if (parts.length === 2) return parts.pop()?.split(";").shift();
  //   }

  console.log(document.cookie);

  // on load, try to fetch user info from server
  useEffect(() => {
    const fetchMe = async () => {
      try {
        if (token) {
          setToken(token);
          axios.defaults.headers.common["X-CSRF-TOKEN"] = token;
        }
        console.log("token:", token);

        const response = await axios.post(
          api + "/who_am_i",
          {},
          { withCredentials: true }
        );
        const user = response.data.user; // user is a JSON object
        setUser(user);
        setIsReady(true);
      } catch (e) {
        console.log(e);
        setUser(null);
        setToken(null);
        toast.error("Must be logged in");
        // navigate("/login");
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
          localStorage.setItem("token", res?.data.token);
          const userObj = {
            username: res?.data.username,
            chips: res?.data.chips,
          };
          localStorage.setItem("user", JSON.stringify(userObj));
          setToken(res?.data.token);
          setUser(userObj);
          toast.success("Register success");
          navigate("/");
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
          const token = res.data?.token;
          setToken(token);
          console.log("token before: ", token);
          axios.defaults.headers.common["X-CSRF-TOKEN"] = token;
          console.log(axios.defaults.headers.common["X-CSRF-TOKEN"]);
          //   localStorage.setItem("token", res?.data.token);
          //   const userObj = {
          //     username: res?.data.username,
          //     chips: res?.data.chips,
          //   };
          //   localStorage.setItem("user", JSON.stringify(userObj));
          //   setToken(res?.data.token);
          //   setUser(userObj);
          toast.success("Login success");
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
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      setUser(null);
      setToken("");
      navigate("/");
    });
  };

  return (
    <UserContext.Provider
      value={{ user, token, registerUser, loginUser, logout, isLoggedIn }}
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
