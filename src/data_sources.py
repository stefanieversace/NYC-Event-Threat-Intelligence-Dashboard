import requests
import feedparser
from datetime import datetime, timezone


# =========================
# FETCH RSS FEEDS
# =========================
def fetch_rss(limit_per_source=20):
    """
    Fetches articles from predefined RSS feeds.
    Returns a list of standardized event dictionaries.
    """

    RSS_FEEDS = {
        "Google News NYC": "https://news.google.com/rss/search?q=New+York&hl=en-US&gl=US&ceid=US:en",
        "NYC Events": "https://news.google.com/rss/search?q=New+York+concert+OR+stadium+OR+festival&hl=en-US&gl=US&ceid=US:en",
        "NYC Protests": "https://news.google.com/rss/search?q=New+York+protest&hl=en-US&gl=US&ceid=US:en",
        "Transit": "https://news.google.com/rss/search?q=New+York+subway+delay&hl=en-US&gl=US&ceid=US:en",
    }

    items = []

    for source_name, url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(url)

            for entry in feed.entries[:limit_per_source]:
                title = entry.get("title", "")
                summary = entry.get("summary", "")
                link = entry.get("link", "")

                published = entry.get("published", None)
                if published:
                    try:
                        published = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                    except:
                        published = datetime.now(timezone.utc)
                else:
                    published = datetime.now(timezone.utc)

                items.append({
                    "title": title,
                    "summary": summary,
                    "source": source_name,
                    "url": link,
                    "published_at": published,
                    "feed_type": "RSS"
                })

        except Exception as e:
            print(f"RSS error ({source_name}): {e}")
            continue

    return items


# =========================
# FETCH NEWSAPI
# =========================
def fetch_newsapi(api_key, limit=50):
    """
    Fetches articles from NewsAPI.
    Requires API key.
    Returns standardized event dictionaries.
    """

    if not api_key:
        return []

    url = "https://newsapi.org/v2/everything"

    query = (
        '"New York" OR NYC OR Manhattan OR Brooklyn '
        'AND (concert OR stadium OR protest OR event OR subway OR security)'
    )

    params = {
        "q": query,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": limit,
        "apiKey": api_key
    }

    items = []

    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()

        data = response.json()

        for article in data.get("articles", []):
            published = article.get("publishedAt", None)

            try:
                published = datetime.fromisoformat(published.replace("Z", "+00:00"))
            except:
                published = datetime.now(timezone.utc)

            items.append({
                "title": article.get("title", ""),
                "summary": (article.get("description", "") or "") + " " + (article.get("content", "") or ""),
                "source": article.get("source", {}).get("name", "NewsAPI"),
                "url": article.get("url", ""),
                "published_at": published,
                "feed_type": "NewsAPI"
            })

    except Exception as e:
        print(f"NewsAPI error: {e}")

    return items
