from core.indicators import klines_to_df, classify_trend


def calc_mtf_align(trend_1h, trend_4h):
    t1 = str(trend_1h).replace("strong_", "")
    t4 = str(trend_4h).replace("strong_", "")

    if t1 == "up" and t4 == "up":
        return "same_up"
    if t1 == "down" and t4 == "down":
        return "same_down"
    if "sideway" in [t1, t4]:
        return "weak"

    return "conflict"


def calc_zone(close, high, low):
    close = float(close)
    high = float(high)
    low = float(low)

    dist_high = abs(high - close) / max(close, 1e-9)
    dist_low = abs(close - low) / max(close, 1e-9)

    if dist_high < dist_low:
        zone = "resistance"
        dist = dist_high
    else:
        zone = "support"
        dist = dist_low

    if dist > 0.01:
        zone = "middle"

    return zone, round(dist, 6)


def calc_coin_behavior(symbol_trend_1h, btc_trend_1h):
    s = str(symbol_trend_1h).replace("strong_", "")
    b = str(btc_trend_1h).replace("strong_", "")

    if s == b and s in ["up", "down"]:
        return "follow_btc"

    if s in ["up", "down"] and b in ["up", "down"] and s != b:
        return "against_btc"

    return "neutral"


def build_context(symbol_data, btc_data):
    signal_df = klines_to_df(symbol_data["signal"])
    signal_df = signal_df.iloc[:-1].copy()

    df_1h = klines_to_df(symbol_data["trend_1h"])
    df_4h = klines_to_df(symbol_data["trend_4h"])
    btc_1h = klines_to_df(btc_data["trend_1h"])
    btc_4h = klines_to_df(btc_data["trend_4h"])

    trend_1h, trend_clarity_1h = classify_trend(df_1h)
    trend_4h, trend_clarity_4h = classify_trend(df_4h)

    btc_trend_1h, _ = classify_trend(btc_1h)
    btc_trend_4h, _ = classify_trend(btc_4h)

    last_close = float(signal_df.iloc[-1]["close"])
    swing_high = float(signal_df["high"].tail(50).max())
    swing_low = float(signal_df["low"].tail(50).min())

    zone, dist_to_sr = calc_zone(last_close, swing_high, swing_low)

    mtf_align = calc_mtf_align(trend_1h, trend_4h)
    coin_behavior = calc_coin_behavior(trend_1h, btc_trend_1h)

    return {
        "trend_1h": trend_1h,
        "trend_4h": trend_4h,
        "trend_clarity_1h": trend_clarity_1h,
        "trend_clarity_4h": trend_clarity_4h,
        "mtf_align": mtf_align,

        "zone": zone,
        "dist_to_sr": dist_to_sr,

        "btc_trend_1h": btc_trend_1h,
        "btc_trend_4h": btc_trend_4h,
        "coin_behavior": coin_behavior,
    }