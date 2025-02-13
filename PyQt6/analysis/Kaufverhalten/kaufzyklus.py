# Standard libaries
import pandas as pd
import plotly.express as px
import shutil  # Für Sicherungskopien

from pathlib import Path


# Speicherpfad für Analyse-Ergebnisse
BASE_DIR = Path("/Users/marcus/Documents/GitHub/Abschlussprojekt/main_project/PyQt6/analysis/analysis_results")
BASE_DIR.mkdir(parents=True, exist_ok=True)  # Verzeichnis automatisch erstellen

def generate_kaufzyklus_analysis(df):
    """Führt die Kaufzyklusanalyse mit den übergebenen Daten durch."""
    
    if df is None or df.empty:
        print("⚠️ Keine gültigen Daten für die Kaufzyklusanalyse vorhanden!")
        return {}

    df["Date"] = pd.to_datetime(df["Date"])

    # Zeitliche Analyse: Abstand zwischen Käufen berechnen
    df["Prev_Purchase"] = df.sort_values(["Customer ID", "Date"]).groupby("Customer ID")["Date"].shift(1)
    df["Days_Between"] = (df["Date"] - df["Prev_Purchase"]).dt.days

    # Durchschnittlicher Kaufzyklus pro Kunde
    customer_cycle = df.groupby("Customer ID")["Days_Between"].mean().reset_index()
    customer_cycle.columns = ["Customer ID", "Avg_Days_Between"]

    # Kaufhäufigkeit pro Monat berechnen
    df["Month"] = df["Date"].dt.to_period("M").astype(str)  
    monthly_sales = df.groupby("Month")["Customer ID"].count().reset_index()
    monthly_sales.columns = ["Month", "Total Purchases"]

    # Kaufhäufigkeit pro Monat
    fig1 = px.line(
        monthly_sales, x="Month", y="Total Purchases",
        title="📅 Kaufaktivität pro Monat",
        markers=True, line_shape="spline"
    )
    fig1.update_layout(template="plotly_dark")

    # Verteilung der Kaufzyklen
    fig2 = px.histogram(
        customer_cycle, x="Avg_Days_Between", nbins=50,
        title="⏳ Verteilung der Kaufzyklen",
        color_discrete_sequence=["#17BECF"]
    )
    fig2.update_layout(template="plotly_dark")

    # Kaufzyklen nach Segmenten 
    fig3 = None
    if "Industry" in df.columns:
        df = df.merge(customer_cycle, on="Customer ID", how="left")
        segment_cycle = df.groupby("Industry")["Avg_Days_Between"].mean().reset_index()
        fig3 = px.bar(
            segment_cycle, x="Industry", y="Avg_Days_Between",
            title="🏢 Durchschnittlicher Kaufzyklus nach Branche",
            color="Avg_Days_Between", color_continuous_scale="Viridis"
        )
        fig3.update_layout(template="plotly_dark")

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
    kaufzyklus_trend_path = BASE_DIR / "kaufzyklus_trend.html"
    kaufzyklus_distribution_path = BASE_DIR / "kaufzyklus_distribution.html"
    kaufzyklus_segments_path = BASE_DIR / "kaufzyklus_segments.html"

    # Speichern derDiagramme mit Backup
    save_chart(fig1, kaufzyklus_trend_path)
    save_chart(fig2, kaufzyklus_distribution_path)
    save_chart(fig3, kaufzyklus_segments_path)

    return {
        "Kaufaktivität pro Monat": str(kaufzyklus_trend_path),
        "Verteilung der Kaufzyklen": str(kaufzyklus_distribution_path),
        "Kaufzyklen nach Segmenten": str(kaufzyklus_segments_path) if fig3 else None,
    }

print("✅ Kaufzyklusanalyse bereit zur Nutzung in der Anwendung.")
