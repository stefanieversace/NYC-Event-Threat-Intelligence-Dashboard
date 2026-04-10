import os
import re
import html
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Tuple

import feedparser
import folium
import pandas as pd
import plotly.express as px
import requests
import streamlit as st
from folium.plugins import MarkerCluster
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from streamlit_autorefresh import st_autorefresh
from streamlit_folium import st_folium

import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="NYC Event Threat Intelligence Dashboard",
    page_icon="🗽",
    layout="wide"
)

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(180deg, #08111f 0%, #0f172a 100%);
        color: #e5e7eb;
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    [data-testid="stSidebar"] {
        background: #0b1220;
        border-right: 1px solid rgba(148, 163, 184, 0.12);
    }

    [data-testid="stSidebar"] * {
        color: #e5e7eb !important;
    }

    .hero-wrap {
        padding: 1.2rem 1.25rem 0.8rem 1.25rem;
        border: 1px solid rgba(148, 163, 184, 0.14);
        border-radius: 18px;
        background: linear-gradient(135deg, rgba(15,23,42,0.98) 0%, rgba(17,24,39,0.95) 100%);
        box-shadow: 0 10px 30px rgba(0,0,0,0.22);
        margin-bottom: 1rem;
    }

    .hero-title {
        font-size: 2rem;
        font-weight: 800;
        color: #f8fafc;
        line-height: 1.1;
        margin-bottom: 0.35rem;
    }

    .hero-subtitle {
        font-size: 0.98rem;
        color: #94a3b8;
        line-height: 1.55;
        margin-bottom: 0.9rem;
    }

    .chip {
        display: inline-block;
        padding: 0.35rem 0.7rem;
        margin: 0 0.45rem 0.45rem 0;
        border-radius: 999px;
        background: rgba(30, 41, 59, 0.95);
        border: 1px solid rgba(148, 163, 184, 0.14);
        color: #cbd5e1;
        font-size: 0.78rem;
        font-weight: 600;
    }

    .status-box {
        text-align: right;
        color: #94a3b8;
        font-size: 0.82rem;
        padding-top: 0.25rem;
    }

    .panel {
        background: rgba(15, 23, 42, 0.82);
        border: 1px solid rgba(148, 163, 184, 0.14);
        border-radius: 18px;
        padding: 1rem;
        box-shadow: 0 8px 28px rgba(0,0,0,0.14);
        margin-bottom: 1rem;
    }

    .panel-title {
        font-size: 1rem;
        font-weight: 700;
        color: #f8fafc;
        margin-bottom: 0.75rem;
    }

    .metric-card {
        background: linear-gradient(180deg, rgba(15,23,42,0.98) 0%, rgba(17,24,39,0.95) 100%);
        border: 1px solid rgba(148, 163, 184, 0.14);
        border-radius: 16px;
        padding: 1rem;
        min-height: 110px;
        box-shadow: 0 8px 28px rgba(0,0,0,0.14);
    }

    .metric-label {
        font-size: 0.76rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #94a3b8;
        margin-bottom: 0.5rem;
    }

    .metric-value {
        font-size: 1.9rem;
        font-weight: 800;
        color: #f8fafc;
        line-height: 1.05;
    }

    .metric-note {
        font-size: 0.82rem;
        color: #94a3b8;
        margin-top: 0.35rem;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        margin-top: 0.5rem;
    }

    .stTabs [data-baseweb="tab"] {
        background: rgba(15, 23, 42, 0.75);
        border: 1px solid rgba(148, 163, 184, 0.14);
        border-radius: 12px;
        padding: 0.55rem 0.9rem;
        color: #cbd5e1;
    }

    .stTabs [aria-selected="true"] {
        background: rgba(30, 41, 59, 1);
        color: #f8fafc !important;
    }

    div[data-testid="stDataFrame"] {
        border-radius: 14px;
        overflow: hidden;
        border: 1px solid rgba(148, 163, 184, 0.14);
    }

    .section-spacer {
        height: 0.2rem;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# CONSTANTS
# =========================================================
NYC_DEFAULT_CENTER = (40.7505, -73.9934)

RSS_FEEDS = {
    "Google News - New York": "https://news.google.com/rss/search?q=New+York&hl=en-US&gl=US&ceid=US:en",
    "Google News - NYC events": "https://news.google.com/rss/search?q=New+York+concert+OR+stadium+OR+arena+OR+festival+OR+parade&hl=en-US&gl=US&ceid=US:en",
    "Google News - protests": "https://news.google.com/rss/search?q=New+York+protest+OR+demonstration&hl=en-US&gl=US&ceid=US:en",
    "Google News - transit disruption": "https://news.google.com/rss/search?q=New+York+subway+delay+OR+transit+disruption&hl=en-US&gl=US&ceid=US:en",
    "ABC7 New York": "https://abc7ny.com/feed/",
    "CBS New York": "https://www.cbsnews.com/latest/rss/main",
    "Reuters World": "https://feeds.reuters.com/Reuters/worldNews",
}

WATCHLIST_VENUES = {
    "Madison Square Garden": "madison square garden",
    "Barclays Center": "barclays center",
    "Radio City Music Hall": "radio city",
    "Times Square": "times square",
}

VENUE_COORDS = {
    "madison square garden": (40.7505, -73.9934),
    "msg": (40.7505, -73.9934),
    "radio city": (40.7599, -73.9793),
    "radio city music hall": (40.7599, -73.9793),
    "barclays center": (40.6826, -73.9754),
    "yankee stadium": (40.8296, -73.9262),
    "citi field": (40.7571, -73.8458),
    "metlife stadium": (40.8135, -74.0745),
    "ubs arena": (40.7118, -73.7260),
    "forest hills stadium": (40.7181, -73.8448),
    "terminal 5": (40.7697, -73.9928),
    "brooklyn mirage": (40.7172, -73.9387),
    "javits center": (40.7578, -74.0026),
    "times square": (40.7580, -73.9855),
    "central park": (40.7829, -73.9654),
    "prospect park": (40.6602, -73.9690),
    "flushing meadows": (40.7498, -73.8408),
    "bryant park": (40.7536, -73.9832),
    "union square": (40.7359, -73.9911),
    "battery park": (40.7033, -74.0170),
    "jfk": (40.6413, -73.7781),
    "laguardia": (40.7769, -73.8740),
    "newark": (40.6895, -74.1745),
}

AREA_FALLBACK_COORDS = {
    "manhattan": (40.7831, -73.9712),
    "brooklyn": (40.6782, -73.9442),
    "queens": (40.7282, -73.7949),
    "bronx": (40.8448, -73.8648),
    "staten island": (40.5795, -74.1502),
    "midtown": (40.7549, -73.9840),
    "harlem": (40.8116, -73.9465),
    "chelsea": (40.7465, -74.0014),
    "soho": (40.7233, -74.0030),
    "lower manhattan": (40.7075, -74.0113),
    "williamsburg": (40.7081, -73.9571),
    "astoria": (40.7644, -73.9235),
    "flushing": (40.7675, -73.8331),
    "brooklyn heights": (40.6959, -73.9956),
}

EVENT_KEYWORDS = [
    "concert", "festival", "show", "parade", "game", "match", "stadium", "arena",
    "venue", "event", "production", "premiere", "red carpet", "fan event",
    "public gathering", "crowd", "performance", "live nation", "msg", "nbc",
    "netflix", "barclays", "radio city", "madison square garden"
]

HIGH_RISK_TERMS = {
    "shooting": 50, "stab": 40, "explosion": 60, "bomb": 60, "terror": 65,
    "terrorist": 65, "active shooter": 75, "hostage": 65, "fire": 45,
    "arson": 45, "evacuated": 40, "evacuation": 40, "collapse": 45,
    "fatal": 35, "killed": 35, "deadly": 40, "vehicle ramming": 60,
    "credible threat": 55, "suspicious package": 45, "weapon": 35,
    "gun": 40, "guns": 40, "injured": 30, "mass casualty": 80
}

MEDIUM_RISK_TERMS = {
    "protest": 22, "demonstration": 22, "march": 18, "unrest": 28, "riot": 35,
    "disruption": 20, "delay": 14, "police activity": 20, "security incident": 26,
    "threat": 24, "lockdown": 35, "closure": 18, "closed": 18, "surge": 14,
    "traffic": 10, "transit": 10, "subway": 10, "strike": 20, "cyberattack": 35,
    "outage": 18, "power outage": 24, "drone": 20, "trespasser": 18
}

LOW_RISK_TERMS = {
    "crowd": 6, "attendance": 5, "sold out": 4, "festival": 5, "concert": 5,
    "match": 5, "event": 4, "venue": 4, "premiere": 4
}

PROTECTED_ASSETS = {
    "people": ["crowd", "attendee", "fan", "spectator", "passenger"],
    "venue": ["arena", "stadium", "venue", "theatre", "center", "hall"],
    "transport": ["subway", "transit", "train", "airport", "traffic", "road"],
    "production": ["production", "broadcast", "studio", "filming", "premiere"],
}

WATCHLIST_TERMS = [
    "madison square garden", "msg", "barclays center", "radio city", "times square",
    "concert", "festival", "protest", "subway", "stadium", "arena", "premiere",
    "netflix", "nbc", "live nation", "production", "security", "evacuation"
]

NEWS_API_KEY = os.getenv("NEWS_API_KEY", "").strip()

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.markdown("## Controls")

auto_refresh = st.sidebar.toggle("Auto-refresh", value=False)
refresh_seconds = st.sidebar.slider("Refresh interval (seconds)", 30, 600, 120, 30)

if auto_refresh:
    st_autorefresh(interval=refresh_seconds * 1000, key="nyc-threat-refresh")

hours_back = st.sidebar.slider("Look back window (hours)", 6, 168, 48, 6)
risk_filter = st.sidebar.multiselect(
    "Risk levels",
    ["HIGH", "MEDIUM", "LOW"],
    default=["HIGH", "MEDIUM", "LOW"],
)
source_limit = st.sidebar.slider("Max records per source", 5, 100, 25, 5)
keyword_filter = st.sidebar.text_input("Keyword filter", "")
show_only_event_related = st.sidebar.toggle("Event-related only", value=True)
show_simulated_items = st.sidebar.toggle("Include simulated demo incidents", value=True)
use_newsapi = st.sidebar.toggle("Use NewsAPI (if configured)", value=bool(NEWS_API_KEY))
show_raw_feed = st.sidebar.toggle("Show raw feed table", value=True)

st.sidebar.markdown("---")
st.sidebar.markdown("## Venue Watchlist")
selected_venues = st.sidebar.multiselect(
    "Monitor venues",
    list(WATCHLIST_VENUES.keys()),
    default=list(WATCHLIST_VENUES.keys())
)

st.sidebar.markdown("---")
st.sidebar.caption("Set NEWS_API_KEY in environment variables to enable NewsAPI enrichment.")

# =========================================================
# HELPERS
# =========================================================
def clean_text(text: str) -> str:
    if not text:
        return ""
    text = str(text)
    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def safe_get(entry, key, default=""):
    try:
        return entry.get(key, default)
    except Exception:
        return default


def parse_datetime(value) -> datetime:
    if not value:
        return datetime.now(timezone.utc)

    if isinstance(value, datetime):
        return value.astimezone(timezone.utc) if value.tzinfo else value.replace(tzinfo=timezone.utc)

    try:
        dt = pd.to_datetime(value, utc=True)
        if pd.isna(dt):
            return datetime.now(timezone.utc)
        return dt.to_pydatetime()
    except Exception:
        return datetime.now(timezone.utc)


def hours_since(dt: datetime) -> float:
    now = datetime.now(timezone.utc)
    delta = now - dt.astimezone(timezone.utc)
    return max(delta.total_seconds() / 3600, 0)


def normalise_url(url: str) -> str:
    return url.strip() if url else ""


def contains_any(text: str, terms: List[str]) -> bool:
    lower = text.lower()
    return any(term in lower for term in terms)


def count_term_hits(text: str, weighted_terms: Dict[str, int]) -> Tuple[int, List[str]]:
    score = 0
    hits = []
    lower = text.lower()
    for term, weight in weighted_terms.items():
        if term in lower:
            score += weight
            hits.append(term)
    return score, hits


def infer_operational_impact(text: str) -> str:
    lower = text.lower()

    if any(t in lower for t in ["active shooter", "bomb", "explosion", "terror", "mass casualty", "hostage"]):
        return "Severe threat to life safety and immediate event disruption likely."
    if any(t in lower for t in ["fire", "evacuation", "evacuated", "collapse", "weapon", "suspicious package"]):
        return "Likely venue disruption with urgent security and crowd management implications."
    if any(t in lower for t in ["protest", "demonstration", "march", "riot", "police activity", "lockdown"]):
        return "Potential access control pressure, perimeter disruption, and crowd movement challenges."
    if any(t in lower for t in ["subway", "delay", "traffic", "closure", "outage", "strike"]):
        return "Possible attendee movement disruption and delayed ingress or egress."
    return "Monitor for escalation; current impact appears limited but relevant to situational awareness."


def infer_asset_type(text: str) -> str:
    lower = text.lower()
    matched_assets = []

    for asset, terms in PROTECTED_ASSETS.items():
        if any(term in lower for term in terms):
            matched_assets.append(asset)

    if not matched_assets:
        return "general operations"

    return ", ".join(sorted(set(matched_assets)))


def classify_event_relevance(text: str) -> bool:
    return contains_any(text, EVENT_KEYWORDS) or contains_any(text, WATCHLIST_TERMS)


def infer_location_from_text(text: str) -> Tuple[float, float, str]:
    lower = text.lower()

    for venue, coords in VENUE_COORDS.items():
        if venue in lower:
            return coords[0], coords[1], venue.title()

    for area, coords in AREA_FALLBACK_COORDS.items():
        if area in lower:
            return coords[0], coords[1], area.title()

    return NYC_DEFAULT_CENTER[0], NYC_DEFAULT_CENTER[1], "New York City"


def recency_boost(hours_old: float) -> int:
    if hours_old <= 3:
        return 18
    if hours_old <= 12:
        return 12
    if hours_old <= 24:
        return 8
    if hours_old <= 48:
        return 4
    return 0


def score_risk(title: str, summary: str) -> Tuple[str, int, List[str]]:
    text = f"{title} {summary}".lower()

    high_score, high_hits = count_term_hits(text, HIGH_RISK_TERMS)
    med_score, med_hits = count_term_hits(text, MEDIUM_RISK_TERMS)
    low_score, low_hits = count_term_hits(text, LOW_RISK_TERMS)

    total = high_score + med_score + low_score
    hits = high_hits + med_hits + low_hits

    if contains_any(text, WATCHLIST_TERMS):
        total += 8

    if "new york" in text or "nyc" in text or "manhattan" in text or "brooklyn" in text:
        total += 5

    if total >= 55:
        return "HIGH", min(total, 100), hits
    if total >= 24:
        return "MEDIUM", min(total, 100), hits
    return "LOW", min(total, 100), hits


def compute_priority(risk_level: str, risk_score_value: int, hours_old: float, is_event_related: bool) -> int:
    base = {"HIGH": 70, "MEDIUM": 40, "LOW": 15}[risk_level]
    event_bonus = 10 if is_event_related else 0
    return min(base + risk_score_value + recency_boost(hours_old) + event_bonus, 100)


def priority_label(priority: int) -> str:
    if priority >= 85:
        return "IMMEDIATE"
    if priority >= 60:
        return "ELEVATED"
    if priority >= 35:
        return "ROUTINE+"
    return "MONITOR"


def marker_colour(risk: str) -> str:
    return {
        "HIGH": "red",
        "MEDIUM": "orange",
        "LOW": "green",
    }.get(risk, "blue")


def generate_alert_id(title: str, source: str, published_at: datetime, location: str) -> str:
    base = f"{title}|{source}|{published_at.isoformat()}|{location}"
    digest = uuid.uuid5(uuid.NAMESPACE_DNS, base).hex[:10].upper()
    return f"ALRT-{digest}"


def recommended_actions(risk: str, impact: str, protected_assets: str) -> List[str]:
    actions = []

    if risk == "HIGH":
        actions.extend([
            "Escalate to security command immediately.",
            "Review CCTV coverage and live perimeter conditions.",
            "Coordinate with venue security leadership and law enforcement.",
            "Prepare protective response and crowd-control contingencies.",
        ])
    elif risk == "MEDIUM":
        actions.extend([
            "Increase monitoring frequency for escalation indicators.",
            "Notify venue or event security stakeholders.",
            "Assess likely disruption to access control and crowd flow.",
        ])
    else:
        actions.extend([
            "Continue monitoring and retain on watchlist.",
            "Log item for situational awareness and trend tracking.",
        ])

    if "transport" in protected_assets:
        actions.append("Review ingress and egress dependencies tied to transit routes.")
    if "people" in protected_assets:
        actions.append("Validate crowd-safety posture and staffing readiness.")
    if "venue" in protected_assets:
        actions.append("Review perimeter, screening, and access-control measures.")
    if "production" in protected_assets:
        actions.append("Assess impact to filming, broadcast, or event continuity.")

    unique_actions = []
    for action in actions:
        if action not in unique_actions:
            unique_actions.append(action)

    return unique_actions


def generate_pdf_brief(brief_text: str, filename: str = "/mnt/data/NYC_Executive_Threat_Brief.pdf") -> str:
    doc = SimpleDocTemplate(filename)
    styles = getSampleStyleSheet()
    story = []

    for line in brief_text.split("\n"):
        safe_line = html.escape(line)
        story.append(Paragraph(safe_line, styles["Normal"]))
        story.append(Spacer(1, 8))

    doc.build(story)
    return filename

# =========================================================
# DATA INGESTION
# =========================================================
@st.cache_data(ttl=300, show_spinner=False)
def fetch_rss_items(limit_per_source: int = 25) -> List[Dict]:
    items = []

    for source_name, feed_url in RSS_FEEDS.items():
        try:
            parsed = feedparser.parse(feed_url)
            for entry in parsed.entries[:limit_per_source]:
                title = clean_text(safe_get(entry, "title", "Untitled"))
                summary = clean_text(safe_get(entry, "summary", ""))
                link = normalise_url(safe_get(entry, "link", ""))
                published = (
                    safe_get(entry, "published", "")
                    or safe_get(entry, "updated", "")
                    or safe_get(entry, "created", "")
                )

                items.append(
                    {
                        "source": source_name,
                        "title": title,
                        "summary": summary,
                        "url": link,
                        "published_at": parse_datetime(published),
                        "feed_type": "RSS",
                    }
                )
        except Exception:
            continue

    return items


@st.cache_data(ttl=300, show_spinner=False)
def fetch_newsapi_items(limit_per_source: int = 25) -> List[Dict]:
    if not NEWS_API_KEY:
        return []

    query = (
        '("New York" OR NYC OR Manhattan OR Brooklyn OR Queens OR Bronx) '
        'AND (concert OR stadium OR arena OR festival OR event OR protest OR subway '
        'OR production OR premiere OR venue OR security)'
    )

    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": min(limit_per_source * 2, 100),
        "apiKey": NEWS_API_KEY,
    }

    try:
        response = requests.get(url, params=params, timeout=20)
        response.raise_for_status()
        data = response.json()
        articles = data.get("articles", [])

        results = []
        for article in articles:
            results.append(
                {
                    "source": article.get("source", {}).get("name", "NewsAPI"),
                    "title": clean_text(article.get("title", "")),
                    "summary": clean_text(article.get("description", "")) + " " + clean_text(article.get("content", "")),
                    "url": normalise_url(article.get("url", "")),
                    "published_at": parse_datetime(article.get("publishedAt")),
                    "feed_type": "NewsAPI",
                }
            )
        return results
    except Exception:
        return []


def generate_simulated_items() -> List[Dict]:
    now = datetime.now(timezone.utc)
    return [
        {
            "source": "Simulated Feed",
            "title": "Crowd surge reported outside Madison Square Garden before sold-out concert",
            "summary": "Heavy pedestrian congestion, temporary lane closures, and elevated security presence reported in Midtown Manhattan ahead of a major live event.",
            "url": "",
            "published_at": now - timedelta(hours=2),
            "feed_type": "Simulated",
        },
        {
            "source": "Simulated Feed",
            "title": "Demonstration announced near Times Square with possible spillover into event routes",
            "summary": "Public gathering expected to affect vehicle access, crowd movement, and policing posture near entertainment venues and tourist corridors.",
            "url": "",
            "published_at": now - timedelta(hours=6),
            "feed_type": "Simulated",
        },
        {
            "source": "Simulated Feed",
            "title": "Subway delays on multiple lines may affect ingress to Barclays Center evening event",
            "summary": "Transit disruption could slow attendee arrival patterns and create queuing pressure at entry points.",
            "url": "",
            "published_at": now - timedelta(hours=4),
            "feed_type": "Simulated",
        },
        {
            "source": "Simulated Feed",
            "title": "Suspicious package investigation prompts partial perimeter adjustment near Radio City Music Hall",
            "summary": "Police activity and controlled access measures reported in the surrounding area with potential implications for pedestrian flow.",
            "url": "",
            "published_at": now - timedelta(hours=1),
            "feed_type": "Simulated",
        },
    ]


def load_sample_csv_items() -> List[Dict]:
    path = "data/sample_events.csv"
    if not os.path.exists(path):
        return []

    try:
        sample_df = pd.read_csv(path)
    except Exception:
        return []

    required_cols = {"title", "summary", "location", "risk", "priority", "source", "published_at"}
    if not required_cols.issubset(set(sample_df.columns)):
        return []

    items = []
    for _, row in sample_df.iterrows():
        items.append(
            {
                "source": row.get("source", "Sample Data"),
                "title": clean_text(row.get("title", "")),
                "summary": clean_text(row.get("summary", "")),
                "url": "",
                "published_at": parse_datetime(row.get("published_at")),
                "feed_type": "Sample CSV",
            }
        )
    return items


def deduplicate_items(items: List[Dict]) -> List[Dict]:
    seen = set()
    deduped = []

    for item in items:
        key = (
            item.get("title", "").strip().lower(),
            item.get("source", "").strip().lower(),
        )
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)

    return deduped

