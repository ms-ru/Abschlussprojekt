# Standard Libaries
import pandas as pd
import plotly.express as px
import shutil  # Für Sicherungskopien

from pathlib import Path

# Speicherpfad für Analyse-Ergebnisse
BASE_DIR = Path("/Users/marcus/Documents/GitHub/Abschlussprojekt/main_project/PyQt6/analysis/analysis_results")
BASE_DIR.mkdir(parents=True, exist_ok=True)  # Verzeichnis automatisch erstellen

def generate_clv_analysis(df):
    """Führt die CLV-Analyse mit den übergebenen Daten durch."""
    
    if df is None or df.empty:
        print("⚠️ Keine gültigen Daten für die CLV-Analyse vorhanden!")
        return {}

    df["Date"] = pd.to_datetime(df["Date"])

    # Berechnung der Kundenwerte
    customer_revenue = df.groupby("Customer ID")["Revenue"].sum().reset_index()
    customer_revenue.columns = ["Customer ID", "Total Revenue"]

    customer_frequency = df.groupby("Customer ID")["Transaction ID"].count().reset_index()
    customer_frequency.columns = ["Customer ID", "Total Transactions"]

    customer_lifespan = df.groupby("Customer ID")["Date"].agg(["min", "max"]).reset_index()
    customer_lifespan["Customer Lifetime"] = (customer_lifespan["max"] - customer_lifespan["min"]).dt.days
    customer_lifespan = customer_lifespan[["Customer ID", "Customer Lifetime"]]

    # Customer Lifetime Value berechnen
    clv_df = customer_revenue.merge(customer_frequency, on="Customer ID").merge(customer_lifespan, on="Customer ID")
    clv_df["CLV"] = (clv_df["Total Revenue"] / clv_df["Total Transactions"]) * (clv_df["Customer Lifetime"] / 30)  # Monatlicher CLV

    # CLV nach Segment visualisieren
    fig1 = px.histogram(
        clv_df, x="CLV", nbins=50, title="📊 Verteilung des Customer Lifetime Value",
        color_discrete_sequence=["#FF5733"]
    )
    fig1.update_layout(template="plotly_dark")

    # CLV nach Kundenlebensdauer
    fig2 = px.scatter(
        clv_df, x="Customer Lifetime", y="CLV",
        title="📈 CLV im Verhältnis zur Kundenlebensdauer",
        color="CLV", color_continuous_scale="Viridis"
    )
    fig2.update_layout(template="plotly_dark")

    # CLV nach Umsatzgruppen
    clv_df["Revenue Segment"] = pd.qcut(clv_df["Total Revenue"], q=4, labels=["Low", "Mid", "High", "Top"])
    fig3 = px.box(
        clv_df, x="Revenue Segment", y="CLV",
        title="💰 CLV nach Umsatzsegmenten",
        color="Revenue Segment"
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
    clv_distribution_path = BASE_DIR / "clv_distribution.html"
    clv_vs_lifetime_path = BASE_DIR / "clv_vs_lifetime.html"
    clv_by_segment_path = BASE_DIR / "clv_by_segment.html"

    # Speichern der Diagramme mit Backup
    save_chart(fig1, clv_distribution_path)
    save_chart(fig2, clv_vs_lifetime_path)
    save_chart(fig3, clv_by_segment_path)

    return {
        "Verteilung des Customer Lifetime Value": str(clv_distribution_path),
        "CLV im Verhältnis zur Kundenlebensdauer": str(clv_vs_lifetime_path),
        "CLV nach Umsatzsegmenten": str(clv_by_segment_path),
    }

print("✅ CLV-Analyse bereit zur Nutzung in der Anwendung.")
