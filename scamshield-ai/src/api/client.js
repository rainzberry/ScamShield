import axios from "axios";
import { getToken } from "../utils/storage";
import { getErrorMessage } from "../utils/errors";

export const UNAUTHORIZED_EVENT = "scamshield:unauthorized";

// The ONLY place the backend URL is read. Set it in .env (VITE_API_BASE_URL).
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:5000/api";

const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000,
  withCredentials: import.meta.env.VITE_WITH_CREDENTIALS === "true",
});

// Attach JWT automatically
client.interceptors.request.use((config) => {
  const token = getToken();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Normalise errors + detect expired / unauthorised sessions
client.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status;
    const url = error.config?.url || "";
    const isAuthCall = /\/auth\/(login|register)/.test(url);

    if (status === 401 && !isAuthCall) {
      window.dispatchEvent(new Event(UNAUTHORIZED_EVENT));
      error.userMessage = "Session expired. Please log in again.";
    } else {
      error.userMessage = getErrorMessage(error);
    }
    error.status = status;
    return Promise.reject(error);
  }
);

export default client;