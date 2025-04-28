# app/api/routers/calendar.py
from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from ...services import google

router = APIRouter()


# ---------------------------------------------------------------------
# Pydantic response models
# ---------------------------------------------------------------------
class CalendarEvent(BaseModel):
    id: str
    summary: str | None = None
    start: datetime
    end: datetime
    hangoutLink: str | None = None


class EventsResponse(BaseModel):
    events: List[CalendarEvent]
    total_hours: float = Field(..., description="Sum of event durations in hours")


# ---------------------------------------------------------------------
# Route: GET /cal/events
# ---------------------------------------------------------------------
@router.get("/events", response_model=EventsResponse)
def list_events(
    session_id: str = Query(..., description="Session ID from /auth/callback"),
    time_min: datetime = Query(
        default_factory=lambda: datetime.utcnow() - timedelta(days=7),
        description="ISO 8601 start (default: 7 days ago)",
    ),
    time_max: datetime = Query(
        default_factory=lambda: datetime.utcnow() + timedelta(days=1),
        description="ISO 8601 end (default: tomorrow)",
    ),
):
    """
    List calendar events between `time_min` and `time_max` (inclusive) and
    return total hours spent in meetings for that window.
    """
    try:
        svc = google.get_calendar_service(session_id)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc))

    items = (
        svc.events()
        .list(
            calendarId="primary",
            timeMin=time_min.isoformat() + "Z",
            timeMax=time_max.isoformat() + "Z",
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
        .get("items", [])
    )

    events: list[CalendarEvent] = []
    total_seconds = 0.0

    for ev in items:
        # events may be all-day (date) or timed (dateTime)
        start_raw = ev["start"].get("dateTime") or ev["start"]["date"]
        end_raw = ev["end"].get("dateTime") or ev["end"]["date"]

        start = google.parse_rfc3339(start_raw)
        end = google.parse_rfc3339(end_raw)

        events.append(
            CalendarEvent(
                id=ev["id"],
                summary=ev.get("summary"),
                start=start,
                end=end,
                hangoutLink=ev.get("hangoutLink"),
            )
        )
        total_seconds += (end - start).total_seconds()

    return EventsResponse(events=events, total_hours=round(total_seconds / 3600, 2))
