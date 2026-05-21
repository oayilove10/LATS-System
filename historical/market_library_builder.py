import os

import pandas as pd

from historical.config import LIBRARY_DIR
from historical.market_regime_classifier import add_regime_label


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def add_basic_behavior_features(df):
    if df.empty:
        return df

    df = df.copy()

    df["return_pct"] = (
        (df["close"] - df["open"]) / df["open"]
    ) * 100

    df["range_pct"] = (
        (df["high"] - df["low"]) / df["open"]
    ) * 100

    df["volume_change_pct"] = (
        df["volume"].pct_change().fillna(0) * 100
    )

    df["ema_fast"] = df["close"].ewm(span=20).mean()
    df["ema_slow"] = df["close"].ewm(span=50).mean()

    df["trend_score"] = (
        (df["ema_fast"] - df["ema_slow"]) / df["close"]
    ) * 100

    df["volatility_score"] = (
        df["range_pct"].rolling(20).mean().fillna(0)
    )

    return df


def classify_behavior(row):
    trend_score = row.get("trend_score", 0)
    range_pct = row.get("range_pct", 0)
    return_pct = row.get("return_pct", 0)
    volume_change = row.get("volume_change_pct", 0)

    if range_pct > 4 and return_pct < -3:
        return "panic_drop"

    if trend_score > 1 and return_pct > 0:
        return "trend_continuation_up"

    if trend_score < -1 and return_pct < 0:
        return "trend_continuation_down"

    if abs(trend_score) < 0.3 and range_pct < 1:
        return "sideway_compression"

    if volume_change > 80 and abs(return_pct) > 1.5:
        return "volume_impulse"

    if trend_score > 0.5 and return_pct < 0:
        return "pullback_in_uptrend"

    if trend_score < -0.5 and return_pct > 0:
        return "relief_bounce_in_downtrend"

    return "normal"


def build_market_library(df, symbol, timeframe):
    if df.empty:
        return pd.DataFrame()

    df = add_basic_behavior_features(df)
    df = add_regime_label(df)

    df["behavior_type"] = df.apply(classify_behavior, axis=1)
    df["symbol"] = symbol
    df["timeframe"] = timeframe

    return df


def save_market_library(library_df, symbol, timeframe):
    ensure_dir(LIBRARY_DIR)

    path = os.path.join(
        LIBRARY_DIR,
        f"{symbol}_{timeframe}_market_library.csv",
    )

    library_df.to_csv(path, index=False, encoding="utf-8")

    return path


if __name__ == "__main__":
    print("market_library_builder ready")