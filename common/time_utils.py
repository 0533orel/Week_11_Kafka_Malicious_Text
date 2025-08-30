import re
from datetime import datetime

# Match dates like 25/03/2020 09:30, 25/03/20, 25-03-2020, 25.03.2020 etc.
DATE_PATTERNS = [
    r"(\d{1,2}[\/\.\-]\d{1,2}[\/\.\-]\d{2,4}\s+\d{1,2}:\d{2})",
    r"(\d{1,2}[\/\.\-]\d{1,2}[\/\.\-]\d{2,4})",
]

FMT_TRIES = [
    "%d/%m/%Y %H:%M","%d-%m-%Y %H:%M","%d.%m.%Y %H:%M",
    "%d/%m/%y %H:%M","%d-%m-%y %H:%M","%d.%m.%y %H:%M",
    "%d/%m/%Y","%d-%m-%Y","%d.%m.%Y",
    "%d/%m/%y","%d-%m-%y","%d.%m.%y",
]

def parse_candidate(s: str):
    for fmt in FMT_TRIES:
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            pass
    return None

def latest_timestamp_in_text(text: str) -> str:
    if not text:
        return ""
    candidates = []
    for pat in DATE_PATTERNS:
        for m in re.findall(pat, text):
            dt = parse_candidate(m)
            if dt:
                candidates.append(dt)
    if not candidates:
        return ""
    latest = max(candidates)
    # Return in dd/mm/YYYY HH:MM
    return latest.strftime("%d/%m/%Y %H:%M")
