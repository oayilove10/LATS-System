import time
from datetime import datetime, timezone

import pandas as pd
import requests

from historical.config import (
    BINANCE_KLINES_URL,
    LIMIT,
    REQUEST_SLEEP,
    MAX_RETRY,
)


def to_ms(date_text):
    dt = datetime.fromisoformat(date_text)

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    return int(dt.timestamp() * 1000)


def fetch_klines(symbol, timeframe, start_ms, end_ms):
    params = {
        "symbol": symbol,
        "interval": timeframe,
        "startTime": start_ms,
        "endTime": end_ms,
        "limit": LIMIT,
    }

    last_error = None

    for attempt in range(1, MAX_RETRY + 1):
        try:
            response = requests.get(
                BINANCE_KLINES_URL,
                params=params,
                timeout=20,
            )

            response.raise_for_status()

            return response.json()

        except Exception as e:
            last_error = e

            print(
                f"[WARN] fetch retry "
                f"{attempt}/{MAX_RETRY} | "
                f"{symbol} {timeframe} | {e}"
            )

            time.sleep(1)

    raise RuntimeError(
        f"fetch failed after retry | "
        f"{symbol} {timeframe} | {last_error}"
    )


def klines_to_df(klines, symbol, timeframe):
    columns = [
        "open_time",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "close_time",
        "quote_asset_volume",
        "number_of_trades",
        "taker_buy_base_volume",
        "taker_buy_quote_volume",
        "ignore",
    ]

    df = pd.DataFrame(
        klines,
        columns=columns,
    )

    if df.empty:
        return df

    numeric_cols = [
        "open",
        "high",
        "low",
        "close",
        "volume",
        "quote_asset_volume",
        "taker_buy_base_volume",
        "taker_buy_quote_volume",
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce",
        )

    df["open_time"] = pd.to_numeric(
        df["open_time"],
        errors="coerce",
    )

    df["close_time"] = pd.to_numeric(
        df["close_time"],
        errors="coerce",
    )

    df["open_time_text"] = pd.to_datetime(
        df["open_time"],
        unit="ms",
        utc=True,
    ).dt.strftime("%Y-%m-%d %H:%M:%S")

    df["close_time_text"] = pd.to_datetime(
        df["close_time"],
        unit="ms",
        utc=True,
    ).dt.strftime("%Y-%m-%d %H:%M:%S")

    df["symbol"] = symbol
    df["timeframe"] = timeframe

    return df


def download_historical_range(
    symbol,
    timeframe,
    start_date,
    end_date,
):
    start_ms = to_ms(start_date)
    end_ms = to_ms(end_date)

    all_klines = []
    current_ms = start_ms

    while current_ms < end_ms:
        klines = fetch_klines(
            symbol=symbol,
            timeframe=timeframe,
            start_ms=current_ms,
            end_ms=end_ms,
        )

        if not klines:
            break

        all_klines.extend(klines)

        last_open_time = klines[-1][0]
        next_ms = last_open_time + 1

        if next_ms <= current_ms:
            break

        current_ms = next_ms

        print(
            f"{symbol} {timeframe} "
            f"downloaded rows={len(all_klines)}"
        )

        time.sleep(REQUEST_SLEEP)

    df = klines_to_df(
        klines=all_klines,
        symbol=symbol,
        timeframe=timeframe,
    )

    return df