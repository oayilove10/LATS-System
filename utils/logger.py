import csv
import os
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "bot", "data")

os.makedirs(DATA_DIR, exist_ok=True)

SIGNAL_FILE = os.path.join(DATA_DIR, "signal_data.csv")
RESULT_FILE = os.path.join(DATA_DIR, "result_data.csv")


SIGNAL_HEADER = [
    "signal_id",
    "symbol",
    "signal_time_ms",
    "signal_time_text",
    "signal_tf",
    "signal_type",

    "open",
    "high",
    "low",
    "close",
    "volume",

    "ema7",
    "ema25",
    "ema99",
    "rsi",

    "trend_15m",
    "trend_1h",
    "trend_4h",

    "trend_clarity_15m",
    "trend_clarity_1h",
    "trend_clarity_4h",

    "mtf_align",
    "zone",
    "dist_to_sr",

    "rejection",
    "rejection_score",
    "candle_strength",

    "volume_ratio",
    "momentum_3",

    "distance_ema7",
    "distance_ema25",

    "ema_cross",

    "btc_trend_1h",
    "btc_trend_4h",
    "coin_behavior",

    "logged_at",

    # NEW FIELD → ต่อท้ายสุด
    "distance_ema99",
]


RESULT_HEADER = [
    "signal_id",
    "symbol",
    "signal_time_ms",
    "signal_time_text",
    "signal_tf",
    "signal_type",
    "entry_price",

    "status",
    "checked_at",

    "result_3",
    "result_5",
    "result_10",
    "result_15",
    "result_30",

    "mfe_3",
    "mfe_5",
    "mfe_10",
    "mfe_15",
    "mfe_30",

    "mae_3",
    "mae_5",
    "mae_10",
    "mae_15",
    "mae_30",
]


def now_text():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def ms_to_time_text(ms):
    try:
        if ms in ["", None]:
            return ""

        ms = int(float(ms))

        return datetime.fromtimestamp(
            ms / 1000
        ).strftime("%Y-%m-%d %H:%M:%S")

    except Exception:
        return ""


def ensure_file(path, header):
    if not os.path.isfile(path) or os.path.getsize(path) == 0:
        with open(path, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(header)


def exists(path, signal_id):
    if not os.path.isfile(path):
        return False

    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            if row.get("signal_id") == signal_id:
                return True

    return False


def safe_append(path, header, data):
    ensure_file(path, header)

    row = [data.get(h, "") for h in header]

    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(row)

        f.flush()
        os.fsync(f.fileno())


def save_signal(feature):
    sid = feature.get("signal_id")

    if not sid:
        return

    if exists(SIGNAL_FILE, sid):
        print(f"skip duplicate signal: {sid}")
        return

    data = dict(feature)

    if not data.get("signal_time_text"):
        data["signal_time_text"] = ms_to_time_text(
            data.get("signal_time_ms")
        )

    data["logged_at"] = now_text()

    safe_append(
        SIGNAL_FILE,
        SIGNAL_HEADER,
        data
    )

    print(f"saved signal: {sid}")


def save_pending_result(feature):
    sid = feature.get("signal_id")

    if not sid:
        return

    if exists(RESULT_FILE, sid):
        print(f"skip duplicate result: {sid}")
        return

    data = {
        "signal_id": sid,
        "symbol": feature.get("symbol", ""),

        "signal_time_ms": feature.get(
            "signal_time_ms", ""
        ),

        "signal_time_text": feature.get(
            "signal_time_text", ""
        ) or ms_to_time_text(
            feature.get("signal_time_ms")
        ),

        "signal_tf": feature.get("signal_tf", ""),
        "signal_type": feature.get("signal_type", ""),

        "entry_price": feature.get("close", ""),

        "status": "pending",
        "checked_at": "",
    }

    safe_append(
        RESULT_FILE,
        RESULT_HEADER,
        data
    )

    print(f"saved result pending: {sid}")