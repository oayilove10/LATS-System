import os
import sys
import time
from datetime import datetime

BOT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BOT_DIR)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from utils.config import (
    SYMBOLS,
    TIMEFRAMES,
    LIMIT_SIGNAL,
    LIMIT_CONTEXT,
    SLEEP_SECONDS,
)

from core.fetcher import fetch_multi_timeframe
from core.indicators import build_feature_row
from core.context_builder import build_context
from core.result_checker import update_pending_results
from utils.logger import save_signal, save_pending_result


def process_symbol(symbol, btc_data):
    symbol_data = fetch_multi_timeframe(
        symbol=symbol,
        timeframes=TIMEFRAMES,
        limit_signal=LIMIT_SIGNAL,
        limit_context=LIMIT_CONTEXT,
    )

    if not symbol_data:
        print(f"{symbol} no data")
        return

    feature = build_feature_row(
        symbol=symbol,
        signal_tf=TIMEFRAMES["signal"],
        klines=symbol_data["signal"],
    )

    if feature is None:
        print(f"{symbol} no feature")
        return

    try:
        context = build_context(
            symbol_data=symbol_data,
            btc_data=btc_data,
        )
        feature.update(context)
    except Exception as e:
        print(f"{symbol} context error -> {e}")
        return

    save_signal(feature)
    save_pending_result(feature)


def main():
    print("BOT STARTED: FUTURES DATA COLLECTION")
    print("MODE: 15m signal / 1h+4h context / no filter")
    print("RESULT CHECKER: ON")

    while True:
        try:
            print(f"\n===== RUN {datetime.now()} =====")

            btc_data = fetch_multi_timeframe(
                symbol="BTCUSDT",
                timeframes=TIMEFRAMES,
                limit_signal=LIMIT_SIGNAL,
                limit_context=LIMIT_CONTEXT,
            )

            for symbol in SYMBOLS:
                try:
                    process_symbol(symbol, btc_data)
                    time.sleep(1)

                except KeyboardInterrupt:
                    print("STOP SAFE")
                    raise

                except Exception as e:
                    print(f"{symbol} process error -> {e}")

            # เช็ก pending → done
            try:
                update_pending_results()
            except Exception as e:
                print(f"result checker error -> {e}")

            print(f"sleep {SLEEP_SECONDS} sec")
            time.sleep(SLEEP_SECONDS)

        except KeyboardInterrupt:
            print("BOT STOPPED")
            break

        except Exception as e:
            print(f"[CRITICAL] {e}")
            time.sleep(5)


if __name__ == "__main__":
    main()