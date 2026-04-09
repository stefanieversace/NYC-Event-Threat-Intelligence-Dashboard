import re
from datetime import datetime, timezone

# =========================================================
# KEYWORD WEIGHTS
# =========================================================
HIGH_RISK_TERMS = {
    "shooting": 50,
    "explosion": 60,
    "bomb": 60,
    "terror": 65,
    "active shooter": 75,
    "hostage": 65,
    "fire": 45,
    "evacuation": 40,
    "evacuated": 40,
    "collapse": 45,
    "suspicious package": 45,
    "weapon": 35,
    "gun": 40,
    "mass casualty": 80,
}

MEDIUM_RISK_TERMS = {
    "protest": 22,
    "demonstration": 22,
    "riot": 35,
    "police activity": 20,
    "threat": 24,
    "lockdown": 35,
    "closure": 18,
    "delay": 14,
    "subway": 10,
    "traffic": 10,
    "outage": 18,
}

LOW_RISK_TERMS = {
    "crowd": 6,
    "festival": 5,
    "concert": 5,
    "event": 4,
    "venue": 4,
}

WATCHLIST_TERMS = [
    "madison square garden",
    "msg",
    "barclays center",
    "radio city",
    "times square",
    "stadium",
    "arena",
]

# =========================================================
# KEYWORD EXTRACTION
# =========================================================
def extract_keywords(text):
    """
    Extracts matched risk keywords from text.
    Returns list of matched terms.
    """
    if not text:
        return []

    text = text.lower()

    matched = []

    for term in list(HIGH_RISK_TERMS.keys()) + list(MEDIUM_RISK_TERMS.keys()) + list(LOW_RISK_TERMS.keys()):
        if term in text:
            matched.append(term)

    return list(set(matched))


# =========================================================
# RISK SCORING
# =========================================================
def score_risk(text):
    """
    Returns:
    (risk_level, risk_score, matched_keywords)
    """

    if not text:
        return "LOW", 0, []

    text = text.lower()

    score = 0
    matched_terms = []

    # High risk
    for term, weight in HIGH_RISK_TERMS.items():
        if term in text:
            score += weight
            matched_terms.append(term)

    # Medium risk
    for term, weight in MEDIUM_RISK_TERMS.items():
        if term in text:
            score += weight
            matched_terms.append(term)

    # Low risk
    for term, weight in LOW_RISK_TERMS.items():
        if term in text:
            score += weight
            matched_terms.append(term)

    # Watchlist boost (venue relevance)
    if any(term in text for term in WATCHLIST_TERMS):
        score += 10

    # Location boost
    if "new york" in text or "nyc" in text:
        score += 5

    # Determine risk level
    if score >= 55:
        level = "HIGH"
    elif score >= 24:
        level = "MEDIUM"
    else:
        level = "LOW"

    return level, min(score, 100), list(set(matched_terms))


# =========================================================
# PRIORITY CLASSIFICATION
# =========================================================
def classify_priority(risk_level, risk_score, published_at=None):
    """
    Returns:
    (priority_label, priority_score)
    """

    base_priority = {
        "HIGH": 70,
        "MEDIUM": 40,
        "LOW": 15,
    }[risk_level]

    # Recency boost
    recency_bonus = 0
    if published_at:
        try:
            if isinstance(published_at, str):
                published_at = datetime.fromisoformat(published_at.replace("Z", "+00:00"))

            now = datetime.now(timezone.utc)
            hours_old = (now - published_at).total_seconds() / 3600

            if hours_old <= 3:
                recency_bonus = 18
            elif hours_old <= 12:
                recency_bonus = 12
            elif hours_old <= 24:
                recency_bonus = 8
            else:
                recency_bonus = 4
        except:
            recency_bonus = 0

    priority_score = min(base_priority + risk_score + recency_bonus, 100)

    if priority_score >= 85:
        label = "IMMEDIATE"
    elif priority_score >= 60:
        label = "ELEVATED"
    elif priority_score >= 35:
        label = "ROUTINE+"
    else:
        label = "MONITOR"

    return label, priority_score
