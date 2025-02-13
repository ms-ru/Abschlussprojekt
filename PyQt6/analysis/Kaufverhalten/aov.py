# Standard libaries
import pandas as pd
import plotly.express as px
import shutil  # Für Sicherungskopien
from pathlib import Path

# Speicherpfad für Analyse-Ergebnisse
BASE_DIR = Path("/Users/marcus/Documents/GitHub/Abschlussprojekt/main_project/PyQt6/analysis/analysis_results")
BASE_DIR.mkdir(parents=True, exist_ok=True)  # Verzeichnis automatisch erstellen

def generate_aov_analysis(df):
    """Führt die AOV-Analyse mit den geladenen Daten durch."""
    
    if df is None or df.empty:
        print("⚠️ Keine gültigen Daten für AOV-Analyse vorhanden!")
        return {}

    df["Date"] = pd.to_datetime(df["Date"])

    # Durchschnittlicher Bestellwert pro Bestellung berechnen*
    aov_per_order = df.groupby("Transaction ID")["Revenue"].sum().reset_index()
    aov_per_order.columns = ["Transaction ID", "AOV"]

    # AOV-Entwicklung über die Zeit
    df["Month"] = df["Date"].dt.to_period("M").astype(str)  
    aov_trend = df.groupby("Month")["Revenue"].mean().reset_index()
    aov_trend.columns = ["Month", "Avg_Order_Value"]

    # Visualisierungen erstellen
    
    # AOV-Trend über die Zeit
    fig1 = px.line(
        aov_trend, x="Month", y="Avg_Order_Value",
        title="📅 AOV-Entwicklung über die Zeit",
        markers=True, line_shape="spline", color_discrete_sequence=["#FF5733"]
    )
    fig1.update_layout(template="plotly_dark")

    # AOV-Verteilung nach Bestellungen
    fig2 = px.histogram(
        aov_per_order, x="AOV", nbins=50,
        title="💰 Verteilung des durchschnittlichen Bestellwerts",
        color_discrete_sequence=["#FFC300"]
    )
    fig2.update_layout(template="plotly_dark")

    # AOV nach Industrie
    fig3 = None
    if "Industry" in df.columns:
        industry_aov = df.groupby("Industry")["Revenue"].mean().reset_index()
        industry_aov.columns = ["Industry", "Avg_Order_Value"]
        fig3 = px.bar(
            industry_aov, x="Industry", y="Avg_Order_Value",
            title="🏢 AOV nach Branche",
            color="Avg_Order_Value", color_continuous_scale="Viridis"
        )
        fig3.update_layout(template="plotly_dark")

    # AOV nach Vertriebskanal
    fig4 = None
    if "Purchase Channel" in df.columns:
        channel_aov = df.groupby("Purchase Channel")["Revenue"].mean().reset_index()
        channel_aov.columns = ["Purchase Channel", "Avg_Order_Value"]
        fig4 = px.bar(
            channel_aov, x="Purchase Channel", y="Avg_Order_Value",
            title="📦 AOV nach Vertriebskanal",
            color="Avg_Order_Value", color_continuous_scale="Blues"
        )
        fig4.update_layout(template="plotly_dark")

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
    aov_trend_path = BASE_DIR / "aov_trend.html"
    aov_distribution_path = BASE_DIR / "aov_distribution.html"
    aov_industry_path = BASE_DIR / "aov_industry.html"
    aov_channel_path = BASE_DIR / "aov_channel.html"

    # Speichere Diagramme mit Backup-Funktion
    save_chart(fig1, aov_trend_path)
    save_chart(fig2, aov_distribution_path)
    save_chart(fig3, aov_industry_path)
    save_chart(fig4, aov_channel_path)

    return {
        "AOV-Entwicklung über Zeit": str(aov_trend_path),
        "Verteilung des AOV": str(aov_distribution_path),
        "AOV nach Industrie": str(aov_industry_path) if fig3 else None,
        "AOV nach Vertriebskanal": str(aov_channel_path) if fig4 else None,
    }

print("✅ AOV-Analyse bereit zur Nutzung in der Anwendung.")