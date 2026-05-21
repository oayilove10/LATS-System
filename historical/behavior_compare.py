from historical.historical_downloader import download_historical_range
from historical.historical_storage import save_by_month
from historical.historical_loader import load_range
from historical.market_library_builder import (
    build_market_library,
    save_market_library,
)
from historical.coin_personality_analyzer import analyze_coin_personality


def run_download(symbol, timeframe, start_date, end_date):

    df = download_historical_range(
        symbol=symbol,
        timeframe=timeframe,
        start_date=start_date,
        end_date=end_date,
    )

    paths = save_by_month(
        df=df,
        symbol=symbol,
        timeframe=timeframe,
    )

    print(f"{symbol} {timeframe} saved:")

    for path in paths:
        print(path)


def run_library_build(symbol, timeframe):

    df = load_range(
        symbol=symbol,
        timeframe=timeframe,
    )

    library_df = build_market_library(
        df=df,
        symbol=symbol,
        timeframe=timeframe,
    )

    path = save_market_library(
        library_df=library_df,
        symbol=symbol,
        timeframe=timeframe,
    )

    print(f"library saved: {path}")

    personality = analyze_coin_personality(
        library_df
    )

    print(personality)


if __name__ == "__main__":

    run_download(
        symbol="BTCUSDT",
        timeframe="15m",
        start_date="2024-01-01",
        end_date="2024-02-01",
    )

    run_library_build(
        symbol="BTCUSDT",
        timeframe="15m",
    )