# core/runtime_guard.py

import os
from datetime import datetime

# =========================
# PATH
# =========================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

LOG_DIR = os.path.join(BASE_DIR, "logs")

os.makedirs(LOG_DIR, exist_ok=True)

# =========================
# LOG FILES
# =========================

RUNTIME_LOG = os.path.join(
    LOG_DIR,
    "runtime_guard.log"
)

ERROR_LOG = os.path.join(
    LOG_DIR,
    "error.log"
)

FETCH_RETRY_LOG = os.path.join(
    LOG_DIR,
    "fetch_retry.log"
)

DATA_GAP_LOG = os.path.join(
    LOG_DIR,
    "data_gap.log"
)

# =========================
# CONFIG
# =========================

MAX_FETCH_RETRY = 5
MAX_GAP_MINUTES = 60

# =========================
# INTERNAL
# =========================


def get_now_text():
    return datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )


def write_log(path, level, message):

    now = get_now_text()

    line = f"[{now}] [{level}] {message}"

    print(line)

    with open(
        path,
        "a",
        encoding="utf-8"
    ) as f:

        f.write(line + "\n")


# =========================
# BASIC LOG
# =========================


def ok(message):

    write_log(
        RUNTIME_LOG,
        "OK",
        message
    )


def warn(message):

    write_log(
        RUNTIME_LOG,
        "WARN",
        message
    )


def error(message):

    write_log(
        ERROR_LOG,
        "ERROR",
        message
    )


# =========================
# INTERNET/API
# =========================


def check_internet(is_ok=True):

    if is_ok:
        ok("Internet")
        return True

    error("Internet Failed")
    return False


def check_binance_api(is_ok=True):

    if is_ok:
        ok("Binance API")
        return True

    error("Binance API Failed")
    return False


# =========================
# COLLECTOR
# =========================


def check_collector_running(is_running=True):

    if is_running:

        ok("Collector Running")
        return True

    error("Collector Not Running")
    return False


# =========================
# FETCH RETRY
# =========================


def check_fetch_retry(
    retry_count,
    limit=MAX_FETCH_RETRY
):

    if retry_count >= limit:

        message = (
            f"Fetch Retry High | "
            f"retry_count={retry_count}"
        )

        warn(message)

        write_log(
            FETCH_RETRY_LOG,
            "WARN",
            message
        )

        return False

    ok(
        f"Fetch Retry Normal | "
        f"retry_count={retry_count}"
    )

    return True


# =========================
# DATA GAP
# =========================


def check_data_gap(
    gap_minutes,
    limit=MAX_GAP_MINUTES
):

    if gap_minutes >= limit:

        message = (
            f"Data Gap Detected | "
            f"gap_minutes={gap_minutes:.2f}"
        )

        error(message)

        write_log(
            DATA_GAP_LOG,
            "ERROR",
            message
        )

        return False

    ok(
        f"No Data Gap | "
        f"gap_minutes={gap_minutes:.2f}"
    )

    return True


# =========================
# MISSING CANDLE
# =========================


def check_missing_candle(
    missing_count
):

    if missing_count > 0:

        warn(
            f"Missing Candle | "
            f"missing_count={missing_count}"
        )

        return False

    ok("No Missing Candle")

    return True


# =========================
# SIGNAL HEALTH
# =========================


def check_signal_health(
    signal_rows,
    result_rows
):

    if signal_rows <= 0:

        error(
            "Signal rows empty"
        )

        return False

    diff = abs(
        signal_rows - result_rows
    )

    if diff > 100:

        warn(
            f"Signal/Result mismatch | "
            f"signal_rows={signal_rows} | "
            f"result_rows={result_rows}"
        )

        return False

    ok(
        f"Signal Health OK | "
        f"signal_rows={signal_rows} | "
        f"result_rows={result_rows}"
    )

    return True


# =========================
# STARTUP
# =========================


def startup_banner():

    print("\n")
    print("=" * 60)
    print("LATS Runtime Guard")
    print("=" * 60)
    print(
        f"Started At: "
        f"{get_now_text()}"
    )
    print("=" * 60)
    print("\n")