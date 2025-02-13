# Standard Libaries
import pandas as pd
import plotly.express as px
import shutil  # Für Sicherungskopien

from pathlib import Path

# Speicherpfad für Analyse-Ergebnisse
BASE_DIR = Path("/Users/marcus/Documents/GitHub/Abschlussprojekt/main_project/PyQt6/analysis/analysis_results")
BASE_DIR.mkdir(parents=True, exist_ok=True)  # Verzeichnis automatisch erstellen

def generate_segment_analysis(df):
    """Führt die Segmentanalyse mit den übergebenen Daten durch."""
    
    if df is None or df.empty:
        print("⚠️ Keine gültigen Daten für die Segmentanalyse vorhanden!")
        return {}

    # Revenue Segment
    if "Revenue Segment" not in df.columns:
        revenue_quantiles = df["Revenue"].quantile([0.2, 0.8])
        df["Revenue Segment"] = df["Revenue"].apply(
            lambda x: "High-Value" if x >= revenue_quantiles[0.8]
            else "Mid-Tier" if x >= revenue_quantiles[0.2]
            else "Low-Value"
        )

    df["Date"] = pd.to_datetime(df["Date"])

    # Sunburst-Diagramm für Umsatz-Segmentierung
    revenue_counts = df["Revenue Segment"].value_counts().reset_index()
    revenue_counts.columns = ["Revenue Segment", "Count"]
    fig1 = px.sunburst(
        revenue_counts, path=["Revenue Segment"], values="Count",
        title="Umsatzbasierte Segmente",
        color="Count", color_continuous_scale="Blues"
    )
    fig1.update_layout(template="plotly_dark")

    # Treemap für Branchen-Segmentierung
    fig2 = None
    if "Industry" in df.columns:
        industry_counts = df.groupby("Industry")["Customer ID"].count().reset_index()
        industry_counts.columns = ["Industry", "Customer Count"]
        fig2 = px.treemap(
            industry_counts, path=["Industry"], values="Customer Count",
            title="Kunden nach Branche", color="Customer Count",
            color_continuous_scale="Viridis"
        )
        fig2.update_layout(template="plotly_dark")

    # Choroplethenkarte für Länder-Segmentierung
    fig3 = None
    if "Country" in df.columns:
        country_counts = df.groupby("Country")["Customer ID"].count().reset_index()
        country_counts.columns = ["Country", "Customer Count"]
        fig3 = px.choropleth(
            country_counts, locations="Country", locationmode="country names",
            color="Customer Count", hover_name="Country",
            color_continuous_scale="Plasma", title="Kundenverteilung nach Ländern"
        )
        fig3.update_layout(template="plotly_dark")

    # Donut-Chart für Vertriebskanal-Segmentierung
    fig4 = None
    if "Purchase Channel" in df.columns:
        channel_counts = df.groupby("Purchase Channel")["Customer ID"].count().reset_index()
        channel_counts.columns = ["Purchase Channel", "Customer Count"]
        fig4 = px.pie(
            channel_counts, names="Purchase Channel", values="Customer Count",
            title="Kunden nach Vertriebskanal", hole=0.4,
            color_discrete_sequence=px.colors.sequential.Teal
        )
        fig4.update_layout(template="plotly_dark")

    # Umsatz-Segmente über die Zeit
    segment_trends = df.groupby([df["Date"].dt.to_period("M"), "Revenue Segment"])["Customer ID"].count().reset_index()
    segment_trends["Date"] = segment_trends["Date"].astype(str)
    fig5 = px.line(
        segment_trends, x="Date", y="Customer ID", color="Revenue Segment",
        title="Segmentverlauf über die Zeit",
        markers=True, line_shape="spline"
    )
    fig5.update_layout(template="plotly_dark")

    # Marktsegmentierung über die Zeit
    fig6 = None
    if "Industry" in df.columns:
        industry_trends = df.groupby([df["Date"].dt.to_period("M"), "Industry"])["Customer ID"].count().reset_index()
        industry_trends["Date"] = industry_trends["Date"].astype(str)
        fig6 = px.line(
            industry_trends, x="Date", y="Customer ID", color="Industry",
            title="Industrie-Segmentierung über die Zeit",
            markers=True, line_shape="spline"
        )
        fig6.update_layout(template="plotly_dark")

    # Sicherstellen, dass der Speicherordner existiert & Backups erstellen
    def save_chart(fig, file_path):
        if fig:
            if file_path.exists():
                backup_path = file_path.with_suffix(".backup.html")
                shutil.move(file_path, backup_path)  # Bestehende Datei sichern
                print(f"📂 Bestehende Datei gesichert: {backup_path}")

            fig.write_html(file_path)
            print(f"✅ Diagramm gespeichert: {file_path}")

    # Speicherpfade
    segment_sunburst_path = BASE_DIR / "segment_sunburst.html"
    industry_treemap_path = BASE_DIR / "industry_treemap.html"
    country_map_path = BASE_DIR / "country_map.html"
    purchase_channel_path = BASE_DIR / "purchase_channel.html"
    segment_trends_path = BASE_DIR / "segment_trends.html"
    industry_trends_path = BASE_DIR / "industry_trends.html"

    # Speichern der Diagramme mit Backup-Funktion
    save_chart(fig1, segment_sunburst_path)
    save_chart(fig2, industry_treemap_path) if fig2 else None
    save_chart(fig3, country_map_path) if fig3 else None
    save_chart(fig4, purchase_channel_path) if fig4 else None
    save_chart(fig5, segment_trends_path)
    save_chart(fig6, industry_trends_path) if fig6 else None

    return {
        "Segment Sunburst": str(segment_sunburst_path),
        "Branchen-Treemap": str(industry_treemap_path) if fig2 else None,
        "Länderkarte": str(country_map_path) if fig3 else None,
        "Vertriebskanäle": str(purchase_channel_path) if fig4 else None,
        "Segment-Trends": str(segment_trends_path),
        "Industrie-Trends": str(industry_trends_path) if fig6 else None,
    }

print("✅ Segmentanalyse bereit zur Nutzung in der Anwendung.")
