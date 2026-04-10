# 🗽 NYC Event Threat Intelligence Dashboard

A real-time threat intelligence and detection system designed to simulate Security Operations Center (SOC) workflows for monitoring risks across New York City.

This project combines:

- High-performance C++ detection engine
- Threat intelligence enrichment (MITRE ATT&CK mapping)
- Python-based analyst dashboard (Streamlit)

It is designed to replicate how security teams monitor risks to public events, infrastructure, and large venues.
---

## Key Capabilities

### OSINT Collection
- Aggregates data from RSS feeds and News APIs  
- Processes real-time information related to NYC events and incidents  

### Risk Scoring Engine
- Keyword-based threat detection model  
- Weighted scoring system (HIGH / MEDIUM / LOW)  
- Context-aware boosts (venues, NYC relevance)  

### Alerting & Prioritisation
- Sentinel-style alert ID generation  
- Priority scoring based on severity + recency  
- Classification: `IMMEDIATE`, `ELEVATED`, `ROUTINE+`, `MONITOR`  

### Geospatial Intelligence
- Maps incidents to NYC venues and boroughs  
- Highlights proximity to high-risk locations  
- Interactive map visualisation  

### Analyst Briefing Engine
- Generates structured intelligence reports  
- Summarises key incidents and trends  
- Provides operational recommendations  

### Executive Reporting
- One-click PDF export of intelligence briefings  
- Designed for leadership-level consumption  

---

## Architecture

```
Raw Logs / Event Data
        ↓
C++ Detection Engine (Brute force / anomaly detection)
        ↓
Structured Alerts (JSON)
        ↓
Python Dashboard (Streamlit)
        ↓
Analyst Insights & Visualisation
```

## Use Cases

### Protecting a Concert at Madison Square Garden
- Monitor crowd risk and surrounding incidents
- Detect threats affecting venue access
- Provide real-time situational awareness

### Monitoring Protests Near Times Square
- Track demonstrations and escalation signals
- Assess impact on events and crowd movement
- Support access control planning

### Assessing Transport Disruption Impact
- Identify subway delays and outages
- Evaluate impact on attendee ingress/egress
- Support contingency planning

## Dashboard Features
- Interactive threat map

- Severity trend analysis

- Venue watchlist filtering
  
- Incident feed with drill-down insights
  
- Analyst briefing panel
  
- Executive PDF export

## Example Alert
```
ALRT-9F3A1C7B2D
Risk: HIGH
Priority: IMMEDIATE
Location: Madison Square Garden

Incident:
Crowd surge reported outside venue before sold-out event

Impact:
Severe congestion and potential safety risk

Recommended Actions:
- Escalate to security command
- Deploy crowd management measures
- Coordinate with law enforcement
```

## Tech Stack

- Python
- Streamlit
- Pandas
- Plotly
- Folium
- Feedparser
- ReportLab

  
## Project Structure
```
nyc-event-threat-intel/
│
├── app.py
├── requirements.txt
├── README.md
├── data/
├── src/
├── notebooks/
├── assets/
└── docs/
```

## Running the Project
```
pip install -r requirements.txt
streamlit run app.py
```

## Design Philosophy

This system is built to reflect how real-world security teams operate:

- Intelligence-driven decision making
  
- Real-time situational awareness
  
- Event-focused risk assessment
  
- Operationally relevant outputs

## Future Enhancements

- MITRE ATT&CK mapping
  
- Machine learning-based threat classification
  
- Real-time alert notifications
  
- Integration with SIEM platforms (e.g. Microsoft Sentinel)

## Why This Project

This project demonstrates:

- End-to-end system design
  
- Security intelligence workflows
  
- OSINT analysis and risk assessment
  
- Ability to translate data into operational insight

## Author

Stefanie Versace

Security & Intelligence Analyst

## Final Note

This is not just a dashboard — it is a simulation of how security intelligence teams protect people, venues, and operations in complex urban environments.
