import { Link } from "react-router-dom";
import { useEvents } from "../hooks/useEvents";

export default function AgendaPage() {
  const { data, isLoading, error } = useEvents();

  if (isLoading) return <p className="p-4">Loading events…</p>;
  if (error)     return <p className="p-4 text-red-500">Error: {(error as Error).message}</p>;

  return (
    <div className="max-w-3xl mx-auto p-4 space-y-6">
      <header className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Your agenda</h1>
        <Link to="/chat" className="text-blue-400 hover:underline">Chat ↗</Link>
      </header>

      <p className="text-lg">
        Total meeting time (last 7 d → tomorrow):{" "}
        <span className="font-semibold">{data?.total_hours.toFixed(2)} h</span>
      </p>

      <ul className="space-y-3">
        {data?.events.map(ev => (
          <li key={ev.id} className="border border-slate-600 rounded p-3">
            <p className="font-medium">{ev.summary ?? "(no title)"}</p>
            <p className="text-sm text-slate-400">
              {new Date(ev.start).toLocaleString()} –{" "}
              {new Date(ev.end).toLocaleString()}
            </p>
          </li>
        ))}
      </ul>
    </div>
  );
}
