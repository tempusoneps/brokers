import json
import click
import requests
from pathlib import Path

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
    'ContentType': 'application/json',
}

AUTH_DIR = Path(__file__).parent.parent

BROKER_CONFIGS = {
    'dnse': {
        'login_url': 'https://services.entrade.com.vn/dnse-auth-service/login',
        'cred_key': 'dnse-auth',
    },
    'entrade': {
        'login_url': 'https://services.entrade.com.vn/entrade-api/v2/auth',
        'cred_key': 'entrade-auth',
    },
}


@click.group()
def cli():
    pass


@cli.command()
@click.option('--broker', type=click.Choice(['dnse', 'entrade']), required=True)
def token(broker):
    """Generate JWT token for a broker."""
    config = BROKER_CONFIGS[broker]
    auth_dir = AUTH_DIR / broker / 'auth'

    with open(auth_dir / 'credentials.json') as f:
        data = json.load(f)

    creds = data[config['cred_key']]['email-otp']
    res = requests.post(config['login_url'], json=creds, headers=HEADERS)
    res.raise_for_status()

    jwt = res.json().get('token')
    if not jwt:
        raise click.ClickException('JWT token not found in response')

    (auth_dir / 'jwt_token.txt').write_text(jwt)
    click.echo(f'[{broker}] JWT token saved.')


@cli.command('trading-token')
def trading_token():
    """Generate trading token for DNSE (requires email OTP)."""
    auth_dir = AUTH_DIR / 'dnse' / 'auth'

    bearer_token = (auth_dir / 'jwt_token.txt').read_text().strip()
    if not bearer_token:
        raise click.ClickException('JWT token not found. Run: vnbrokers token --broker dnse')

    click.echo('Requesting email OTP...')
    requests.get(
        'https://services.entrade.com.vn/dnse-auth-service/api/email-otp',
        headers={**HEADERS, 'Authorization': f'Bearer {bearer_token}'},
    )

    otp = click.prompt('Enter OTP received in email')

    res = requests.post(
        'https://services.entrade.com.vn/dnse-order-service/trading-token',
        headers={**HEADERS, 'Authorization': f'Bearer {bearer_token}', 'otp': otp},
    )
    res.raise_for_status()

    trading_token = res.json().get('tradingToken')
    if not trading_token:
        raise click.ClickException('Trading token not found in response')

    (auth_dir / 'trading_token.txt').write_text(trading_token)
    click.echo('[dnse] Trading token saved.')
