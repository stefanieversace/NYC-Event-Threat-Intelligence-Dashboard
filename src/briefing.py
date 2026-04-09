from datetime import datetime, timezone


def generate_briefing(df):
    """
    Generates an analyst-style intelligence briefing from a dataframe of alerts.
    """

    if df is None or df.empty:
        return (
            "NYC EVENT INTELLIGENCE BRIEF\n\n"
            "No relevant incidents detected in the current monitoring window.\n"
            "Recommendation: Maintain baseline monitoring posture."
        )

    total = len(df)
    high = (df["risk"] == "HIGH").sum()
    medium = (df["risk"] == "MEDIUM").sum()
    low = (df["risk"] == "LOW").sum()

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # Top incidents
    top_incidents = df.head(5)

    # Location + source trends
    top_locations = df["location"].value_counts().head(3)
    top_sources = df["source"].value_counts().head(3)

    # Build briefing
    lines = []

    lines.append("🧠 NYC EVENT INTELLIGENCE BRIEF")
    lines.append(f"Generated: {now}")
    lines.append("")
    lines.append(f"Total Incidents: {total}")
    lines.append(f"Risk Breakdown: HIGH {high} | MEDIUM {medium} | LOW {low}")
    lines.append("")

    # =========================
    # EXECUTIVE ASSESSMENT
    # =========================
    if high > 0:
        lines.append("Executive Assessment:")
        lines.append(
            "Elevated threat environment detected. High-risk incidents may impact venue operations, crowd safety, or access routes."
        )
    elif medium > 0:
        lines.append("Executive Assessment:")
        lines.append(
            "Moderate operational risk. Ongoing monitoring required for potential disruptions affecting events or transport."
        )
    else:
        lines.append("Executive Assessment:")
        lines.append(
            "Low threat level. No significant disruptions currently affecting event operations."
        )

    lines.append("")

    # =========================
    # TOP INCIDENTS
    # =========================
    lines.append("Top Incidents:")

    for _, row in top_incidents.iterrows():
        lines.append(
            f"- [{row.get('alert_id', 'N/A')}] "
            f"{row.get('title', 'No title')} "
            f"({row.get('location', 'Unknown')}) | "
            f"Risk: {row.get('risk')} | "
            f"Priority: {row.get('priority')}"
        )

    lines.append("")

    # =========================
    # GEOGRAPHIC INSIGHT
    # =========================
    lines.append("Geographic Focus:")

    for loc, count in top_locations.items():
        lines.append(f"- {loc}: {count} incidents")

    lines.append("")

    # =========================
    # SOURCE INSIGHT
    # =========================
    lines.append("Most Active Sources:")

    for src, count in top_sources.items():
        lines.append(f"- {src}: {count} reports")

    lines.append("")

    # =========================
    # RECOMMENDATIONS
    # =========================
    lines.append("Operational Recommendations:")

    if high > 0:
        lines.append("- Escalate high-priority alerts to security leadership")
        lines.append("- Review venue access control and crowd management plans")
        lines.append("- Coordinate with law enforcement if required")
    elif medium > 0:
        lines.append("- Maintain enhanced monitoring for escalation indicators")
        lines.append("- Assess potential impact on transport and event access")
    else:
        lines.append("- Continue routine monitoring")
        lines.append("- Maintain situational awareness across venues")

    return "\n".join(lines)
