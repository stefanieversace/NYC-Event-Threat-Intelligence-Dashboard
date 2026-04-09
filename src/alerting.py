import uuid
from datetime import datetime


def generate_alert_id(title, source, published_at, location):
    """
    Generates a deterministic, Sentinel-style alert ID based on event attributes.

    Example output:
    ALRT-9F3A1C7B2D
    """

    if isinstance(published_at, str):
        try:
            published_at = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
        except Exception:
            published_at = datetime.utcnow()

    base_string = f"{title}|{source}|{location}|{published_at.isoformat()}"

    # Generate consistent UUID based on content
    alert_hash = uuid.uuid5(uuid.NAMESPACE_DNS, base_string).hex[:10].upper()

    return f"ALRT-{alert_hash}"


def recommended_actions(risk, impact="", protected_assets=""):
    """
    Returns a list of operational actions based on risk level,
    impact description, and affected assets.
    """

    actions = []

    # =========================
