import axios from "axios";

export const api = axios.create({
  baseURL: "http://localhost:5000",
});

export const auth_api = axios.create({
  baseURL: "http://localhost:5000/auth",
  withCredentials: true,
});

export const game_api = axios.create({
  baseURL: "http://localhost:5000/game",
  withCredentials: true,
});

export const admin_api = axios.create({
  baseURL: "http://localhost:5000/admin",
  withCredentials: true,
});
