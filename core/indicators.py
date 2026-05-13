import pandas as pd


def klines_to_df(klines):
    df = pd.DataFrame(klines, columns=[
        "time_ms", "open", "high", "low", "close", "volume",
        "close_time", "qav", "trades", "tb_base", "tb_quote", "ignore"
    ])

    for c in ["open", "high", "low", "close", "volume"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    df["time_ms"] = pd.to_numeric(df["time_ms"], errors="coerce")
    df = df.dropna().reset_index(drop=True)
    return df


def add_indicators(df):
    df["ema7"] = df["close"].ewm(span=7, adjust=False).mean()
    df["ema25"] = df["close"].ewm(span=25, adjust=False).mean()
    df["ema99"] = df["close"].ewm(span=99, adjust=False).mean()

    delta = df["close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(
        alpha=1 / 14,
        min_periods=14,
        adjust=False
    ).mean()

    avg_loss = loss.ewm(
        alpha=1 / 14,
        min_periods=14,
        adjust=False
    ).mean()

    rs = avg_gain / avg_loss.replace(0, 1e-9)
    df["rsi"] = (100 - (100 / (1 + rs))).fillna(50)

    return df


def detect_rejection(row):
    o = float(row["open"])
    h = float(row["high"])
    l = float(row["low"])
    c = float(row["close"])

    candle_range = h - l

    if candle_range <= 0:
        return "none", 0, 0.0

    body = abs(c - o)
    upper = h - max(o, c)
    lower = min(o, c) - l

    upper_pct = upper / candle_range
    lower_pct = lower / candle_range
    body_pct = body / candle_range

    if upper_pct >= 0.4 and upper > body:
        return "bearish", round(upper_pct * 100, 2), round(body_pct, 4)

    if lower_pct >= 0.4 and lower > body:
        return "bullish", round(lower_pct * 100, 2), round(body_pct, 4)

    return "none", 0, round(body_pct, 4)


def detect_ema_cross(df):
    if len(df) < 3:
        return "none"

    prev = df.iloc[-2]
    last = df.iloc[-1]

    prev_diff = prev["ema7"] - prev["ema25"]
    now_diff = last["ema7"] - last["ema25"]

    if prev_diff <= 0 and now_diff > 0:
        return "bullish_cross"

    if prev_diff >= 0 and now_diff < 0:
        return "bearish_cross"

    return "none"


def classify_trend(df):
    if df is None or len(df) < 50:
        return "unknown", "unknown"

    df = add_indicators(df.copy())
    last = df.iloc[-1]

    close = float(last["close"])
    ema25 = float(last["ema25"])
    ema99 = float(last["ema99"])

    dist = (ema25 - ema99) / max(abs(ema99), 1e-9)

    if close > ema25 > ema99 and dist > 0.006:
        return "strong_up", "clear"

    if close > ema25:
        return "up", "moderate"

    if close < ema25 < ema99 and dist < -0.006:
        return "strong_down", "clear"

    if close < ema25:
        return "down", "moderate"

    return "sideway", "weak"


def build_feature_row(symbol, signal_tf, klines):
    df = klines_to_df(klines)

    if len(df) < 100:
        return None

    # ใช้แท่งปิดล่าสุดเสมอ:
    # ถ้าแท่งสุดท้ายยังวิ่งอยู่ ใช้แท่งก่อนหน้า
    df = df.iloc[:-1].copy()

    if len(df) < 100:
        return None

    df = add_indicators(df)
    last = df.iloc[-1]

    rejection_type, rejection_score, candle_strength = detect_rejection(last)
    ema_cross = detect_ema_cross(df)

    close = float(last["close"])
    ema7 = float(last["ema7"])
    ema25 = float(last["ema25"])
    ema99 = float(last["ema99"])

    distance_ema7 = round(
        (close - ema7) / max(abs(ema7), 1e-9),
        6
    )

    distance_ema25 = round(
        (close - ema25) / max(abs(ema25), 1e-9),
        6
    )

    distance_ema99 = round(
        (close - ema99) / max(abs(ema99), 1e-9),
        6
    )

    momentum_3 = 0.0

    if len(df) >= 4:
        prev_close = float(df.iloc[-4]["close"])
        momentum_3 = round(
            (close - prev_close) / max(abs(prev_close), 1e-9),
            6
        )

    avg_vol = df["volume"].rolling(20).mean().iloc[-1]

    volume_ratio = round(
        float(last["volume"]) / max(float(avg_vol), 1e-9),
        6
    )

    trend_15m, trend_clarity_15m = classify_trend(df)

    signal_type = "none"

    if rejection_type == "bullish":
        signal_type = "long"

    elif rejection_type == "bearish":
        signal_type = "short"

    signal_id = f"{symbol}_{signal_tf}_{int(last['time_ms'])}"

    return {
        "signal_id": signal_id,
        "symbol": symbol,
        "signal_time_ms": int(last["time_ms"]),
        "signal_tf": signal_tf,
        "signal_type": signal_type,

        "open": round(float(last["open"]), 8),
        "high": round(float(last["high"]), 8),
        "low": round(float(last["low"]), 8),
        "close": round(close, 8),
        "volume": round(float(last["volume"]), 8),

        "ema7": round(ema7, 8),
        "ema25": round(ema25, 8),
        "ema99": round(ema99, 8),
        "rsi": round(float(last["rsi"]), 2),

        "trend_15m": trend_15m,
        "trend_clarity_15m": trend_clarity_15m,

        "rejection": rejection_type,
        "rejection_score": rejection_score,
        "candle_strength": candle_strength,

        "ema_cross": ema_cross,

        "distance_ema7": distance_ema7,
        "distance_ema25": distance_ema25,
        "distance_ema99": distance_ema99,

        "momentum_3": momentum_3,
        "volume_ratio": volume_ratio,
    }