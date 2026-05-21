from collections import Counter


def analyze_coin_personality(df):
    if df.empty:
        return {
            "symbol": "UNKNOWN",
            "sample_size": 0,
            "personality": "no_data",
        }

    symbol = df["symbol"].iloc[0] if "symbol" in df.columns else "UNKNOWN"

    behavior_counter = Counter(
        df.get("behavior_type", [])
    )

    regime_counter = Counter(
        df.get("market_regime", [])
    )

    avg_range = (
        df["range_pct"].mean()
        if "range_pct" in df.columns
        else 0
    )

    avg_volume_change = (
        df["volume_change_pct"].mean()
        if "volume_change_pct" in df.columns
        else 0
    )

    if avg_range > 3:
        personality = "high_volatility_coin"
    elif behavior_counter.get("trend_continuation_up", 0) > behavior_counter.get("sideway_compression", 0):
        personality = "trend_follow_coin"
    elif behavior_counter.get("sideway_compression", 0) > behavior_counter.get("trend_continuation_up", 0):
        personality = "sideway_coin"
    else:
        personality = "mixed_behavior_coin"

    return {
        "symbol": symbol,
        "sample_size": len(df),
        "personality": personality,
        "avg_range_pct": round(avg_range, 4),
        "avg_volume_change_pct": round(avg_volume_change, 4),
        "top_behaviors": behavior_counter.most_common(10),
        "top_regimes": regime_counter.most_common(10),
    }


if __name__ == "__main__":
    print("coin_personality_analyzer ready")