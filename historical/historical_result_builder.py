import os
import pandas as pd

from historical.config import SYMBOLS
from historical.historical_signal_builder import load_raw_months


RESULT_WINDOWS = [
    3,
    5,
    10,
    15,
    30,
]


def calculate_result(signal_type, entry_price, future_df):
    if future_df.empty:
        return "EMPTY", 0, 0

    highs = future_df["high"]
    lows = future_df["low"]

    max_high = highs.max()
    min_low = lows.min()

    if signal_type == "long":
        mfe = (
            (max_high - entry_price)
            / entry_price
        ) * 100

        mae = (
            (min_low - entry_price)
            / entry_price
        ) * 100

        if mfe > abs(mae):
            result = "win"
        else:
            result = "loss"

        return result, mfe, mae

    if signal_type == "short":
        mfe = (
            (entry_price - min_low)
            / entry_price
        ) * 100

        mae = (
            (entry_price - max_high)
            / entry_price
        ) * 100

        if mfe > abs(mae):
            result = "win"
        else:
            result = "loss"

        return result, mfe, mae

    return "EMPTY", 0, 0


def build_historical_results(symbol, timeframe="15m"):
    signal_path = os.path.join(
        "historical_output",
        f"{symbol}_historical_signal_data.csv",
    )

    if not os.path.isfile(signal_path):
        print(f"signal file not found: {signal_path}")
        return pd.DataFrame()

    signals = pd.read_csv(signal_path)

    raw = load_raw_months(
        symbol=symbol,
        timeframe=timeframe,
    )

    if raw.empty:
        return pd.DataFrame()

    raw = raw.sort_values(
        "open_time"
    ).reset_index(drop=True)

    time_to_index = {
        int(row["open_time"]): i
        for i, row in raw.iterrows()
    }

    results = []

    for _, signal in signals.iterrows():
        signal_time = int(signal["signal_time_ms"])
        signal_type = signal["signal_type"]
        entry_price = float(signal["close"])

        idx = time_to_index.get(signal_time)

        if idx is None:
            continue

        result_row = {
            "signal_id": signal["signal_id"],
            "symbol": signal["symbol"],
            "signal_time": signal["signal_time"],
            "signal_type": signal_type,
            "entry_price": entry_price,
            "status": "done",
        }

        best_mfe = 0
        worst_mae = 0

        for window in RESULT_WINDOWS:
            future_df = raw.iloc[
                idx + 1: idx + 1 + window
            ]

            result, mfe, mae = calculate_result(
                signal_type=signal_type,
                entry_price=entry_price,
                future_df=future_df,
            )

            result_row[f"result_{window}"] = result
            result_row[f"mfe_{window}"] = mfe
            result_row[f"mae_{window}"] = mae

            if mfe > best_mfe:
                best_mfe = mfe

            if mae < worst_mae:
                worst_mae = mae

        result_row["mfe"] = best_mfe
        result_row["mae"] = worst_mae

        results.append(result_row)

    return pd.DataFrame(results)


def save_historical_results(symbol, timeframe="15m"):
    out_dir = os.path.join(
        "historical_output"
    )

    os.makedirs(
        out_dir,
        exist_ok=True,
    )

    results = build_historical_results(
        symbol=symbol,
        timeframe=timeframe,
    )

    path = os.path.join(
        out_dir,
        f"{symbol}_historical_result_data.csv",
    )

    results.to_csv(
        path,
        index=False,
        encoding="utf-8",
    )

    print(
        f"saved historical results: {path}"
    )

    print(
        f"rows={len(results)}"
    )

    return path


def main():
    for symbol in SYMBOLS:
        try:
            print("=" * 60)
            print(f"BUILD RESULT: {symbol}")
            print("=" * 60)

            save_historical_results(
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