st.markdown('<div class="hero-wrap">', unsafe_allow_html=True)

hero_left, hero_right = st.columns([1.9, 1])

with hero_left:
    st.markdown(
        '<div class="hero-title">NYC Event Threat Intelligence Dashboard</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="hero-subtitle">Operational monitoring for live events, venues, crowd movement, transit disruption, and emerging public safety indicators across New York City.</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        """
        <span class="chip">OSINT Monitoring</span>
        <span class="chip">Venue Watchlisting</span>
        <span class="chip">Risk Scoring</span>
        <span class="chip">MITRE Mapping</span>
        <span class="chip">Executive Reporting</span>
        """,
        unsafe_allow_html=True
    )

with hero_right:
    posture = "Routine"
    if high_alerts > 0:
        posture = "Immediate Review"
    elif medium_alerts > 0:
        posture = "Elevated Monitoring"

    st.markdown(
        f"""
        <div class="status-box">
            <div><strong>Monitoring Posture:</strong> {posture}</div>
            <div><strong>Last Refreshed:</strong> {datetime.now().strftime("%d %b %Y, %H:%M:%S")}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("</div>", unsafe_allow_html=True)

def build_dataframe(items: List[Dict]) -> pd.DataFrame:
    enriched = []

    for item in items:
        title = item.get("title", "")
        summary = item.get("summary", "")
        combined_text = f"{title} {summary}"

        published_at = parse_datetime(item.get("published_at"))
        age_hours = round(hours_since(published_at), 1)

        risk, risk_score_value, term_hits = score_risk(title, summary)
        event_related = classify_event_relevance(combined_text)

        lat, lon, inferred_location = infer_location_from_text(combined_text)
        impact = infer_operational_impact(combined_text)
        asset_type = infer_asset_type(combined_text)
        priority_score = compute_priority(risk, risk_score_value, age_hours, event_related)
        priority = priority_label(priority_score)
        alert_id = generate_alert_id(title, item.get("source", "Unknown"), published_at, inferred_location)

        enriched.append(
            {
                "alert_id": alert_id,
                "published_at": published_at,
                "age_hours": age_hours,
                "source": item.get("source", "Unknown"),
                "feed_type": item.get("feed_type", "Unknown"),
                "title": title,
                "summary": summary,
                "url": item.get("url", ""),
                "risk": risk,
                "risk_score": risk_score_value,
                "priority_score": priority_score,
                "priority": priority,
                "event_related": event_related,
                "location": inferred_location,
                "lat": lat,
                "lon": lon,
                "impact": impact,
                "protected_assets": asset_type,
                "matched_terms": ", ".join(sorted(set(term_hits))) if term_hits else "",
            }
        )

    df = pd.DataFrame(enriched)

    if df.empty:
        return df

    df = df.sort_values(
        by=["priority_score", "risk_score", "published_at"],
        ascending=[False, False, False]
    ).reset_index(drop=True)

    return df


def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours_back)
    filtered = df[df["published_at"] >= cutoff].copy()

    if risk_filter:
        filtered = filtered[filtered["risk"].isin(risk_filter)]

    if show_only_event_related:
        filtered = filtered[filtered["event_related"] == True]

    if keyword_filter.strip():
        pattern = keyword_filter.strip().lower()
        mask = (
            filtered["title"].str.lower().str.contains(pattern, na=False)
            | filtered["summary"].str.lower().str.contains(pattern, na=False)
            | filtered["location"].str.lower().str.contains(pattern, na=False)
            | filtered["source"].str.lower().str.contains(pattern, na=False)
            | filtered["alert_id"].str.lower().str.contains(pattern, na=False)
        )
        filtered = filtered[mask]

    if selected_venues:
        venue_terms = [WATCHLIST_VENUES[v] for v in selected_venues]
        venue_pattern = "|".join(re.escape(term) for term in venue_terms)
        filtered = filtered[
            filtered["title"].str.lower().str.contains(venue_pattern, na=False)
            | filtered["summary"].str.lower().str.contains(venue_pattern, na=False)
            | filtered["location"].str.lower().str.contains(venue_pattern, na=False)
        ]

    return filtered.reset_index(drop=True)


