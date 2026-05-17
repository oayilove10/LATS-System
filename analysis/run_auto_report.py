import os
import csv
from datetime import datetime
from collections import Counter, defaultdict

# =========================
# LATS AUTO ANALYSIS REPORT V6
# 1 run = 1 folder
# include context-aware signal chain quality
# =========================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "bot", "data")

SIGNAL_FILE = os.path.join(DATA_DIR, "signal_data.csv")
RESULT_FILE = os.path.join(DATA_DIR, "result_data.csv")

RUN_TIME = datetime.now()
RUN_DATE = RUN_TIME.strftime("%Y-%m-%d")
RUN_TIME_TEXT = RUN_TIME.strftime("%H%M")
RUN_STAMP = RUN_TIME.strftime("%Y-%m-%d_%H%M")

RUN_FOLDER_NAME = f"weekly-{RUN_DATE}-{RUN_TIME_TEXT}"

OUT_ROOT = os.path.join(BASE_DIR, "analysis", "outputs", RUN_FOLDER_NAME)
DAILY_DIR = os.path.join(OUT_ROOT, "daily", RUN_STAMP)
COMPARE_DIR = os.path.join(OUT_ROOT, "compare")
SUMMARY_DIR = os.path.join(OUT_ROOT, "summary")

os.makedirs(DAILY_DIR, exist_ok=True)
os.makedirs(COMPARE_DIR, exist_ok=True)
os.makedirs(SUMMARY_DIR, exist_ok=True)


