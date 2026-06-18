# DNSE broker


## Required Google credentials for Gmail
Read Google API to get credentials.json & token.json
https://developers.google.com/gmail/api/guides

Read DNSE Lightspeed API
https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api/ii.-trading-api

## Use

```python
from vnbrokers.dnse import Broker

bearer_token = open("./dnse_token.txt").read().strip()
trading_token = open("./trading_token.txt").read().strip()

broker = Broker(
    symbol="VN30F2503",
    account_no="00010011111",
    bearer_token=bearer_token,
    trading_token=trading_token,
)
broker.pull_deal_data()
broker.open_long_deal(expected_price, order_type="MTL")

broker.open_short_deal(expected_price, order_type="MTL")

broker.set_force_stoploss(1364)
broker.set_take_profit(1390)
broker.set_risk_reward()

broker.close_all_open_deal(current_price)
```
