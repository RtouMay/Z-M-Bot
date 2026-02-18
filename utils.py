from __future__ import annotations


def parse_hhmm(time_text: str) -> tuple[int, int]:
    try:
        hour_text, minute_text = time_text.split(":", maxsplit=1)
        hour, minute = int(hour_text), int(minute_text)
    except ValueError as exc:
        raise ValueError("فرمت زمان باید HH:MM باشد.") from exc

    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        raise ValueError("ساعت یا دقیقه معتبر نیست.")
    return hour, minute