def generate_briefing(df: pd.DataFrame) -> str:
    if df.empty:
        return (
            "NYC EVENT INTELLIGENCE BRIEF\n\n"
            "No qualifying items in the current view.\n"
            "Recommendation: maintain baseline monitoring posture and continue collection."
        )

    total = len(df)
    high = (df["risk"] == "HIGH").sum()
    medium = (df["risk"] == "MEDIUM").sum()
    low = (df["risk"] == "LOW").sum()

    top_items = df.head(5)
    locations = df["location"].value_counts().head(5)
    sources = df["source"].value_counts().head(5)

    lines = []
    lines.append("NYC EVENT INTELLIGENCE BRIEF")
    lines.append("")
    lines.append(f"Collection window: last {hours_back} hours")
    lines.append(f"Items in view: {total}")
    lines.append(f"Risk mix: HIGH {high} | MEDIUM {medium} | LOW {low}")
    lines.append("")

    if high > 0:
        lines.append("Executive assessment:")
        lines.append(
            "Elevated operational attention recommended. High-risk or high-priority indicators suggest possible impacts to venue access, crowd safety, transport flow, or event continuity."
        )
    elif medium > 0:
        lines.append("Executive assessment:")
        lines.append(
            "Moderate operational awareness posture recommended. Current indicators suggest potential disruption factors requiring monitoring and contingency planning."
        )
    else:
        lines.append("Executive assessment:")
        lines.append(
            "Current view indicates low-severity but relevant situational awareness items. Maintain routine monitoring posture."
        )

    lines.append("")
    lines.append("Top items for analyst review:")
    for _, row in top_items.iterrows():
        lines.append(
            f"- {row['alert_id']} | [{row['priority']}] {row['title']} | {row['location']} | "
            f"Risk={row['risk']} ({row['risk_score']}) | Age={row['age_hours']}h"
        )

    lines.append("")
    lines.append("Geographic concentration:")
    for loc, count in locations.items():
        lines.append(f"- {loc}: {count}")

    lines.append("")
    lines.append("Most active sources:")
    for src, count in sources.items():
        lines.append(f"- {src}: {count}")

    lines.append("")
    lines.append("Operational recommendations:")
    if high > 0:
        lines.append("- Review venue ingress, egress, and perimeter plans for affected locations.")
        lines.append("- Validate transport disruption contingencies for attendee movement.")
        lines.append("- Escalate high-priority items to duty leadership for awareness.")
    elif medium > 0:
        lines.append("- Maintain enhanced monitoring for escalation indicators.")
        lines.append("- Review likely impacts to crowd flow and access control.")
        lines.append("- Prepare comms notes for venue or operations partners.")
    else:
        lines.append("- Continue routine monitoring and watchlist coverage.")
        lines.append("- Retain transport and public gathering keywords on active watch.")
        lines.append("- Refresh collection as event timings approach.")

    return "\n".join(lines)


