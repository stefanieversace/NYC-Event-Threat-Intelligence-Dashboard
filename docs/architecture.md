# 🏗️ Architecture

```text
Data Sources → Ingestion Layer → Processing Engine → Risk Scoring → Alerting → Dashboard UI
```

## 🔎 1. Data Sources

External open-source intelligence (OSINT) feeds:

RSS feeds (Google News, NYC events, protests, transit)
News APIs (NewsAPI)
Simulated intelligence data (for testing and demos)

## 📡 2. Ingestion Layer

Responsible for collecting and standardising raw data:

Fetches articles from multiple sources
Normalises fields (title, summary, timestamp)
Cleans text and removes HTML noise
Handles missing or inconsistent data

## ⚙️ 3. Processing Engine

Transforms raw data into structured intelligence:

Extracts keywords and entities
Identifies event relevance (concerts, venues, protests)
Infers geographic locations (MSG, Times Square, boroughs)
Maps incidents to operational context

## ⚠️ 4. Risk Scoring Engine

Assigns severity based on weighted logic:

Keyword-based threat detection
Weighted scoring model (HIGH / MEDIUM / LOW)
Contextual boosts (venue relevance, NYC indicators)
Generates risk score (0–100)

## 🚨 5. Alerting & Prioritisation

Simulates a SOC-style alert pipeline:

Generates unique alert IDs (Sentinel-style)
Calculates priority score (risk + recency)
Classifies alerts (IMMEDIATE, ELEVATED, MONITOR)
Produces recommended response actions

## 🧠 6. Intelligence Briefing Layer

Converts data into decision-ready insights:

Generates analyst-style briefings
Summarises top incidents and trends
Highlights geographic and source patterns
Provides operational recommendations

## 🖥️ 7. Dashboard UI (Streamlit)

User-facing interface for real-time monitoring:

Interactive map of incidents
Threat severity trend analysis
Venue watchlist filtering (MSG, Barclays, Times Square)
Incident feed with drill-down details
Executive PDF briefing export

## 🎯 Design Philosophy

This system is designed to simulate how security teams monitor and respond to threats in high-density environments such as:

Live events (concerts, sports games)
Media productions
Public gatherings in urban centres

## 💥 Why This Matters

This architecture demonstrates:

End-to-end system design
Clear separation of components
Real-world security and intelligence workflows

It reflects how modern security teams operate in dynamic environments.
