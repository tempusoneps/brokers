from pathlib import Path

import click
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
GMAIL_DIR = Path(__file__).resolve().parent
TOKEN_PATH = GMAIL_DIR / "token.json"


def load_credentials(credentials_path: Path):
    creds = None
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)

    if creds and creds.valid:
        return creds

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        return creds

    flow = InstalledAppFlow.from_client_secrets_file(str(credentials_path), SCOPES)
    return flow.run_local_server(port=0)


def run(credentials_path: Path, output: Path | None = None):
    creds = load_credentials(credentials_path)
    token_path = output or TOKEN_PATH
    token_path.parent.mkdir(parents=True, exist_ok=True)
    token_path.write_text(creds.to_json())
    click.echo(f"[dnse] Gmail token saved to {token_path}")


@click.command()
@click.option(
    "--credentials",
    "-c",
    type=click.Path(path_type=Path, dir_okay=False, exists=True),
    required=True,
    help="Path to Gmail OAuth client secrets JSON.",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path, dir_okay=False),
    default=None,
    help="Path to save Gmail token.json.",
)
def quickstart(credentials, output):
    """Authorize Gmail and save token.json."""
    run(credentials, output)


if __name__ == "__main__":
    quickstart()
