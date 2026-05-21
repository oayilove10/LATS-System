import os
import pandas as pd


HISTORICAL_OUTPUT_DIR = "historical_output"


def load_csv(path):
    if not os.path.isfile(path):
        print(f"file not found: {path}")
        return pd.DataFrame()

    return pd.read_csv(path)


def load_signal(symbol):
    path = os.path.join(
        HISTORICAL_OUTPUT_DIR,
        f"{symbol}_historical_signal_data.csv",
    )

    return load_csv(path)


def load_result(symbol):
    path = os.path.join(
        HISTORICAL_OUTPUT_DIR,
        f"{symbol}_historical_result_data.csv",
    )

    return load_csv(path)


def load_all_signals(symbols):
    frames = []

    for symbol in symbols:
        df = load_signal(symbol)

        if df.empty:
            continue

        frames.append(df)

    if not frames:
        return pd.DataFrame()

    return pd.concat(
        frames,
        ignore_index=True,
    )


def load_all_results(symbols):
    frames = []

    for symbol in symbols:
        df = load_result(symbol)

        if df.empty:
            continue

        frames.append(df)

    if not frames:
        return pd.DataFrame()

    return pd.concat(
        frames,
        ignore_index=True,
    )


def merge_signal_result(signals, results):
    if signals.empty or results.empty:
        return pd.DataFrame()

    merged = signals.merge(
        results,
        on="signal_id",
        how="inner",
        suffixes=("_signal", "_result"),
    )

    return merged


def main():
    from historical.config import SYMBOLS

    signals = load_all_signals(SYMBOLS)
    results = load_all_results(SYMBOLS)

    print("=" * 60)
    print("HISTORICAL LOADER SUMMARY")
    print("=" * 60)

    print(f"signals rows: {len(signals)}")
    print(f"results rows: {len(results)}")

    merged = merge_signal_result(
        signals,
        results,
    )

    print(f"merged rows: {len(merged)}")

    out_dir = "historical_output"
    os.makedirs(out_dir, exist_ok=True)

    merged_path = os.path.join(
        out_dir,
        "ALL_historical_merged.csv",
    )

    merged.to_csv(
        merged_path,
        index=False,
        encoding="utf-8",
    )

    print(f"saved merged: {merged_path}")


if __name__ == "__main__":
    main()