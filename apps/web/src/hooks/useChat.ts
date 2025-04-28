import { useMutation } from "@tanstack/react-query";
import { api } from "../api";
import { useAuth } from "./useAuth";

interface ChatPayload { session_id: string; message: string }
interface ChatResponse { reply: string }

export function useChat() {
  const { sessionId } = useAuth();

  return useMutation({
    mutationFn: async (message: string): Promise<string> => {
      const { data } = await api.post<ChatResponse>("/agent/chat", {
        session_id: sessionId,
        message,
      } satisfies ChatPayload);
      return data.reply;
    },
  });
}
