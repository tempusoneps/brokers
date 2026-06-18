import base64
import re
import time
from pathlib import Path

import click
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
GMAIL_DIR = Path(__file__).resolve().parent
AUTH_DIR = GMAIL_DIR.parent / "auth"
TOKEN_PATH = GMAIL_DIR / "token.json"
CREDENTIALS_PATH = GMAIL_DIR / "credentials.json"


def get_otp(message_body: str) -> str | None:
    match = re.search(r"\b(\d{4,8})\b", message_body)
    if match:
        return match.group(1)
    return None


def load_credentials():
    creds = None
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)

    if creds and creds.valid:
        return creds

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        return creds

    flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_PATH), SCOPES)
    return flow.run_local_server(port=0)


def decode_message_part(part: dict) -> str | None:
    body = part.get("body", {}).get("data", "")
    if body:
        return base64.urlsafe_b64decode(body + "===").decode("utf-8", errors="ignore")
    return None


def iter_message_texts(payload: dict):
    snippet = payload.get("snippet")
    if snippet:
        yield snippet

    for part in payload.get("parts", []):
        decoded = decode_message_part(part)
        if decoded:
            yield decoded

        nested = part.get("parts", [])
        if nested:
            yield from iter_message_texts({"parts": nested})


def fetch_latest_otp(
    output: Path | None = None,
    wait_seconds: int = 55,
    poll_attempts: int = 6,
    poll_interval: int = 5,
):
    creds = load_credentials()
    TOKEN_PATH.write_text(creds.to_json())

    target_path = output or (AUTH_DIR / "email_otp.txt")
    target_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        service = build("gmail", "v1", credentials=creds)
        if wait_seconds > 0:
            time.sleep(wait_seconds)

        otp = None
        for attempt in range(max(1, poll_attempts)):
            result = service.users().messages().list(
                userId="me",
                q="from:noreply@mail.dnse.com.vn",
            ).execute()
            messages = result.get("messages", [])
            if messages:
                msg = service.users().messages().get(userId="me", id=messages[0]["id"]).execute()
                payload = msg["payload"]

                for content in iter_message_texts(payload):
                    otp = get_otp(content)
                    if otp:
                        break

            if otp:
                break

            if attempt < poll_attempts - 1:
                time.sleep(poll_interval)

        if not otp:
            raise click.ClickException("OTP not found in the latest email")

        target_path.write_text(otp)
        click.echo(f"[dnse] OTP saved to {target_path}")
        return otp

    except HttpError as error:
        raise click.ClickException(f"Gmail API error: {error}") from error
