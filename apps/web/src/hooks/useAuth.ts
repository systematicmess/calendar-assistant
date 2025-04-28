import { useState } from "react";

export function useAuth() {
  const [sessionId, setSessionId] = useState<string | null>(
    () => localStorage.getItem("session_id")
  );

  const login = (id: string) => {
    localStorage.setItem("session_id", id);
    setSessionId(id);
  };

  const logout = () => {
    localStorage.removeItem("session_id");
    setSessionId(null);
  };

  return { sessionId, login, logout };
}
