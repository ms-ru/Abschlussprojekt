# Standard Libaries
import pandas as pd
import plotly.express as px
import shutil  # Für Sicherungskopien

from pathlib import Path

# Speicherpfad für Analyse-Ergebnisse
BASE_DIR = Path("/Users/marcus/Documents/GitHub/Abschlussprojekt/main_project/PyQt6/analysis/analysis_results")
BASE_DIR.mkdir(parents=True, exist_ok=True)  # Verzeichnis automatisch erstellen

def generate_benchmark_analysis(df):
    """Führt die Benchmark-Analyse mit den übergebenen Daten durch."""
    
    if df is None or df.empty:
        print("⚠️ Keine gültigen Daten für die Benchmark-Analyse vorhanden!")
        return {}

    df["Date"] = pd.to_datetime(df["Date"])

    # Umsatz- und Absatzstatistiken pro Branche berechnen
    fig1, fig2, fig3, fig4 = None, None, None, None

    if "Industry" in df.columns:
        benchmark_industry = df.groupby("Industry").agg(
            Total_Revenue=("Revenue", "sum"),
            Avg_Revenue_Per_Customer=("Revenue", "mean"),
            Total_Sales=("Transaction ID", "count"),
        ).reset_index()

        # Gesamtumsatz nach Branche
        fig1 = px.bar(
            benchmark_industry, x="Industry", y="Total_Revenue",
            title="📊 Gesamtumsatz nach Branche",
            color="Total_Revenue", color_continuous_scale="Viridis"
        )
        fig1.update_layout(template="plotly_dark")

        # Durchschnittlicher Umsatz pro Kunde in jeder Branche
        fig2 = px.bar(
            benchmark_industry, x="Industry", y="Avg_Revenue_Per_Customer",
            title="📈 Durchschnittlicher Umsatz pro Kunde nach Branche",
            color="Avg_Revenue_Per_Customer", color_continuous_scale="Magma"
        )
        fig2.update_layout(template="plotly_dark")

        # Anzahl der Verkäufe pro Branche
        fig3 = px.bar(
            benchmark_industry, x="Industry", y="Total_Sales",
            title="📦 Gesamtverkäufe nach Branche",
            color="Total_Sales", color_continuous_scale="Blues"
        )
        fig3.update_layout(template="plotly_dark")

    if "Purchase Channel" in df.columns:
        # Vergleich nach Vertriebskanal
        benchmark_channel = df.groupby("Purchase Channel").agg(
            Total_Revenue=("Revenue", "sum"),
            Avg_Revenue_Per_Customer=("Revenue", "mean"),
            Total_Sales=("Transaction ID", "count"),
        ).reset_index()

        fig4 = px.bar(
            benchmark_channel, x="Purchase Channel", y="Total_Revenue",
            title="🛒 Gesamtumsatz nach Vertriebskanal",
            color="Total_Revenue", color_continuous_scale="Plasma"
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
    benchmark_revenue_path = BASE_DIR / "benchmark_revenue.html"
    benchmark_avg_revenue_path = BASE_DIR / "benchmark_avg_revenue.html"
    benchmark_total_sales_path = BASE_DIR / "benchmark_total_sales.html"
    benchmark_revenue_channel_path = BASE_DIR / "benchmark_revenue_channel.html"

    # Speichern der Diagramme mit Backup
    save_chart(fig1, benchmark_revenue_path) if fig1 else None
    save_chart(fig2, benchmark_avg_revenue_path) if fig2 else None
    save_chart(fig3, benchmark_total_sales_path) if fig3 else None
    save_chart(fig4, benchmark_revenue_channel_path) if fig4 else None

    return {
        "Gesamtumsatz nach Branche": str(benchmark_revenue_path) if fig1 else None,
        "Durchschnittlicher Umsatz pro Kunde": str(benchmark_avg_revenue_path) if fig2 else None,
        "Gesamtverkäufe nach Branche": str(benchmark_total_sales_path) if fig3 else None,
        "Umsatz nach Vertriebskanal": str(benchmark_revenue_channel_path) if fig4 else None,
    }

print("✅ Benchmark-Analyse bereit zur Nutzung in der Anwendung.")
