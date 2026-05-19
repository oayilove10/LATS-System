import os
import sys
import time
from datetime import datetime

# =========================
# PATH
# =========================

BOT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BOT_DIR)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# =========================
# CONFIG
# =========================

from utils.config import (
    SYMBOLS,
    TIMEFRAMES,
    LIMIT_SIGNAL,
    LIMIT_CONTEXT,
    SLEEP_SECONDS,
)

# =========================
# CORE
# =========================

from core.fetcher import fetch_multi_timeframe
from core.indicators import build_feature_row
from core.context_builder import build_context
from core.result_checker import update_pending_results

# =========================
# LOGGER
# =========================

from utils.logger import (
    save_signal,
    save_pending_result,
)

# =========================
# RUNTIME GUARD
# =========================

from core.runtime_guard import (
    startup_banner,
    check_internet,
    check_binance_api,
    check_collector_running,
    check_fetch_retry,
    check_signal_health,
)

# =========================
# GLOBAL
# =========================

retry_count = 0

# =========================
# PROCESS SYMBOL
# =========================


def process_symbol(symbol, btc_data):

    global retry_count

    symbol_data = fetch_multi_timeframe(
        symbol=symbol,
        timeframes=TIMEFRAMES,
        limit_signal=LIMIT_SIGNAL,
        limit_context=LIMIT_CONTEXT,
    )

    # =========================
    # DATA CHECK
    # =========================

    if not symbol_data:

        retry_count += 1

        check_fetch_retry(retry_count)

        print(f"{symbol} no data")

        return

    # reset retry
    retry_count = 0

    # =========================
    # FEATURE
    # =========================

    feature = build_feature_row(
        symbol=symbol,
        signal_tf=TIMEFRAMES["signal"],
        klines=symbol_data["signal"],
    )

    if feature is None:
        print(f"{symbol} no feature")
        return

    # =========================
    # CONTEXT
    # =========================

    try:

        context = build_context(
            symbol_data=symbol_data,
            btc_data=btc_data,
        )

        feature.update(context)

    except Exception as e:

        print(f"{symbol} context error -> {e}")

        return

    # =========================
    # SAVE
    # =========================

    save_signal(feature)

    save_pending_result(feature)

    print(
        f"{symbol} saved | "
        f"type={feature.get('signal_type')} | "
        f"trend_4h={feature.get('trend_4h')} | "
        f"zone={feature.get('zone')}"
    )


# =========================
# MAIN
# =========================


def main():

    # =========================
    # STARTUP
    # =========================

    startup_banner()

    check_internet(True)

    check_binance_api(True)

    check_collector_running(True)

    # =========================
    # INFO
    # =========================

    print("BOT STARTED: FUTURES DATA COLLECTION")

    print(
        "MODE: "
        "15m signal / "
        "1h+4h context / "
        "no filter"
    )

    print("RESULT CHECKER: ON")

    # =========================
    # LOOP
    # =========================

    while True:

        try:

            print(
                f"\n===== RUN "
                f"{datetime.now()} ====="
            )

            # =========================
            # BTC CONTEXT
            # =========================

            btc_data = fetch_multi_timeframe(
                symbol="BTCUSDT",
                timeframes=TIMEFRAMES,
                limit_signal=LIMIT_SIGNAL,
                limit_context=LIMIT_CONTEXT,
            )

            if not btc_data:

                print("BTCUSDT no data")

                time.sleep(5)

                continue

            # =========================
            # SYMBOL LOOP
            # =========================

            for symbol in SYMBOLS:

                try:

                    process_symbol(
                        symbol,
                        btc_data
                    )

                    time.sleep(1)

                except KeyboardInterrupt:

                    print("STOP SAFE")

                    raise

                except Exception as e:

                    print(
                        f"{symbol} "
                        f"process error -> {e}"
                    )

            # =========================
            # UPDATE RESULT
            # =========================

            try:

                update_pending_results()

            except Exception as e:

                print(
                    f"result checker error -> {e}"
                )

            # =========================
            # HEALTH
            # =========================

            try:

                signal_rows = 1
                result_rows = 1

                check_signal_health(
                    signal_rows,
                    result_rows
                )

            except Exception as e:

                print(
                    f"health check error -> {e}"
                )

            # =========================
            # SLEEP
            # =========================

            print(
                f"sleep "
                f"{SLEEP_SECONDS} sec"
            )

            time.sleep(SLEEP_SECONDS)

        except KeyboardInterrupt:

            print("BOT STOPPED")

            break

        except Exception as e:

            print(f"[CRITICAL] {e}")

            time.sleep(5)


# =========================
# START
# =========================

if __name__ == "__main__":
    main()