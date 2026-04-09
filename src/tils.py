import re
import html
from datetime import datetime, timezone
import pandas as pd


# =========================================================
# CLEAN TEXT
# =========================================================
def clean_text(text):
    """
    Cleans and normalises text from RSS / API sources.

    - Removes HTML tags
    - Unescapes HTML entities
    - Normalises whitespace
    """

    if not text:
        return ""

    # Convert to string just in case
    text = str(text)

    # Unescape HTML entities (&amp;, etc.)
    text = html.unescape(text)

    # Remove HTML tags
    text = re.sub(r"<[^>]+>", " ", text)

    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# =========================================================
# PARSE DATE
# =========================================================
def parse_date(date_input):
    """
    Safely parses dates from multiple formats into UTC datetime.

    Handles:
    - ISO strings
    - RSS timestamps
    - None values
    - pandas timestamps
    """

    if not date_input:
        return datetime.now(timezone.utc)

    # Already datetime
    if isinstance(date_input, datetime):
        if date_input.tzinfo:
            return date_input.astimezone(timezone.utc)
        return date_input.replace(tzinfo=timezone.utc)

    # Try pandas parser (very robust)
    try:
        dt = pd.to_datetime(date_input, utc=True)
        if pd.isna(dt):
            return datetime.now(timezone.utc)
        return dt.to_pydatetime()
    except Exception:
        pass

    # Fallback: try manual ISO parsing
    try:
        return datetime.fromisoformat(str(date_input).replace("Z", "+00:00"))
    except Exception:
        pass

    # Final fallback
    return datetime.now(timezone.utc)
