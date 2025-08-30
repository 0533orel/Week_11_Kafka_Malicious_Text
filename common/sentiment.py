# Super-simple lexicon-based sentiment. Extend as needed.
POSITIVE = {
    "good","great","love","like","enjoy","happy","success","win","safe","peace","calm","support","hope"
}
NEGATIVE = {
    "bad","hate","kill","attack","bomb","explode","fear","threat","danger","die","dead","war","hostile"
}

def sentiment_from_text(clean_text: str) -> str:
    if not clean_text:
        return "neutral"
    toks = clean_text.split()
    score = 0
    for t in toks:
        if t in POSITIVE:
            score += 1
        if t in NEGATIVE:
            score -= 1
    if score > 0:
        return "positive"
    if score < 0:
        return "negative"
    return "neutral"
