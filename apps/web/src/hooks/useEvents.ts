import { useQuery } from "@tanstack/react-query";
import { api } from "../api";
import { useAuth } from "./useAuth";

export interface CalendarEvent {
  id: string;
  summary?: string;
  start: string;          // ISO
  end: string;            // ISO
  hangoutLink?: string;
}

interface EventsResponse {
  events: CalendarEvent[];
  total_hours: number;
}

export function useEvents() {
  const { sessionId } = useAuth();

  return useQuery({
    queryKey: ["events", sessionId],
    enabled: !!sessionId,
    queryFn: async (): Promise<EventsResponse> => {
      const { data } = await api.get<EventsResponse>("/cal/events", {
        params: { session_id: sessionId },
      });
      return data;
    },
    staleTime: 1000 * 60, // 1 min
  });
}