def read_csv(path):
    if not os.path.isfile(path):
        print(f"WARNING: file not found: {path}")
        return []

    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_txt(folder, filename, lines):
    path = os.path.join(folder, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def count_by(rows, field):
    counter = Counter()
    for row in rows:
        value = row.get(field, "") or "EMPTY"
        counter[value] += 1
    return counter


def count_status(results, status_name):
    return sum(
        1 for r in results
        if r.get("status", "").lower() == status_name
    )


def section(title):
    return ["", "=" * 50, title, "=" * 50]


def safe_int(value):
    try:
        if value in ["", None]:
            return None
        return int(float(value))
    except Exception:
        return None


def get_result_value(result_row, field):
    if not result_row:
        return "EMPTY"
    return result_row.get(field, "") or "EMPTY"


def calc_winrate(records, result_field):
    counter = Counter(r.get(result_field, "EMPTY") or "EMPTY" for r in records)

    win = counter.get("win", 0)
    loss = counter.get("loss", 0)
    empty = counter.get("EMPTY", 0)
    total = win + loss

    if total > 0:
        winrate = (win / total) * 100
    else:
        winrate = None

    return win, loss, empty, total, winrate


def report_overview(signals, results):
    done_rows = count_status(results, "done")
    pending_rows = count_status(results, "pending")

    lines = []
    lines.append("LATS AUTO ANALYSIS REPORT")
    lines.append("REPORT: 01 OVERVIEW")
    lines.append(f"DATE: {RUN_DATE}")
    lines.append(f"GENERATED_AT: {RUN_TIME}")
    lines.append("=" * 50)
    lines.append(f"Total signal rows: {len(signals)}")
    lines.append(f"Total result rows: {len(results)}")
    lines.append(f"Done result rows: {done_rows}")
    lines.append(f"Pending result rows: {pending_rows}")

    lines += section("RESULT STATUS")
    for k, v in count_by(results, "status").most_common():
        lines.append(f"{k}: {v}")

    lines += section("SIGNAL TYPE")
    for k, v in count_by(signals, "signal_type").most_common():
        lines.append(f"{k}: {v}")

    lines += section("MTF ALIGN")
    for k, v in count_by(signals, "mtf_align").most_common():
        lines.append(f"{k}: {v}")

    lines += section("ZONE")
    for k, v in count_by(signals, "zone").most_common():
        lines.append(f"{k}: {v}")

    write_txt(DAILY_DIR, "01_overview.txt", lines)


def report_coin_summary(signals):
    lines = []
    lines.append("LATS AUTO ANALYSIS REPORT")
    lines.append("REPORT: 02 COIN SUMMARY")
    lines.append(f"DATE: {RUN_DATE}")
    lines.append("=" * 50)

    lines += section("SIGNAL COUNT BY COIN")
    for k, v in count_by(signals, "symbol").most_common():
        lines.append(f"{k}: {v}")

    lines += section("COIN BEHAVIOR")
    for k, v in count_by(signals, "coin_behavior").most_common():
        lines.append(f"{k}: {v}")

    write_txt(DAILY_DIR, "02_coin_summary.txt", lines)


def report_trend_summary(signals):
    lines = []
    lines.append("LATS AUTO ANALYSIS REPORT")
    lines.append("REPORT: 03 TREND SUMMARY")
    lines.append(f"DATE: {RUN_DATE}")
    lines.append("=" * 50)

    trend_fields = [
        "trend_15m",
        "trend_1h",
        "trend_4h",
        "trend_clarity_15m",
        "trend_clarity_1h",
        "trend_clarity_4h",
    ]

    for field in trend_fields:
        lines += section(field.upper())
        for k, v in count_by(signals, field).most_common():
            lines.append(f"{k}: {v}")

    write_txt(DAILY_DIR, "03_trend_summary.txt", lines)


def report_behavior_summary(signals):
    lines = []
    lines.append("LATS AUTO ANALYSIS REPORT")
    lines.append("REPORT: 04 BEHAVIOR SUMMARY")
    lines.append(f"DATE: {RUN_DATE}")
    lines.append("=" * 50)

    fields = [
        "rejection",
        "ema_cross",
        "zone",
        "mtf_align",
        "coin_behavior",
        "btc_trend_1h",
        "btc_trend_4h",
    ]

    for field in fields:
        lines += section(field.upper())
        for k, v in count_by(signals, field).most_common():
            lines.append(f"{k}: {v}")

    write_txt(DAILY_DIR, "04_behavior_summary.txt", lines)


def report_warning_checklist(signals, results):
    done_rows = count_status(results, "done")
    pending_rows = count_status(results, "pending")
    conflict_rows = sum(
        1 for s in signals
        if s.get("mtf_align") == "conflict"
    )

    lines = []
    lines.append("LATS AUTO ANALYSIS REPORT")
    lines.append("REPORT: 05 WARNING CHECKLIST")
    lines.append(f"DATE: {RUN_DATE}")
    lines.append("=" * 50)

    lines.append(f"Done result rows: {done_rows}")
    lines.append(f"Pending result rows: {pending_rows}")
    lines.append(f"MTF conflict signal rows: {conflict_rows}")

    if len(results) != len(signals):
        lines.append(
            f"WARNING: result rows ({len(results)}) "
            f"!= signal rows ({len(signals)})"
        )

    lines += section("THINGS TO CHECK")
    lines.append("- Check if pending result rows are growing too much")
    lines.append("- Check if one coin dominates too much")
    lines.append("- Check if MTF conflict increases")
    lines.append("- Check if coin_behavior changes")
    lines.append("- Check if high score / strong trend starts failing later")
    lines.append("- Check if repeated behavior is becoming too duplicated")

    write_txt(DAILY_DIR, "05_warning_checklist.txt", lines)


def report_winrate_by_window(results):
    lines = []
    lines.append("LATS AUTO ANALYSIS REPORT")
    lines.append("REPORT: 06 WINRATE BY RESULT WINDOW")
    lines.append(f"DATE: {RUN_DATE}")
    lines.append("=" * 50)

    windows = [
        "result_3",
        "result_5",
        "result_10",
        "result_15",
        "result_30",
    ]

    done_rows = [
        r for r in results
        if r.get("status", "").lower() == "done"
    ]

    lines.append(f"Done rows used: {len(done_rows)}")

    for field in windows:
        lines += section(field.upper())

        counter = count_by(done_rows, field)

        win = counter.get("win", 0)
        loss = counter.get("loss", 0)
        empty = counter.get("EMPTY", 0)
        total = win + loss

        lines.append(f"win: {win}")
        lines.append(f"loss: {loss}")
        lines.append(f"empty/unknown: {empty}")
        lines.append(f"valid total: {total}")

        if total > 0:
            winrate = (win / total) * 100
            lines.append(f"winrate: {winrate:.2f}%")
        else:
            lines.append("winrate: N/A")

    write_txt(DAILY_DIR, "06_winrate_by_window.txt", lines)


def build_valid_signal_rows(signals):
    valid = []

    for s in signals:
        signal_type = (s.get("signal_type") or "").lower()
        t = safe_int(s.get("signal_time_ms"))

        if signal_type not in ["long", "short"]:
            continue

        if t is None:
            continue

        row = dict(s)
        row["_time"] = t
        row["_type"] = signal_type
        valid.append(row)

    return valid
def report_signal_chain(signals):
    lines = []
    lines.append("LATS AUTO ANALYSIS REPORT")
    lines.append("REPORT: 07 SIGNAL CHAIN ANALYSIS")
    lines.append(f"DATE: {RUN_DATE}")
    lines.append("=" * 50)

    valid = build_valid_signal_rows(signals)

    by_symbol = defaultdict(list)
    for row in valid:
        by_symbol[row.get("symbol", "EMPTY")].append(row)

    total_chains = 0
    long_to_short = 0
    short_to_long = 0
    same_direction = 0
    chain_gaps = []
    per_coin_lines = []

    for symbol, rows in sorted(by_symbol.items()):
        rows.sort(key=lambda x: x["_time"])

        coin_chains = 0
        coin_long_to_short = 0
        coin_short_to_long = 0
        coin_same = 0
        coin_gaps = []

        for i in range(1, len(rows)):
            prev = rows[i - 1]
            curr = rows[i]

            prev_type = prev["_type"]
            curr_type = curr["_type"]

            gap_ms = curr["_time"] - prev["_time"]
            gap_minutes = gap_ms / 1000 / 60

            coin_chains += 1
            total_chains += 1
            coin_gaps.append(gap_minutes)
            chain_gaps.append(gap_minutes)

            if prev_type == "long" and curr_type == "short":
                long_to_short += 1
                coin_long_to_short += 1

            elif prev_type == "short" and curr_type == "long":
                short_to_long += 1
                coin_short_to_long += 1

            else:
                same_direction += 1
                coin_same += 1

        avg_gap = sum(coin_gaps) / len(coin_gaps) if coin_gaps else 0

        per_coin_lines.append(
            f"{symbol}: chains={coin_chains}, "
            f"long->short={coin_long_to_short}, "
            f"short->long={coin_short_to_long}, "
            f"same_direction={coin_same}, "
            f"avg_gap_min={avg_gap:.2f}"
        )

    avg_all_gap = sum(chain_gaps) / len(chain_gaps) if chain_gaps else 0

    lines += section("SUMMARY")
    lines.append(f"Valid long/short signals used: {len(valid)}")
    lines.append(f"Total signal chains: {total_chains}")
    lines.append(f"Long -> Short chains: {long_to_short}")
    lines.append(f"Short -> Long chains: {short_to_long}")
    lines.append(f"Same direction chains: {same_direction}")
    lines.append(f"Average gap between signals: {avg_all_gap:.2f} minutes")

    lines += section("INTERPRETATION")
    lines.append("Long -> Short = possible exit / pause after long")
    lines.append("Short -> Long = possible exit / pause after short")
    lines.append("Same direction = continuation / repeated signal")

    lines += section("BY COIN")
    lines.extend(per_coin_lines)

    write_txt(DAILY_DIR, "07_signal_chain_report.txt", lines)


def report_signal_chain_quality(signals, results):
    lines = []
    lines.append("LATS AUTO ANALYSIS REPORT")
    lines.append("REPORT: 08 SIGNAL CHAIN QUALITY")
    lines.append(f"DATE: {RUN_DATE}")
    lines.append("=" * 50)

    result_map = {
        r.get("signal_id"): r
        for r in results
        if r.get("signal_id")
    }

    valid = build_valid_signal_rows(signals)

    by_symbol = defaultdict(list)

    for row in valid:
        by_symbol[row.get("symbol", "EMPTY")].append(row)

    chain_groups = defaultdict(list)

    for symbol, rows in by_symbol.items():
        rows.sort(key=lambda x: x["_time"])

        for i in range(1, len(rows)):
            prev = rows[i - 1]
            curr = rows[i]

            prev_type = prev["_type"]
            curr_type = curr["_type"]

            curr_result = result_map.get(curr.get("signal_id"))

            trend_4h = curr.get("trend_4h", "EMPTY")
            mtf_align = curr.get("mtf_align", "EMPTY")
            zone = curr.get("zone", "EMPTY")

            record = {
                "symbol": symbol,
                "result_3": get_result_value(curr_result, "result_3"),
                "result_5": get_result_value(curr_result, "result_5"),
                "result_10": get_result_value(curr_result, "result_10"),
                "result_15": get_result_value(curr_result, "result_15"),
                "result_30": get_result_value(curr_result, "result_30"),
            }

            if prev_type == "long" and curr_type == "short":
                chain_name = "LONG_TO_SHORT"

            elif prev_type == "short" and curr_type == "long":
                chain_name = "SHORT_TO_LONG"

            else:
                chain_name = "SAME_DIRECTION"

            key = (
                chain_name,
                trend_4h,
                mtf_align,
                zone,
            )

            chain_groups[key].append(record)

    windows = [
        "result_3",
        "result_5",
        "result_10",
        "result_15",
        "result_30",
    ]

    lines += section("SUMMARY")
    lines.append("Context-aware signal chain quality analysis")
    lines.append("This checks which context creates better continuation or reversal behavior")

    sorted_groups = sorted(
        chain_groups.items(),
        key=lambda x: len(x[1]),
        reverse=True
    )

    for key, records in sorted_groups[:80]:

        chain_name, trend_4h, mtf_align, zone = key

        if len(records) < 20:
            continue

        lines += section(
            f"{chain_name} | "
            f"trend_4h={trend_4h} | "
            f"mtf_align={mtf_align} | "
            f"zone={zone}"
        )

        lines.append(f"sample_size: {len(records)}")

        for window in windows:

            win, loss, empty, total, winrate = calc_winrate(
                records,
                window
            )

            if total > 0:
                lines.append(
                    f"{window}: "
                    f"win={win}, "
                    f"loss={loss}, "
                    f"empty={empty}, "
                    f"winrate={winrate:.2f}%"
                )
            else:
                lines.append(
                    f"{window}: no valid rows"
                )

    lines += section("INTERPRETATION")
    lines.append("LONG_TO_SHORT in strong_up may represent pause more than reversal.")
    lines.append("LONG_TO_SHORT at resistance may create stronger exit quality.")
    lines.append("SAME_DIRECTION high winrate suggests continuation behavior.")
    lines.append("Use this report to classify pause vs reversal behavior.")

    write_txt(
        DAILY_DIR,
        "08_signal_chain_quality.txt",
        lines
    )


def report_compare_placeholder():
    lines = []
    lines.append("LATS AUTO ANALYSIS REPORT")
    lines.append("COMPARE PLACEHOLDER")
    lines.append(f"DATE: {RUN_DATE}")
    lines.append("=" * 50)

    lines.append("Future:")
    lines.append("- compare this week vs last week")
    lines.append("- changed behavior")
    lines.append("- unchanged behavior")
    lines.append("- increased / decreased setup group")
    lines.append("- coin behavior shift")

    write_txt(
        COMPARE_DIR,
        "compare_vs_last_week.txt",
        lines
    )


def report_weekly_summary(signals, results):
    done_rows = count_status(results, "done")
    pending_rows = count_status(results, "pending")

    lines = []

    lines.append("LATS AUTO ANALYSIS REPORT")
    lines.append("WEEKLY SUMMARY")
    lines.append(f"DATE: {RUN_DATE}")
    lines.append(f"RUN_FOLDER: {OUT_ROOT}")
    lines.append("=" * 50)

    lines.append(f"Total signal rows: {len(signals)}")
    lines.append(f"Total result rows: {len(results)}")
    lines.append(f"Done result rows: {done_rows}")
    lines.append(f"Pending result rows: {pending_rows}")

    lines += section("GENERATED REPORTS")

    lines.append("- 01_overview.txt")
    lines.append("- 02_coin_summary.txt")
    lines.append("- 03_trend_summary.txt")
    lines.append("- 04_behavior_summary.txt")
    lines.append("- 05_warning_checklist.txt")
    lines.append("- 06_winrate_by_window.txt")
    lines.append("- 07_signal_chain_report.txt")
    lines.append("- 08_signal_chain_quality.txt")

    lines += section("NEXT")

    lines.append("- Review continuation vs reversal behavior")
    lines.append("- Review LONG_TO_SHORT in strong_up")
    lines.append("- Review SAME_DIRECTION continuation quality")
    lines.append("- Do not add new fields until analysis proves it is needed")

    write_txt(
        SUMMARY_DIR,
        "weekly_summary.txt",
        lines
    )


def main():
    signals = read_csv(SIGNAL_FILE)
    results = read_csv(RESULT_FILE)

    report_overview(signals, results)
    report_coin_summary(signals)
    report_trend_summary(signals)
    report_behavior_summary(signals)
    report_warning_checklist(signals, results)
    report_winrate_by_window(results)

    report_signal_chain(signals)

    report_signal_chain_quality(
        signals,
        results
    )

    report_compare_placeholder()

    report_weekly_summary(
        signals,
        results
    )

    print("LATS auto report generated successfully")
    print(OUT_ROOT)

    print(f"Signal rows: {len(signals)}")
    print(f"Result rows: {len(results)}")

    print(
        f"Done rows: "
        f"{count_status(results, 'done')}"
    )

    print(
        f"Pending rows: "
        f"{count_status(results, 'pending')}"
    )


if __name__ == "__main__":
    main()