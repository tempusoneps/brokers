# DNSE broker


## Required Google credentials for Gmail
Read Google API to get credentials.json & token.json
https://developers.google.com/gmail/api/guides

Read Entrade API
https://services.entrade.com.vn/

## Use

```python
from vnbrokers.entrade import Broker

bearer_token = open("./entrade_token.txt").read().strip()

broker = Broker(
    symbol="VN30F2503",
    investor_id="00010011111",
    investor_account_id="00010011112",
    bearer_token=bearer_token,
)
broker.pull_deal_data()
broker.open_long_deal(expected_price, order_type="MTL")

broker.open_short_deal(expected_price, order_type="MTL")

broker.set_force_stoploss(1364)
broker.set_take_profit(1390)
broker.set_risk_reward()

broker.close_all_open_deal(current_price)
```
