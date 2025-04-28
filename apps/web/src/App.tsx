import { BrowserRouter, Routes, Route } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import LoginPage from "./pages/LoginPage";
import AuthCallback from "./pages/AuthCallback";
import AgendaPage from "./pages/AgendaPage";
import ChatPage from "./pages/ChatPage";

const qc = new QueryClient();

export default function App() {
  return (
    <QueryClientProvider client={qc}>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/callback" element={<AuthCallback />} />
          <Route path="/agenda" element={<AgendaPage />} />
          <Route path="/chat" element={<ChatPage />} />
          <Route path="*" element={<LoginPage />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
