import click
import requests
from pathlib import Path

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
    'ContentType': 'application/json',
}

BROKER_CONFIGS = {
    'dnse': {
        'login_url': 'https://services.entrade.com.vn/dnse-auth-service/login',
    },
    'entrade': {
        'login_url': 'https://services.entrade.com.vn/entrade-api/v2/auth',
    },
}


@click.group()
def cli():
    pass


@cli.command()
@click.option('--broker', type=click.Choice(['dnse', 'entrade']), required=True)
@click.option('--username', required=True, help='Account username')
@click.option('--password', required=True, hide_input=True, help='Account password')
def token(broker, username, password):
    """Generate and save JWT token for a broker."""
    login_url = BROKER_CONFIGS[broker]['login_url']

    res = requests.post(login_url, json={'username': username, 'password': password}, headers=HEADERS)
    res.raise_for_status()

    jwt = res.json().get('token')
    if not jwt:
        raise click.ClickException('JWT token not found in response')

    token_path = Path.cwd() / f'{broker}_jwt_token.txt'
    token_path.write_text(jwt)
    click.echo(f'[{broker}] JWT token saved to {token_path}')


@cli.command('trading-token')
def trading_token():
    """Generate trading token for DNSE (requires email OTP)."""
    token_path = Path.cwd() / 'dnse_jwt_token.txt'
    if not token_path.exists():
        raise click.ClickException(f'JWT token not found at {token_path}. Run: vnbrokers token --broker dnse')

    jwt_token = token_path.read_text().strip()

    click.echo('Requesting email OTP...')
    requests.get(
        'https://services.entrade.com.vn/dnse-auth-service/api/email-otp',
        headers={**HEADERS, 'Authorization': f'Bearer {jwt_token}'},
    )

    otp = click.prompt('Enter OTP received in email')

    res = requests.post(
        'https://services.entrade.com.vn/dnse-order-service/trading-token',
        headers={**HEADERS, 'Authorization': f'Bearer {jwt_token}', 'otp': otp},
    )
    res.raise_for_status()

    trading = res.json().get('tradingToken')
    if not trading:
        raise click.ClickException('Trading token not found in response')

    trading_path = Path.cwd() / 'dnse_trading_token.txt'
    trading_path.write_text(trading)
    click.echo(f'[dnse] Trading token saved to {trading_path}')
