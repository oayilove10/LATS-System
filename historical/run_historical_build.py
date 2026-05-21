from historical.config import (
    SYMBOLS,
    TIMEFRAMES,
    START_DATE,
    END_DATE,
)

from historical.historical_downloader import (
    download_historical_range,
)

from historical.historical_storage import (
    save_by_month,
)


def run_one(symbol, timeframe):
    print("")
    print("=" * 60)
    print(f"START: {symbol} {timeframe}")
    print(f"DATE RANGE: {START_DATE} -> {END_DATE}")
    print("=" * 60)

    df = download_historical_range(
        symbol=symbol,
        timeframe=timeframe,
        start_date=START_DATE,
        end_date=END_DATE,
    )

    print(
        f"DOWNLOAD DONE: {symbol} {timeframe} "
        f"rows={len(df)}"
    )

    saved_paths = save_by_month(
        df=df,
        symbol=symbol,
        timeframe=timeframe,
    )

    print(
        f"SAVE DONE: {symbol} {timeframe} "
        f"files={len(saved_paths)}"
    )

    return saved_paths


def main():
    all_files = []

    for symbol in SYMBOLS:
        for timeframe in TIMEFRAMES:
            try:
                paths = run_one(
                    symbol=symbol,
                    timeframe=timeframe,
                )

                all_files.extend(paths)

            except KeyboardInterrupt:
                print("STOP SAFE")
                raise

            except Exception as e:
                print(
                    f"[ERROR] {symbol} {timeframe} -> {e}"
                )

    print("")
    print("=" * 60)
    print("HISTORICAL BACKFILL FINISHED")
    print(f"TOTAL FILES SAVED: {len(all_files)}")
    print("=" * 60)

    for path in all_files:
        print(path)


if __name__ == "__main__":
    main()