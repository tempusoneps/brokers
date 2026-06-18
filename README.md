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

CLI không còn đọc `credentials.json` của broker nữa. Bạn truyền thẳng `--username` và `--password` khi chạy `vnbrokers token`.

File cần cho DNSE Gmail OAuth:

- `credentials.json`: OAuth client secrets tải từ Google Cloud Console, bạn truyền vào khi chạy `dnse-gmail-quickstart`
- `src/vnbrokers/dnse/gmail/token.json`: file token được tạo sau lần authorize đầu tiên

Nếu chưa có `credentials.json` cho Gmail, hãy tạo OAuth Client ID kiểu Desktop app trong Google Cloud Console rồi tải JSON về.

## CLI

Sinh token trước khi dùng SDK:

```bash
# DNSE: sinh luôn JWT + trading token, tự lấy OTP từ Gmail
vnbrokers dnse-gmail-quickstart --credentials ./credentials.json
vnbrokers token --broker dnse --username YOUR_USERNAME --password YOUR_PASSWORD
vnbrokers token --broker dnse --username YOUR_USERNAME --password YOUR_PASSWORD -o ./dnse_token.txt

# Entrade: chỉ sinh JWT token
vnbrokers token --broker entrade --username YOUR_USERNAME --password YOUR_PASSWORD
vnbrokers token --broker entrade --username YOUR_USERNAME --password YOUR_PASSWORD -o ./entrade_token.txt

# DNSE Gmail OAuth helper: chỉ authorize Gmail và tạo token.json
vnbrokers dnse-gmail-quickstart --credentials ./credentials.json -o ./src/vnbrokers/dnse/gmail/token.json
```

Mặc định nếu không truyền `-o`:

- DNSE JWT token: `src/vnbrokers/dnse/auth/jwt_token.txt`
- DNSE trading token: `src/vnbrokers/dnse/auth/trading_token.txt`
- Entrade JWT token: `src/vnbrokers/entrade/auth/jwt_token.txt`
- Gmail token: `src/vnbrokers/dnse/gmail/token.json`

Nếu truyền `-o` cho `vnbrokers token --broker dnse`, file JWT sẽ được lưu đúng path bạn chọn và trading token sẽ được lưu cùng thư mục đó.

## Sử dụng

### DNSE

```python
from vnbrokers.dnse import Broker

broker = Broker(
    symbol="VN30F1M",
    account_no="00010011111",
)
broker.set_qty(1)
broker.open_long_deal(1200.0)
```

### Entrade

```python
from vnbrokers.entrade import Broker

broker = Broker(
    symbol="VN30F1M",
    investor_id="00010011111",
)
broker.set_qty(1)
broker.open_long_deal(1200.0)
```

### Luồng DNSE

1. Chạy `vnbrokers dnse-gmail-quickstart --credentials ./credentials.json` một lần để authorize Gmail và tạo `token.json`.
2. Chạy `vnbrokers token --broker dnse --username ... --password ...` để sinh JWT và trading token.
3. SDK DNSE đọc token từ `src/vnbrokers/dnse/auth/`.

## Brokers được hỗ trợ

| Broker  | JWT Token | Trading Token |
|---------|-----------|---------------|
| DNSE    | ✓         | ✓             |
| Entrade | ✓         | —             |