def make_map(df: pd.DataFrame) -> folium.Map:
    m = folium.Map(location=NYC_DEFAULT_CENTER, zoom_start=11, tiles="CartoDB positron")
    cluster = MarkerCluster().add_to(m)

    if df.empty:
        return m

    for _, row in df.iterrows():
        popup_html = f"""
        <div style="width:340px;">
            <b>{html.escape(str(row['title']))}</b><br><br>
            <b>Alert ID:</b> {html.escape(str(row['alert_id']))}<br>
            <b>Risk:</b> {html.escape(str(row['risk']))} ({row['risk_score']})<br>
            <b>Priority:</b> {html.escape(str(row['priority']))} ({row['priority_score']})<br>
            <b>Location:</b> {html.escape(str(row['location']))}<br>
            <b>Source:</b> {html.escape(str(row['source']))}<br>
            <b>Age:</b> {row['age_hours']}h<br>
            <b>Assets:</b> {html.escape(str(row['protected_assets']))}<br><br>
            <b>Impact:</b> {html.escape(str(row['impact']))}<br><br>
            <span style="font-size:12px;">{html.escape(str(row['summary'])[:280])}</span>
        </div>
        """

        folium.Marker(
            location=[row["lat"], row["lon"]],
            popup=folium.Popup(popup_html, max_width=350),
            tooltip=f"{row['risk']} | {row['location']} | {row['alert_id']}",
            icon=folium.Icon(color=marker_colour(row["risk"]), icon="info-sign"),
        ).add_to(cluster)

    return m

