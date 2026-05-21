import os
import pandas as pd

from historical.config import (
    HISTORICAL_RAW_DIR,
    SYMBOLS,
)


def load_raw_months(symbol, timeframe):
    folder = os.path.join(
        HISTORICAL_RAW_DIR,
        symbol,
        timeframe,
    )

    if not os.path.isdir(folder):
        print(f"folder not found: {folder}")
        return pd.DataFrame()

    files = sorted([
        os.path.join(folder, filename)
        for filename in os.listdir(folder)
        if filename.endswith(".csv")
    ])

    frames = []

    for path in files:
        df = pd.read_csv(path)
        frames.append(df)

    if not frames:
        return pd.DataFrame()

    df = pd.concat(
        frames,
        ignore_index=True,
    )

    df = df.sort_values(
        "open_time"
    ).reset_index(drop=True)

    return df


def add_indicators(df):
    df = df.copy()

    df["ema7"] = df["close"].ewm(
        span=7,
        adjust=False,
    ).mean()

    df["ema25"] = df["close"].ewm(
        span=25,
        adjust=False,
    ).mean()

    df["ema99"] = df["close"].ewm(
        span=99,
        adjust=False,
    ).mean()

    delta = df["close"].diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()

    rs = avg_gain / avg_loss

    df["rsi"] = 100 - (
        100 / (1 + rs)
    )

    df["momentum_3"] = (
        (df["close"] - df["close"].shift(3))
        / df["close"].shift(3)
    ) * 100

    df["distance_ema7"] = (
        (df["close"] - df["ema7"])
        / df["ema7"]
    ) * 100

    df["distance_ema25"] = (
        (df["close"] - df["ema25"])
        / df["ema25"]
    ) * 100

    return df


def classify_trend(row):
    close = row["close"]
    ema25 = row["ema25"]
    ema99 = row["ema99"]

    if close > ema25 > ema99:
        return "up"

    if close < ema25 < ema99:
        return "down"

    return "sideway"


def classify_signal(row):
    close = row["close"]
    open_price = row["open"]
    ema7 = row["ema7"]
    ema25 = row["ema25"]

    if close > open_price and close > ema7 > ema25:
        return "long"

    if close < open_price and close < ema7 < ema25:
        return "short"

    return "none"


def build_historical_signals(symbol, timeframe="15m"):
    df = load_raw_months(
        symbol=symbol,
        timeframe=timeframe,
    )

    if df.empty:
        return pd.DataFrame()

    df = add_indicators(df)

    rows = []

    for _, row in df.iterrows():
        if pd.isna(row["ema99"]):
            continue

        signal_type = classify_signal(row)

        if signal_type == "none":
            continue

        signal_id = (
            f"{symbol}_"
            f"{timeframe}_"
            f"{int(row['open_time'])}"
        )

        item = {
            "signal_id": signal_id,
            "symbol": symbol,
            "signal_time": row.get(
                "open_time_text",
                "",
            ),
            "signal_time_ms": int(row["open_time"]),
            "signal_tf": timeframe,
            "signal_type": signal_type,

            "open": row["open"],
            "high": row["high"],
            "low": row["low"],
            "close": row["close"],
            "volume": row["volume"],

            "ema7": row["ema7"],
            "ema25": row["ema25"],
            "ema99": row["ema99"],
            "rsi": row["rsi"],

            "trend_15m": classify_trend(row),
            "trend_1h": "EMPTY",
            "trend_4h": "EMPTY",
            "mtf_align": "EMPTY",
            "zone": "EMPTY",
            "rejection": "EMPTY",
            "volume_ratio": "EMPTY",
            "momentum_3": row["momentum_3"],
            "coin_behavior": "EMPTY",
            "distance_ema7": row["distance_ema7"],
            "distance_ema25": row["distance_ema25"],
        }

        rows.append(item)

    return pd.DataFrame(rows)


def save_historical_signals(symbol, timeframe="15m"):
    out_dir = os.path.join(
        "historical_output"
    )

    os.makedirs(
        out_dir,
        exist_ok=True,
    )

    signals = build_historical_signals(
        symbol=symbol,
        timeframe=timeframe,
    )

    path = os.path.join(
        out_dir,
        f"{symbol}_historical_signal_data.csv",
    )

    signals.to_csv(
        path,
        index=False,
        encoding="utf-8",
    )

    print(
        f"saved historical signals: {path}"
    )

    print(
        f"rows={len(signals)}"
    )

    return path


def main():
    for symbol in SYMBOLS:
        try:
            print("=" * 60)
            print(f"BUILD SIGNAL: {symbol}")
            print("=" * 60)

            save_historical_signals(
                symbol=symbol,
                timeframe="15m",
            )

        except KeyboardInterrupt:
            print("STOP SAFE")
            raise

        except Exception as e:
            print(
                f"[ERROR] {symbol} -> {e}"
            )


if __name__ == "__main__":
    main()