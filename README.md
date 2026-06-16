# vnbrokers

Python SDK cho các sàn chứng khoán phái sinh Việt Nam (DNSE, Entrade).

## Cài đặt

```bash
uv add git+https://github.com/tempusoneps/vnbrokers.git
```

Cài branch cụ thể:

```bash
uv add git+https://github.com/tempusoneps/vnbrokers.git@develop
```

## Cấu hình

Mỗi broker cần file `credentials.json` và `jwt_token.txt` trong thư mục `auth/` tương ứng.

**DNSE** — `src/dnse/auth/credentials.json`:

```json
{
  "dnse-auth": {
    "email-otp": {
      "username": "064C111111",
      "password": "your_password"
    },
    "account": {
      "no": "00010011111"
    }
  }
}
```

**Entrade** — `src/entrade/auth/credentials.json`:

```json
{
  "entrade-auth": {
    "email-otp": {
      "username": "064C111111",
      "password": "your_password"
    },
    "account": {
      "no": "00010011111"
    }
  }
}
```

## CLI

Sinh token trước khi dùng SDK:

```bash
# JWT token
vnbrokers token --broker dnse
vnbrokers token --broker entrade

# Trading token DNSE (yêu cầu nhập OTP qua email)
vnbrokers trading-token
```

## Sử dụng

### DNSE

```python
from dnse import Broker

broker = Broker(
    symbol="VN30F1M",
    account_no="00010011111",
)
broker.set_qty(1)
broker.open_long_deal(1200.0)
```

### Entrade

```python
from entrade import Broker

broker = Broker(
    symbol="VN30F1M",
    investor_id="00010011111",
)
broker.set_qty(1)
broker.open_long_deal(1200.0)
```

## Brokers được hỗ trợ

| Broker  | JWT Token | Trading Token |
|---------|-----------|---------------|
| DNSE    | ✓         | ✓             |
| Entrade | ✓         | —             |
