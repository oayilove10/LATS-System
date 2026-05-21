import os
import pandas as pd


MERGED_PATH = os.path.join(
    "historical_output",
    "ALL_historical_merged.csv",
)


def load_merged():
    if not os.path.isfile(MERGED_PATH):
        print(f"file not found: {MERGED_PATH}")
        return pd.DataFrame()

    df = pd.read_csv(MERGED_PATH)

    print(f"loaded rows={len(df)}")

    return df


def calc_winrate(series):
    total = len(series)

    if total == 0:
        return 0

    wins = (series == "win").sum()

    return round((wins / total) * 100, 2)


def analyze_overview(df):
    print("")
    print("=" * 60)
    print("OVERVIEW")
    print("=" * 60)

    print(f"rows={len(df)}")

    if "symbol_signal" in df.columns:
        print(
            f"symbols={df['symbol_signal'].nunique()}"
        )

    if "signal_type_signal" in df.columns:
        print(
            f"signal_types="
            f"{df['signal_type_signal'].unique()}"
        )


def analyze_result_windows(df):
    print("")
    print("=" * 60)
    print("RESULT WINDOWS")
    print("=" * 60)

    windows = [
        3,
        5,
        10,
        15,
        30,
    ]

    for window in windows:
        col = f"result_{window}"

        if col not in df.columns:
            continue

        winrate = calc_winrate(df[col])

        print(
            f"{col} "
            f"winrate={winrate}%"
        )


def analyze_signal_type(df):
    print("")
    print("=" * 60)
    print("SIGNAL TYPE")
    print("=" * 60)

    if "signal_type_signal" not in df.columns:
        return

    grouped = df.groupby(
        "signal_type_signal"
    )

    for signal_type, group in grouped:
        winrate = calc_winrate(
            group["result_10"]
        )

        print(
            f"{signal_type} "
            f"rows={len(group)} "
            f"result_10_winrate={winrate}%"
        )


def analyze_symbol(df):
    print("")
    print("=" * 60)
    print("SYMBOL ANALYSIS")
    print("=" * 60)

    if "symbol_signal" not in df.columns:
        return

    grouped = df.groupby(
        "symbol_signal"
    )

    rows = []

    for symbol, group in grouped:
        item = {
            "symbol": symbol,
            "rows": len(group),
            "result_3": calc_winrate(
                group["result_3"]
            ),
            "result_5": calc_winrate(
                group["result_5"]
            ),
            "result_10": calc_winrate(
                group["result_10"]
            ),
            "result_15": calc_winrate(
                group["result_15"]
            ),
            "result_30": calc_winrate(
                group["result_30"]
            ),
        }

        rows.append(item)

    result_df = pd.DataFrame(rows)

    result_df = result_df.sort_values(
        "result_10",
        ascending=False,
    )

    print(result_df.to_string(index=False))

    return result_df


def analyze_trend(df):
    print("")
    print("=" * 60)
    print("TREND ANALYSIS")
    print("=" * 60)

    if "trend_15m" not in df.columns:
        return

    grouped = df.groupby(
        "trend_15m"
    )

    for trend, group in grouped:
        winrate = calc_winrate(
            group["result_10"]
        )

        print(
            f"{trend} "
            f"rows={len(group)} "
            f"result_10_winrate={winrate}%"
        )


def analyze_mfe_mae(df):
    print("")
    print("=" * 60)
    print("MFE / MAE")
    print("=" * 60)

    if "mfe" not in df.columns:
        return

    avg_mfe = round(
        df["mfe"].mean(),
        4,
    )

    avg_mae = round(
        df["mae"].mean(),
        4,
    )

    print(f"avg_mfe={avg_mfe}")
    print(f"avg_mae={avg_mae}")


def save_report(lines):
    out_dir = "historical_output"

    os.makedirs(
        out_dir,
        exist_ok=True,
    )

    path = os.path.join(
        out_dir,
        "historical_analysis_report.txt",
    )

    with open(
        path,
        "w",
        encoding="utf-8",
    ) as f:
        f.write("\n".join(lines))

    print(f"saved report: {path}")


def build_text_report(df):
    lines = []

    lines.append("=" * 60)
    lines.append("LATS HISTORICAL ANALYSIS REPORT")
    lines.append("=" * 60)

    lines.append(f"rows={len(df)}")

    lines.append("")

    windows = [
        3,
        5,
        10,
        15,
        30,
    ]

    for window in windows:
        col = f"result_{window}"

        if col not in df.columns:
            continue

        winrate = calc_winrate(df[col])

        lines.append(
            f"{col} winrate={winrate}%"
        )

    lines.append("")

    if "symbol_signal" in df.columns:
        grouped = df.groupby(
            "symbol_signal"
        )

        for symbol, group in grouped:
            winrate = calc_winrate(
                group["result_10"]
            )

            lines.append(
                f"{symbol} "
                f"rows={len(group)} "
                f"result_10={winrate}%"
            )

    save_report(lines)


def main():
    df = load_merged()

    if df.empty:
        return

    analyze_overview(df)

    analyze_result_windows(df)

    analyze_signal_type(df)

    analyze_symbol(df)

    analyze_trend(df)

    analyze_mfe_mae(df)

    build_text_report(df)


if __name__ == "__main__":
    main()