# =========================================================
# LOAD + PROCESS
# =========================================================
with st.spinner("Collecting open-source items..."):
    all_items = fetch_rss_items(limit_per_source=source_limit)

    if use_newsapi and NEWS_API_KEY:
        all_items.extend(fetch_newsapi_items(limit_per_source=source_limit))

    if show_simulated_items:
        all_items.extend(generate_simulated_items())

    if not all_items:
        all_items.extend(load_sample_csv_items())

    all_items = deduplicate_items(all_items)
    df_all = build_dataframe(all_items)
    df = filter_dataframe(df_all)

total_alerts = 0 if df.empty else len(df)
high_alerts = 0 if df.empty else int((df["risk"] == "HIGH").sum())
medium_alerts = 0 if df.empty else int((df["risk"] == "MEDIUM").sum())
avg_priority = 0 if df.empty else round(float(df["priority_score"].mean()), 1)


briefing = generate_briefing(df)

# =========================================================
# HEADER
# =========================================================
st.markdown('<div class="page-title">NYC Event Threat Intelligence Dashboard</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="page-subtitle">Operational monitoring for live events, venues, public gatherings, and transit-adjacent disruption across New York City.</div>',
    unsafe_allow_html=True,
)

header_left, header_right = st.columns([1.4, 1])
with header_left:
    chips = [
        "OSINT monitoring",
        "Venue watchlisting",
        "Risk scoring",
        "Executive brief export",
    ]
    st.markdown("".join([f'<span class="summary-chip">{c}</span>' for c in chips]), unsafe_allow_html=True)

