"""Coinbase model"""
__docformat__ = "numpy"

import pandas as pd
import gamestonk_terminal.config_terminal as cfg
from gamestonk_terminal.cryptocurrency.coinbase_helpers import (
    CoinbaseProAuth,
    _check_account_validity,
    make_coinbase_request,
)


def get_accounts(add_current_price: bool = True, currency: str = "USD") -> pd.DataFrame:
    """Get list of all your trading accounts. [Source: Coinbase]

    Single account information:

    .. code-block:: json

        {
            "id": "71452118-efc7-4cc4-8780-a5e22d4baa53",
            "currency": "BTC",
            "balance": "0.0000000000000000",
            "available": "0.0000000000000000",
            "hold": "0.0000000000000000",
            "profile_id": "75da88c5-05bf-4f54-bc85-5c775bd68254"
        }

    .

    Parameters
    -------
    add_current_price: bool
        Boolean to query coinbase for current price
    currency: str
        Currency to convert to, defaults to 'USD'

    Returns
    -------
    pd.DataFrame
        DataFrame with all your trading accounts.
    """
    auth = CoinbaseProAuth(
        cfg.API_COINBASE_KEY, cfg.API_COINBASE_SECRET, cfg.API_COINBASE_PASS_PHRASE
    )
    resp = make_coinbase_request("/accounts", auth=auth)
    if not resp:
        return pd.DataFrame()

    df = pd.DataFrame(resp)
    df = df[df.balance.astype(float) > 0]
    if add_current_price:
        current_prices = []
        for _, row in df.iterrows():
            to_get = f"{row.currency}-{currency}"
            current_prices.append(
                float(
                    make_coinbase_request(f"/products/{to_get}/stats", auth=auth)[
                        "last"
                    ]
                )
            )
        df["current_price"] = current_prices
        df[f"BalanceValue({currency})"] = df.current_price * df.balance.astype(float)
        return df[
            [
                "id",
                "currency",
                "balance",
                "available",
                "hold",
                f"BalanceValue({currency})",
            ]
        ]
    return df[["id", "currency", "balance", "available", "hold"]]


def get_account_history(account: str) -> pd.DataFrame:
    """Get your account history. Account activity either increases or decreases your account balance. [Source: Coinbase]

    Example api response:

    .. code-block:: json

        {
            "id": "100",
            "created_at": "2014-11-07T08:19:27.028459Z",
            "amount": "0.001",
            "balance": "239.669",
            "type": "fee",
            "details": {
                "order_id": "d50ec984-77a8-460a-b958-66f114b0de9b",
                "trade_id": "74",
                "product_id": "BTC-USD"
            }
        }

    .

    Parameters
    ----------
    account: str
        id ("71452118-efc7-4cc4-8780-a5e22d4baa53") or currency (BTC)
    Returns
    -------
    pd.DataFrame
        DataFrame with account history.
    """
    auth = CoinbaseProAuth(
        cfg.API_COINBASE_KEY, cfg.API_COINBASE_SECRET, cfg.API_COINBASE_PASS_PHRASE
    )

    account = _check_account_validity(account)
    if not account:
        return pd.DataFrame()

    resp = make_coinbase_request(f"/accounts/{account}/holds", auth=auth)
    if not resp:
        return pd.DataFrame()
    df = pd.json_normalize(resp)

    try:
        df.columns = [
            col.replace("details.", "") if "details" in col else col
            for col in df.columns
        ]
    except Exception as e:
        print(e)

    return df


def get_orders() -> pd.DataFrame:
    """List your current open orders. Only open or un-settled orders are returned. [Source: Coinbase]

    Example response from API:

    .. code-block:: json

        {
            "id": "d0c5340b-6d6c-49d9-b567-48c4bfca13d2",
            "price": "0.10000000",
            "size": "0.01000000",
            "product_id": "BTC-USD",
            "side": "buy",
            "stp": "dc",
            "type": "limit",
            "time_in_force": "GTC",
            "post_only": false,
            "created_at": "2016-12-08T20:02:28.53864Z",
            "fill_fees": "0.0000000000000000",
            "filled_size": "0.00000000",
            "executed_value": "0.0000000000000000",
            "status": "open",
            "settled": false
        }

    .

    Returns
    -------
    pd.DataFrame
        Open orders in your account
    """

    auth = CoinbaseProAuth(
        cfg.API_COINBASE_KEY, cfg.API_COINBASE_SECRET, cfg.API_COINBASE_PASS_PHRASE
    )
    resp = make_coinbase_request("/orders", auth=auth)
    if not resp:
        return pd.DataFrame(
            columns=[
                "product_id",
                "side",
                "price",
                "size",
                "type",
                "created_at",
                "status",
            ]
        )
    return pd.DataFrame(resp)[
        ["product_id", "side", "price", "size", "type", "created_at", "status"]
    ]


def get_deposits(deposit_type: str = "deposit") -> pd.DataFrame:
    """Get a list of deposits for your account. [Source: Coinbase]

    Parameters
    ----------
    deposit_type: str
        internal_deposits (transfer between portfolios) or deposit

    Returns
    -------
    pd.DataFrame
        List of deposits
    """

    auth = CoinbaseProAuth(
        cfg.API_COINBASE_KEY, cfg.API_COINBASE_SECRET, cfg.API_COINBASE_PASS_PHRASE
    )
    params = {"type": deposit_type}
    if deposit_type not in ["internal_deposit", "deposit"]:
        params["type"] = "deposit"
    resp = make_coinbase_request("/transfers", auth=auth, params=params)
    if not resp:
        return pd.DataFrame()

    if isinstance(resp, tuple):
        resp = resp[0]

    # pylint:disable=no-else-return
    if deposit_type == "deposit":
        return pd.json_normalize(resp)
    else:
        return pd.DataFrame(resp)[["type", "created_at", "amount", "currency"]]
