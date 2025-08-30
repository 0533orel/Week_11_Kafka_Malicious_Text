import re

def load_blacklist(path: str):
    try:
        with open(path, "r", encoding="utf-8") as f:
            items = [ln.strip() for ln in f if ln.strip() and not ln.strip().startswith("#")]
        # normalize
        items = sorted(set([i.lower() for i in items]))
        return items
    except FileNotFoundError:
        return []

def detect_weapons(clean_text: str, blacklist: list[str]) -> list[str]:
    if not clean_text:
        return []
    words = set(clean_text.split())
    # also capture hyphenated variants, e.g., ak-47 vs ak47
    found = set()
    for w in blacklist:
        w0 = w.replace("-", "")
        if w in words:
            found.add(w)
        elif w0 in words:
            found.add(w)
        else:
            # regex contains check (word boundary-ish) – minimal
            if re.search(rf"\b{re.escape(w)}\b", clean_text):
                found.add(w)
            elif "-" in w and re.search(rf"\b{re.escape(w.replace('-', ''))}\b", clean_text):
                found.add(w)
    return sorted(found)
