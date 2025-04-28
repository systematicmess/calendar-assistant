import { useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

export default function AuthCallback() {
  const [params] = useSearchParams();
  const { login } = useAuth();
  const nav = useNavigate();

  useEffect(() => {
    const sid = params.get("session");
    if (sid) {
      login(sid);
      nav("/agenda", { replace: true });
    } else {
      nav("/login", { replace: true });
    }
  }, [login, nav, params]);

  return <p className="p-4">Completing sign-in…</p>;
}