with header_right:
    st.markdown(
        f'<div class="small-muted" style="text-align:right;">Last refreshed: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>',
        unsafe_allow_html=True,
    )

# =========================================================
# ALERT BANNER
# =========================================================
if not df.empty:
    top_priority = int(df["priority_score"].max())
    high_count = int((df["risk"] == "HIGH").sum())

    if high_count > 0 or top_priority >= 85:
        st.error("Immediate review recommended. High-risk or high-priority indicators are present in the current operational picture.")
    elif int((df["risk"] == "MEDIUM").sum()) > 0:
        st.warning("Elevated monitoring posture advised. Current items may affect venue operations, transport flow, or crowd movement.")
    else:
        st.success("No major escalations in the current filtered view. Routine monitoring posture remains appropriate.")
else:
    st.info("No items matched the current filters.")

# =========================================================
# KPI CALCULATIONS
# =========================================================
if not df.empty:
    high_items = int((df["risk"] == "HIGH").sum())
    med_items = int((df["risk"] == "MEDIUM").sum())
    low_items = int((df["risk"] == "LOW").sum())
    total_items = len(df)
    avg_priority = round(float(df["priority_score"].mean()), 1)
else:
    high_items = 0
    med_items = 0
    low_items = 0
    total_items = 0
    avg_priority = 0.0

