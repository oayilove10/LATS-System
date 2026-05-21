import os

# =========================
# LATS HISTORICAL BACKFILL CONFIG
# TEST ONLY
# =========================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

HISTORICAL_RAW_DIR = os.path.join(
    PROJECT_ROOT,
    "historical_raw",
)

SYMBOLS = [
    "BTCUSDT",
    "ETHUSDT",
    "SOLUSDT",
    "BNBUSDT",
    "XRPUSDT",
    "ADAUSDT",
    "DOGEUSDT",
    "LINKUSDT",
    "AVAXUSDT",
    "TONUSDT",
]

TIMEFRAMES = [
    "15m",
    "1h",
    "4h",
]

# historical ถึงก่อน live_current เต็มระบบ 10 เหรียญ
START_DATE = "2025-11-12"
END_DATE = "2026-05-12"

BINANCE_KLINES_URL = "https://fapi.binance.com/fapi/v1/klines"

LIMIT = 1000
REQUEST_SLEEP = 0.2
MAX_RETRY = 3