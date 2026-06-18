import click
import requests
from pathlib import Path

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
    'ContentType': 'application/json',
}

PACKAGE_DIR = Path(__file__).resolve().parent
DNSE_AUTH_DIR = PACKAGE_DIR / 'dnse' / 'auth'
ENTRADE_AUTH_DIR = PACKAGE_DIR / 'entrade' / 'auth'

BROKER_CONFIGS = {
    'dnse': {
        'login_url': 'https://services.entrade.com.vn/dnse-auth-service/login',
        'auth_dir': DNSE_AUTH_DIR,
    },
    'entrade': {
        'login_url': 'https://services.entrade.com.vn/entrade-api/v2/auth',
        'auth_dir': ENTRADE_AUTH_DIR,
    },
}


def generate_dnse_trading_token(jwt_token: str, auth_dir: Path, trading_token_path: Path | None = None):
    auth_dir.mkdir(parents=True, exist_ok=True)
    click.echo('Requesting email OTP...')
    otp_response = requests.get(
        'https://services.entrade.com.vn/dnse-auth-service/api/email-otp',
        headers={**HEADERS, 'Authorization': f'Bearer {jwt_token}'},
    )
    otp_response.raise_for_status()
    from vnbrokers.dnse.gmail.get_otp import fetch_latest_otp

    otp = fetch_latest_otp(output=auth_dir / 'email_otp.txt')

    res = requests.post(
        'https://services.entrade.com.vn/dnse-order-service/trading-token',
        headers={**HEADERS, 'Authorization': f'Bearer {jwt_token}', 'otp': otp},
    )
    res.raise_for_status()

    trading = res.json().get('tradingToken')
    if not trading:
        raise click.ClickException('Trading token not found in response')

    trading_path = trading_token_path or (auth_dir / 'trading_token.txt')
    trading_path.parent.mkdir(parents=True, exist_ok=True)
    trading_path.write_text(trading)
    click.echo(f'[dnse] Trading token saved to {trading_path}')


@click.group()
def cli():
    pass


@cli.command()
@click.option('--broker', type=click.Choice(['dnse', 'entrade']), required=True)
@click.option('--username', required=True, help='Account username')
@click.option('--password', required=True, hide_input=True, help='Account password')
@click.option(
    '--output',
    '-o',
    type=click.Path(path_type=Path, dir_okay=False),
    default=None,
    help='Path to save the JWT token file.',
)
def token(broker, username, password, output):
    """Generate and save tokens for a broker."""
    config = BROKER_CONFIGS[broker]
    login_url = config['login_url']

    res = requests.post(login_url, json={'username': username, 'password': password}, headers=HEADERS)
    res.raise_for_status()

    jwt = res.json().get('token')
    if not jwt:
        raise click.ClickException('JWT token not found in response')

    auth_dir = config['auth_dir']
    token_path = output or (auth_dir / 'jwt_token.txt')
    token_path.parent.mkdir(parents=True, exist_ok=True)
    token_path.write_text(jwt)
    click.echo(f'[{broker}] JWT token saved to {token_path}')

    if broker == 'dnse':
        generate_dnse_trading_token(jwt, token_path.parent)


@cli.command('dnse-gmail-quickstart')
@click.option(
    '--output',
    '-o',
    type=click.Path(path_type=Path, dir_okay=False),
    default=None,
    help='Path to save the extracted OTP.',
)
def dnse_gmail_quickstart(output):
    """Fetch the latest DNSE OTP from Gmail and save it to a file."""
    from vnbrokers.dnse.gmail.quickstart import run

    run(output)
