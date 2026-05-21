import math

from historical.config import SIMILARITY_FIELDS


def safe_float(value, default=0.0):
    try:
        if value is None or value == "":
            return default
        return float(value)
    except Exception:
        return default


def normalize_distance(a, b):
    a = safe_float(a)
    b = safe_float(b)

    return abs(a - b)


def calculate_similarity_score(current_row, historical_row, fields=None):
    if fields is None:
        fields = SIMILARITY_FIELDS

    total_distance = 0.0
    used = 0

    for field in fields:
        if field not in current_row or field not in historical_row:
            continue

        total_distance += normalize_distance(
            current_row.get(field),
            historical_row.get(field),
        )

        used += 1

    if used == 0:
        return 0.0

    avg_distance = total_distance / used

    score = 100 / (1 + avg_distance)

    return round(score, 2)


def find_similar_cases(current_row, historical_rows, top_n=20):
    scored = []

    for row in historical_rows:
        score = calculate_similarity_score(
            current_row=current_row,
            historical_row=row,
        )

        scored.append((score, row))

    scored.sort(key=lambda x: x[0], reverse=True)

    return scored[:top_n]


if __name__ == "__main__":
    print("similarity_engine ready")