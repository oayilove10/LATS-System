import os
import pandas as pd

MERGED_FILE = "historical_output/ALL_historical_merged.csv"


def load_data():
    if not os.path.exists(MERGED_FILE):
        print("merged file not found")
        return pd.DataFrame()

    df = pd.read_csv(MERGED_FILE)

    print(f"loaded rows={len(df)}")

    return df


# =========================================
# CONTINUATION
# =========================================
def analyze_continuation(df):
    print("\n" + "=" * 60)
    print("CONTINUATION ANALYSIS")
    print("=" * 60)

    long_df = df[df["signal_type"] == "long"]
    short_df = df[df["signal_type"] == "short"]

    if len(long_df) > 0:
        long_win = (
            (long_df["result_10"] == "win").mean() * 100
        )

        print(
            f"LONG continuation "
            f"rows={len(long_df)} "
            f"winrate={long_win:.2f}%"
        )

    if len(short_df) > 0:
        short_win = (
            (short_df["result_10"] == "win").mean() * 100
        )

        print(
            f"SHORT continuation "
            f"rows={len(short_df)} "
            f"winrate={short_win:.2f}%"
        )


# =========================================
# EXHAUSTION
# =========================================
def analyze_exhaustion(df):
    print("\n" + "=" * 60)
    print("EXHAUSTION ANALYSIS")
    print("=" * 60)

    if "momentum_3" not in df.columns:
        print("momentum_3 column not found")
        return

    strong_df = df[df["momentum_3"] > 1.5]

    if len(strong_df) == 0:
        print("no strong momentum rows")
        return

    winrate = (
        (strong_df["result_10"] == "win").mean() * 100
    )

    print(
        f"strong momentum rows={len(strong_df)} "
        f"result_10_winrate={winrate:.2f}%"
    )


# =========================================
# SIDEWAY
# =========================================
def analyze_sideway(df):
    print("\n" + "=" * 60)
    print("SIDEWAY ANALYSIS")
    print("=" * 60)

    if "trend_15m" not in df.columns:
        print("trend_15m not found")
        return

    sideway_df = df[
        df["trend_15m"].astype(str).str.contains(
            "sideway",
            case=False,
            na=False,
        )
    ]

    if len(sideway_df) == 0:
        print("no sideway rows")
        return

    winrate = (
        (sideway_df["result_10"] == "win").mean() * 100
    )

    print(
        f"sideway rows={len(sideway_df)} "
        f"result_10_winrate={winrate:.2f}%"
    )


# =========================================
# TREND ALIGNMENT
# =========================================
def analyze_mtf_alignment(df):
    print("\n" + "=" * 60)
    print("MTF ALIGNMENT")
    print("=" * 60)

    if "mtf_align" not in df.columns:
        print("mtf_align not found")
        return

    for align in df["mtf_align"].dropna().unique():

        temp = df[df["mtf_align"] == align]

        if len(temp) == 0:
            continue

        winrate = (
            (temp["result_10"] == "win").mean() * 100
        )

        print(
            f"{align} "
            f"rows={len(temp)} "
            f"winrate={winrate:.2f}%"
        )


# =========================================
# MAIN
# =========================================
def main():

    df = load_data()

    if df.empty:
        return

    analyze_continuation(df)

    analyze_exhaustion(df)

    analyze_sideway(df)

    analyze_mtf_alignment(df)


if __name__ == "__main__":
    main()