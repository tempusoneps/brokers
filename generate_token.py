import argparse
import json
import requests
from pathlib import Path

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
    'ContentType': 'application/json',
}

CONFIGS = {
    'dnse': {
        'login_url': 'https://services.entrade.com.vn/dnse-auth-service/login',
        'cred_key': 'dnse-auth',
        'token_field': 'token',
    },
    'entrade': {
        'login_url': 'https://services.entrade.com.vn/entrade-api/v2/auth',
        'cred_key': 'entrade-auth',
        'token_field': 'token',
    },
}


def generate_jwt_token(broker: str):
    config = CONFIGS[broker]
    auth_dir = Path(__file__).parent / 'src' / broker / 'auth'

    with open(auth_dir / 'credentials.json', 'r') as f:
        data = json.load(f)

    creds = data[config['cred_key']]['email-otp']
    res = requests.post(config['login_url'], json=creds, headers=HEADERS)
    res.raise_for_status()

    token = res.json()[config['token_field']]
    if not token:
        raise Exception(f"JWT token not found in response for {broker}")

    token_path = auth_dir / 'jwt_token.txt'
    token_path.write_text(token)
    print(f"[{broker}] JWT token saved to {token_path}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--broker', choices=['dnse', 'entrade'], required=True)
    args = parser.parse_args()

    generate_jwt_token(args.broker)
