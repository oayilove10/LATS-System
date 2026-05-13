import csv
from datetime import datetime

from core.fetcher import fetch_klines
from utils.config import TIMEFRAMES
from utils.logger import RESULT_FILE, RESULT_HEADER


RESULT_WINDOWS = [3, 5, 10, 15, 30]

# Phase 2.1 temporary result rules
# win  = price moved in favor >= 0.5%
# loss = price moved against >= 0.3%
WIN_PCT = 0.5
LOSS_PCT = 0.3

# Allow timestamp matching tolerance
# 60 seconds = safe for 15m candle timestamp matching
TIME_MATCH_TOLERANCE_MS = 60_000


def now_text():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def safe_float(value, default=0.0):
    try:
        if value in ["", None]:
            return default
        return float(value)
    except Exception:
        return default


def safe_int(value, default=0):
    try:
        if value in ["", None]:
            return default
        return int(float(value))
    except Exception:
        return default


def read_result_rows():
    try:
        with open(RESULT_FILE, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return list(reader)
    except FileNotFoundError:
        return []


def write_result_rows(rows):
    with open(RESULT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=RESULT_HEADER)
        writer.writeheader()
        writer.writerows(rows)


def find_signal_index(klines, signal_time_ms):
    """
    Find the candle index that matches signal_time_ms.

    We allow a small tolerance because CSV/Excel formatting or timestamp
    conversion may cause tiny differences.
    """
    for i, k in enumerate(klines):
        kline_time = safe_int(k[0])

        if abs(kline_time - signal_time_ms) <= TIME_MATCH_TOLERANCE_MS:
            return i

    return None


def calc_result(signal_type, entry_price, future_klines):
    if not future_klines or entry_price <= 0:
        return "neutral", 0.0, 0.0

    highs = [safe_float(k[2]) for k in future_klines]
    lows = [safe_float(k[3]) for k in future_klines]

    max_high = max(highs)
    min_low = min(lows)

    if signal_type == "long":
        mfe = ((max_high - entry_price) / entry_price) * 100
        mae = ((entry_price - min_low) / entry_price) * 100

    elif signal_type == "short":
        mfe = ((entry_price - min_low) / entry_price) * 100
        mae = ((max_high - entry_price) / entry_price) * 100

    else:
        mfe = 0.0
        mae = 0.0

    mfe = round(mfe, 4)
    mae = round(mae, 4)

    if mfe >= WIN_PCT:
        result = "win"
    elif mae >= LOSS_PCT:
        result = "loss"
    else:
        result = "neutral"

    return result, mfe, mae


def update_pending_results():
    rows = read_result_rows()

    if not rows:
        print("no result rows")
        return

    updated_count = 0
    pending_count = 0
    not_ready_count = 0
    not_found_count = 0

    for row in rows:
        if row.get("status") != "pending":
            continue

        pending_count += 1

        symbol = row.get("symbol", "")
        signal_time_ms = safe_int(row.get("signal_time_ms"))
        signal_type = row.get("signal_type", "")
        entry_price = safe_float(row.get("entry_price"))

        if not symbol or signal_time_ms <= 0:
            continue

        klines = fetch_klines(
            symbol=symbol,
            interval=TIMEFRAMES["signal"],
            limit=250,
        )

        if not klines:
            continue

        signal_index = find_signal_index(
            klines=klines,
            signal_time_ms=signal_time_ms,
        )

        if signal_index is None:
            not_found_count += 1
            continue

        max_window = max(RESULT_WINDOWS)

        # Need enough future candles after signal candle
        if len(klines) <= signal_index + max_window:
            not_ready_count += 1
            continue

        for window in RESULT_WINDOWS:
            future_klines = klines[
                signal_index + 1:
                signal_index + 1 + window
            ]

            result, mfe, mae = calc_result(
                signal_type=signal_type,
                entry_price=entry_price,
                future_klines=future_klines,
            )

            row[f"result_{window}"] = result
            row[f"mfe_{window}"] = mfe
            row[f"mae_{window}"] = mae

        row["status"] = "done"
        row["checked_at"] = now_text()

        updated_count += 1

    if updated_count > 0:
        write_result_rows(rows)

    print(
        "result checker -> "
        f"pending:{pending_count} "
        f"updated:{updated_count} "
        f"not_ready:{not_ready_count} "
        f"not_found:{not_found_count}"
    )