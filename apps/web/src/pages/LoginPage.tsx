import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";
import { useAuth } from "../hooks/useAuth";

export default function LoginPage() {
  const { sessionId } = useAuth();
  const nav = useNavigate();
  const [loading, setLoading] = useState(false);

  // already logged-in? → jump to agenda
  useEffect(() => {
    if (sessionId) nav("/agenda");
  }, [sessionId, nav]);

  const handleSignIn = async () => {
    try {
      setLoading(true);
      const { data } = await api.get<{ url: string }>("/auth/url");
      window.location.href = data.url;          // off to Google consent
    } catch (err) {
      console.error(err);
      alert("Failed to start Google sign-in. Is the back-end running?");
      setLoading(false);
    }
  };

  return (
    <div className="h-screen flex flex-col items-center justify-center gap-6">
      <h1 className="text-3xl font-bold">Calendar Assistant</h1>

      <button
        onClick={handleSignIn}
        disabled={loading}
        className="px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
      >
        {loading ? "Redirecting…" : "Sign in with Google"}
      </button>
    </div>
  );
}
