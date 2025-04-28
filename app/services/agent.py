# app/services/agent.py
from __future__ import annotations

import os
import re
from collections import deque
from datetime import datetime, timedelta
from typing import Deque, Dict, List, Tuple

from dateutil import parser as dt_parse       # python-dateutil
from openai import OpenAI
from pydantic import BaseModel

from . import google                           # calendar helpers

# ---------------------------------------------------------------------
# Config / globals
# ---------------------------------------------------------------------
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
MAX_HISTORY = 10                               # turns to keep per session
HISTORY: Dict[str, Deque[dict]] = {}
client = OpenAI()                              # needs OPENAI_API_KEY


# ---------------------------------------------------------------------
# Pydantic schema
# ---------------------------------------------------------------------
class ChatRequest(BaseModel):
    session_id: str
    message: str


# ---------------------------------------------------------------------
# Calendar helpers
# ---------------------------------------------------------------------
def _sum_hours(events: list[dict]) -> float:
    h = 0.0
    for ev in events:
        s_raw = ev["start"].get("dateTime") or ev["start"]["date"]
        e_raw = ev["end"].get("dateTime") or ev["end"]["date"]
        s = google.parse_rfc3339(s_raw)
        e = google.parse_rfc3339(e_raw)
        h += (e - s).total_seconds() / 3600
    return h


def _events_between(svc, start: datetime, end: datetime) -> list[dict]:
    rfc = lambda d: d.isoformat() + "Z"
    return (
        svc.events()
        .list(
            calendarId="primary",
            timeMin=rfc(start),
            timeMax=rfc(end),
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
        .get("items", [])
    )


# ---------------------------------------------------------------------
# Query parsing
# ---------------------------------------------------------------------
DATE_RE = re.compile(
    r"(?P<d>\d{4}-\d{2}-\d{2})|"                 # 2025-04-28
    r"(?P<month>\w+)\s+(?P<day>\d{1,2})(?:,\s*(?P<y>\d{4}))?",  # April 28 2025
    re.I,
)

WINDOW_RE = re.compile(
    r"\b(next|past)\s+(\d+)\s*(day|days|week|weeks)\b", re.I
)

TODAY_RE = re.compile(r"\btoday\b", re.I)
TOMORROW_RE = re.compile(r"\btomorrow\b", re.I)


def interpret_query(text: str) -> Tuple[datetime, datetime] | None:
    """
    Return (start, end) UTC datetimes for which the user requests stats,
    or None if the query is not a range we recognise.
    """
    text = text.lower()
    now = datetime.utcnow()

    # today / tomorrow
    if TODAY_RE.search(text):
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        return start, start + timedelta(days=1)
    if TOMORROW_RE.search(text):
        start = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        return start, start + timedelta(days=1)

    # "next 3 days / next 2 weeks / past 7 days"
    if m := WINDOW_RE.search(text):
        direction, num, unit = m.groups()
        num = int(num)
        delta = timedelta(days=num * (7 if "week" in unit else 1))
        if direction == "next":
            start = now
            end = now + delta
        else:                                   # past
            start = now - delta
            end = now
        return start, end

    # explicit date e.g. 2025-04-28 or April 28 2025
    if m := DATE_RE.search(text):
        try:
            dt = dt_parse.parse(m.group(0), dayfirst=False, yearfirst=True)
            dt = dt.replace(hour=0, minute=0, second=0, microsecond=0)
            return dt, dt + timedelta(days=1)
        except Exception:
            pass

    return None


# ---------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------
def chat(req: ChatRequest) -> str:
    svc = google.get_calendar_service(req.session_id)
    utc_now = datetime.utcnow()

    # Base aggregates (30-day back, 7-day forward)
    past30 = _events_between(svc, utc_now - timedelta(days=30), utc_now)
    next7  = _events_between(svc, utc_now, utc_now + timedelta(days=7))

    summary_lines = [
        f"In the last 30 days you spent **{_sum_hours(past30):.1f} h** in meetings.",
        f"In the next 7 days you have **{_sum_hours(next7):.1f} h** scheduled.",
    ]

    # Detect fine-grained query
    span = interpret_query(req.message)
    if span:
        start, end = span
        hrs = _sum_hours(_events_between(svc, start, end))
        label = start.strftime("%Y-%m-%d") if (end - start).days == 1 else f"{(end-start).days}-day window"
        summary_lines.append(f"Total for **{label}**: **{hrs:.1f} h**")

    calendar_facts = "\n".join(summary_lines)

    # Keep short history
    hist = HISTORY.setdefault(req.session_id, deque(maxlen=MAX_HISTORY))
    hist.append({"role": "user", "content": req.message})

    messages: List[dict] = [
        {
            "role": "system",
            "content": (
                "You are Calendar-GPT. Use **only** the factual numbers below. "
                "If data is missing, ask the user to clarify; do not guess.\n\n"
                + calendar_facts
            ),
        },
        *hist,
    ]

    reply = (
        client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            temperature=0,
        )
        .choices[0]
        .message.content
    )

    hist.append({"role": "assistant", "content": reply})
    return reply
