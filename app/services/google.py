# app/services/google.py
from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone
from typing import Dict

from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# ---------------------------------------------------------------------
# In-memory token store (keyed by session_id)
# ---------------------------------------------------------------------
TOKENS: Dict[str, Credentials] = {}

SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
    # add more scopes later if you need write access
]

# ---------------------------------------------------------------------
# OAuth helpers
# ---------------------------------------------------------------------
def build_flow() -> Flow:
    """Create an OAuth 2.0 Flow configured for the installed-app pattern."""
    return Flow.from_client_config(
        {
            "installed": {
                "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                "redirect_uris": [os.getenv("GOOGLE_REDIRECT")],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=SCOPES,
        redirect_uri=os.getenv("GOOGLE_REDIRECT"),
    )


def authorization_url() -> tuple[str, str]:
    """Return (auth_url, state) for the Google consent screen."""
    flow = build_flow()
    auth_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )
    return auth_url, state


def exchange_code(code: str, _state: str | None = None) -> str:
    """
    Swap the auth code for tokens and return a new session_id.

    google-auth-oauthlib validates the state internally;
    the library no longer exposes flow.state, so we don’t compare here.
    """
    flow = build_flow()
    flow.fetch_token(code=code)

    creds: Credentials = flow.credentials
    session_id = str(uuid.uuid4())
    TOKENS[session_id] = creds
    return session_id


# ---------------------------------------------------------------------
# Calendar helpers
# ---------------------------------------------------------------------
def get_calendar_service(session_id: str):
    """Return an authenticated Calendar API service."""
    creds = TOKENS.get(session_id)
    if not creds or not creds.valid:
        raise ValueError("Invalid or expired session_id")
    return build("calendar", "v3", credentials=creds)


def parse_rfc3339(value: str) -> datetime:
    """
    Convert RFC-3339 / ISO date-time strings (with or without trailing 'Z')
    to timezone-aware datetime objects in UTC.
    """
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    return datetime.fromisoformat(value).astimezone(timezone.utc)
