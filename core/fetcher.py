import time
import requests

BINANCE_FUTURES_KLINES_URL = "https://fapi.binance.com/fapi/v1/klines"


def normalize_symbol(symbol):
    return str(symbol).replace("/", "").upper().strip()


def fetch_klines(symbol, interval, limit=200, timeout=10, retries=3, retry_sleep=2):
    symbol = normalize_symbol(symbol)

    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit,
    }

    last_error = None

    for attempt in range(1, retries + 1):
        try:
            r = requests.get(BINANCE_FUTURES_KLINES_URL, params=params, timeout=timeout)
            r.raise_for_status()

            data = r.json()
            if not isinstance(data, list):
                return []

            return data

        except Exception as e:
            last_error = e
            print(f"[FETCH ERROR] {symbol} {interval} {attempt}/{retries} -> {e}")
            if attempt < retries:
                time.sleep(retry_sleep)

    print(f"[FETCH FAILED] {symbol} {interval} -> {last_error}")
    return []


def fetch_multi_timeframe(symbol, timeframes, limit_signal, limit_context):
    return {
        "signal": fetch_klines(symbol, timeframes["signal"], limit_signal),
        "trend_1h": fetch_klines(symbol, timeframes["trend_1h"], limit_context),
        "trend_4h": fetch_klines(symbol, timeframes["trend_4h"], limit_context),
    }