# =========================================================
# KPI ROW
# =========================================================
k1, k2, k3, k4 = st.columns(4)

with k1:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Total Alerts</div>
            <div class="metric-value">{total_alerts}</div>
            <div class="metric-note">Current filtered operational picture</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with k2:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">High Risk</div>
            <div class="metric-value">{high_alerts}</div>
            <div class="metric-note">Immediate review candidates</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with k3:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Medium Risk</div>
            <div class="metric-value">{medium_alerts}</div>
            <div class="metric-note">Items requiring enhanced monitoring</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with k4:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Avg Priority</div>
            <div class="metric-value">{avg_priority}</div>
            <div class="metric-note">Mean score across active alerts</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# =========================================================
# SEVERITY TREND CHART
# =========================================================
st.markdown('<div class="section-title">Threat Activity Over Time</div>', unsafe_allow_html=True)

if not df.empty:
    trend_df = df.copy()
    trend_df["hour"] = trend_df["published_at"].dt.floor("h")
    grouped = trend_df.groupby(["hour", "risk"]).size().reset_index(name="count")

    fig = px.line(
        grouped,
        x="hour",
        y="count",
        color="risk",
        markers=True,
    )
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15,23,42,0.65)",
        height=350,
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis_title="Time",
        yaxis_title="Incident Count",
        legend_title="Risk Level",
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="rgba(148,163,184,0.12)")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No data available for trend analysis.")

# =========================================================
# MAIN LAYOUT
# =========================================================
left_col, right_col = st.columns([1.35, 0.95])

with left_col:
    st.markdown('<div class="section-title">Geospatial Incident Map</div>', unsafe_allow_html=True)
    threat_map = make_map(df)
    st_folium(threat_map, width=None, height=560)

with right_col:
    st.markdown('<div class="section-title">Analyst Briefing</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="brief-box">{html.escape(briefing)}</div>', unsafe_allow_html=True)

    st.markdown('<div class="divider-space"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Executive Export</div>', unsafe_allow_html=True)

    if st.button("Generate PDF Brief"):
        pdf_path = generate_pdf_brief(briefing)
        st.success("Executive brief generated.")
        with open(pdf_path, "rb") as f:
            st.download_button(
                label="Download Executive Brief",
                data=f,
                file_name="NYC_Executive_Threat_Brief.pdf",
                mime="application/pdf",
            )

# =========================================================
# TABS
# =========================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Overview",
    "Threat Map",
    "Alerts",
    "Analyst Brief",
    "Executive Export"
])

