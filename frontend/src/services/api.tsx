import axios from "axios";

export const api = axios.create({
  baseURL: "http://localhost:5000",
});

export const auth_api = axios.create({
  baseURL: "http://localhost:5000/auth",
  withCredentials: true,
});
