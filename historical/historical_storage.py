import os

import pandas as pd

from historical.config import HISTORICAL_RAW_DIR


def ensure_dir(path):
    os.makedirs(
        path,
        exist_ok=True,
    )


def get_month_text(open_time_ms):
    dt = pd.to_datetime(
        open_time_ms,
        unit="ms",
        utc=True,
    )

    return dt.strftime("%Y-%m")


def get_save_path(symbol, timeframe, month_text):
    folder = os.path.join(
        HISTORICAL_RAW_DIR,
        symbol,
        timeframe,
    )

    ensure_dir(folder)

    filename = f"{month_text}.csv"

    return os.path.join(
        folder,
        filename,
    )


def save_by_month(df, symbol, timeframe):
    if df.empty:
        print(
            f"{symbol} {timeframe} "
            f"no data to save"
        )

        return []

    df = df.copy()

    df["month"] = df["open_time"].apply(
        get_month_text
    )

    saved_paths = []

    for month_text, month_df in df.groupby("month"):
        path = get_save_path(
            symbol=symbol,
            timeframe=timeframe,
            month_text=month_text,
        )

        month_df = month_df.drop(
            columns=["month"]
        )

        month_df.to_csv(
            path,
            index=False,
            encoding="utf-8",
        )

        saved_paths.append(path)

        print(
            f"saved {symbol} {timeframe} "
            f"{month_text} "
            f"rows={len(month_df)} -> {path}"
        )

    return saved_paths