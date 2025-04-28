import axios from "axios";

export const api = axios.create({
  baseURL: "http://localhost:8000",
});

/* ─── 401 interceptor: clears stale session and sends user to /login ───────── */
api.interceptors.response.use(
  res => res,
  err => {
    if (err.response?.status === 401) {
      localStorage.removeItem("session_id"); // remove cached/stale ID
      window.location.href = "/login";       // force fresh sign-in
    }
    return Promise.reject(err);
  }
);
