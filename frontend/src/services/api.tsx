import axios from "axios";

const baseURL = import.meta.env.VITE_API_BASE_URL || "/api";

function getCookie(name: string) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop()?.split(";").shift();
}

export const api = axios.create({
  baseURL: baseURL, // "http://localhost:5000"
});

export const auth_api = axios.create({
  baseURL: baseURL + "/auth", // "http://localhost:5000/auth"
  withCredentials: true,
});

export const game_api = axios.create({
  baseURL: baseURL + "/game", // "http://localhost:5000/game"
  withCredentials: true,
});

export const admin_api = axios.create({
  baseURL: baseURL + "/admin", //"http://localhost:5000/admin"
  withCredentials: true,
});

export const leaderboard_api = axios.create({
  baseURL: baseURL + "/leaderboard", //"http://localhost:5000/admin"
  withCredentials: true,
});

// Set interceptors to always inject fresh CSRF token
[api, auth_api, game_api, admin_api, leaderboard_api].forEach((api) => {
  api.interceptors.request.use((config) => {
    const token = getCookie("csrf_access_token");
    if (token) {
      config.headers["X-CSRF-TOKEN"] = token;
    }
    return config;
  });
});
