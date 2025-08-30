import re
import string

# A very small English stopword list to keep things lightweight and readable
STOPWORDS = {
    "a","an","the","and","or","but","if","then","else","when","while","for","to","of","in","on","at","by",
    "is","are","was","were","be","been","being","as","with","from","that","this","these","those","it","its",
    "he","she","they","them","we","you","i","my","your","our","their","me"
}

_punct_tbl = str.maketrans({c: " " for c in string.punctuation})

def normalize_whitespace(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()

def remove_specials(s: str) -> str:
    # Keep letters, numbers, hyphen, and whitespace; everything else -> space
    return re.sub(r"[^A-Za-z0-9\-\s]", " ", s)

def to_lower(s: str) -> str:
    return s.lower()

def tokenize(s: str):
    return s.split()

def light_stem(word: str) -> str:
    # Extremely lightweight "lemmatization-ish" rules for demonstration.
    # Order matters.
    w = word
    if len(w) > 4 and w.endswith("ies"):
        return w[:-3] + "y"
    if len(w) > 4 and w.endswith("ing"):
        return w[:-3]
    if len(w) > 3 and w.endswith("ed"):
        return w[:-2]
    if len(w) > 3 and w.endswith("es"):
        return w[:-2]
    if len(w) > 3 and w.endswith("s"):
        return w[:-1]
    return w

def remove_stopwords(tokens):
    return [t for t in tokens if t not in STOPWORDS]

def clean_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    s = text.translate(_punct_tbl)
    s = remove_specials(s)
    s = to_lower(s)
    s = normalize_whitespace(s)
    toks = tokenize(s)
    toks = remove_stopwords(toks)
    toks = [light_stem(t) for t in toks]
    return " ".join(toks)
