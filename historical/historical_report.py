import os
from datetime import datetime

from historical.config import REPORT_DIR


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def write_report(filename, lines):
    ensure_dir(REPORT_DIR)

    path = os.path.join(REPORT_DIR, filename)

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return path


def build_compare_report(symbol, timeframe, summary, similar_df):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = []

    lines.append("LATS HISTORICAL COMPARE REPORT")
    lines.append("=" * 50)
    lines.append(f"Generated At: {now}")
    lines.append(f"Symbol: {symbol}")
    lines.append(f"Timeframe: {timeframe}")

    lines.append("")
    lines.append("=" * 50)
    lines.append("SUMMARY")
    lines.append("=" * 50)

    for key, value in summary.items():
        lines.append(f"{key}: {value}")

    lines.append("")
    lines.append("=" * 50)
    lines.append("TOP SIMILAR CASES")
    lines.append("=" * 50)

    if similar_df.empty:
        lines.append("No similar cases found")
    else:
        for _, row in similar_df.head(20).iterrows():
            lines.append(
                f"score={row.get('similarity_score')} | "
                f"time={row.get('open_time_text')} | "
                f"regime={row.get('market_regime')} | "
                f"behavior={row.get('behavior_type')} | "
                f"return={row.get('return_pct')}"
            )

    filename = f"{symbol}_{timeframe}_historical_compare.txt"

    return write_report(filename, lines)


if __name__ == "__main__":
    print("historical_report ready")