with tab1:
    left, right = st.columns([1.3, 1])

    with left:
        st.markdown('<div class="panel-title">Operational Snapshot</div>', unsafe_allow_html=True)
        if not df.empty:
            top_cols = ["alert_id", "title", "location", "risk", "priority", "priority_score"]
            available_cols = [c for c in top_cols if c in df.columns]
            st.dataframe(
                df[available_cols].head(8),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No alerts match the current filters.")

    with right:
        st.markdown('<div class="panel-title">Monitoring Assessment</div>', unsafe_allow_html=True)
        if high_alerts > 0:
            st.error("Immediate review recommended. High-risk items are present in the current operating picture.")
        elif medium_alerts > 0:
            st.warning("Elevated monitoring posture advised. Conditions may affect venue access, crowd flow, or transport continuity.")
        else:
            st.success("Routine monitoring posture remains appropriate in the current filtered view.")

with tab2:
    st.markdown('<div class="section-title">Top Risk Drivers</div>', unsafe_allow_html=True)

    if df.empty:
        st.info("No data to analyse.")
    else:
        term_series = (
            df["matched_terms"]
            .fillna("")
            .str.split(", ")
            .explode()
            .replace("", pd.NA)
            .dropna()
        )

        if term_series.empty:
            st.info("No risk-driving keywords matched in the current view.")
        else:
            term_counts = term_series.value_counts().reset_index()
            term_counts.columns = ["term", "count"]
            st.dataframe(term_counts, use_container_width=True, hide_index=True)

        st.markdown('<div class="divider-space"></div>', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Geographic Concentration</div>', unsafe_allow_html=True)
        loc_counts = df["location"].value_counts().reset_index()
        loc_counts.columns = ["location", "count"]
        st.dataframe(loc_counts, use_container_width=True, hide_index=True)
        
        st.markdown('<div class="panel-title">Geospatial Threat View</div>', unsafe_allow_html=True)
        st.caption("Venue proximity, borough-level activity, and incident concentration across the current filter set.")
        st_folium(threat_map, use_container_width=True, height=650)

with tab3:
    left, right = st.columns([1.5, 1])

    with left:
        st.markdown('<div class="panel-title">Alert Queue</div>', unsafe_allow_html=True)
        if not df.empty:
            preferred_cols = [
                "alert_id", "title", "source", "location",
                "risk", "priority", "priority_score", "age_hours"
            ]
            available_cols = [c for c in preferred_cols if c in df.columns]
            st.dataframe(
                df[available_cols],
                use_container_width=True,
                hide_index=True,
                height=520
            )
        else:
            st.info("No alerts available for the current selection.")

    with right:
        st.markdown('<div class="panel-title">Top Priority Items</div>', unsafe_allow_html=True)
        if not df.empty:
            ranked = df.sort_values("priority_score", ascending=False).head(5)
            for _, row in ranked.iterrows():
                st.markdown(
                    f"""
                    <div class="panel" style="margin-bottom:0.75rem;">
                        <strong>{row.get('alert_id', 'N/A')}</strong><br>
                        <span style="font-size:0.95rem;color:#f8fafc;">{row.get('title', 'Untitled alert')}</span><br>
                        <span style="color:#94a3b8;font-size:0.82rem;">
                            {row.get('location', 'Unknown location')} · {row.get('risk', 'N/A')} · {row.get('priority', 'N/A')}
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.info("No priority items to display.")
with tab4:
    st.markdown('<div class="section-title">Raw Intelligence Feed</div>', unsafe_allow_html=True)

    if df_all.empty:
        st.info("No raw items available.")
    else:
        raw_df = df_all.copy()
        raw_df["published_at"] = raw_df["published_at"].dt.strftime("%Y-%m-%d %H:%M UTC")

        if not show_raw_feed:
            st.info("Enable 'Show raw feed table' in the sidebar to display the full feed.")
        else:
            st.dataframe(
                raw_df[
                    [
                        "alert_id",
                        "published_at",
                        "source",
                        "feed_type",
                        "risk",
                        "risk_score",
                        "priority",
                        "priority_score",
                        "event_related",
                        "location",
                        "title",
                        "summary",
                        "matched_terms",
                        "url",
                    ]
                ],
                use_container_width=True,
                hide_index=True,
            )
with tab5:
    st.markdown('<div class="panel-title">Executive Reporting</div>', unsafe_allow_html=True)
    st.caption("Export a concise leadership-ready briefing for operational awareness and decision support.")

    export_col1, export_col2 = st.columns([1, 2])

    with export_col1:
        if st.button("Generate PDF Briefing", use_container_width=True):
            st.success("PDF briefing generated successfully.")

    with export_col2:
        st.markdown(
            """
            <div class="panel">
                <strong>Recommended contents</strong><br><br>
                • Current monitoring posture<br>
                • Highest priority incidents<br>
                • Venue and transit impacts<br>
                • Recommended operational actions
            </div>
            """,
            unsafe_allow_html=True
        )
# =========================================================
# FOOTER
# =========================================================
st.markdown("---")
st.markdown(
    '<div class="small-muted">This dashboard simulates how security intelligence teams monitor open-source reporting relevant to concerts, sports events, public gatherings, and live productions in New York City. It combines OSINT collection, weighted risk scoring, venue watchlisting, geospatial context, alert prioritisation, and briefing outputs to support protective security decision-making.</div>',
    unsafe_allow_html=True,
)
