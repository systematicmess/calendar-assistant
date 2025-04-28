from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import RedirectResponse

from ...services import google  # relative import from app.services

router = APIRouter()

@router.get("/url")
def oauth_url() -> dict[str, str]:
    """Return Google consent-screen URL + state string."""
    url, state = google.authorization_url()
    return {"url": url, "state": state}

@router.get("/callback")
def oauth_callback(
    code: str = Query(..., description="Auth code returned by Google"),
    state: str = Query(..., description="State parameter for CSRF check"),
):
    """
    Google redirects here after user grants permission.
    We exchange the code for tokens and set a lightweight cookie
    containing our internal `session_id`.
    """
    try:
        session_id = google.exchange_code(code, state)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    # For demo: drop user on a simple success page with their session_id.
    response = RedirectResponse(url=f"http://localhost:5173/callback?session={session_id}")
    # In production you’d set a secure HttpOnly cookie instead:
    # response.set_cookie("sid", session_id, httponly=True, secure=True, samesite="lax")
    return response
