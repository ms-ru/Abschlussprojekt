# Standard Libaries
import pandas as pd
import plotly.express as px
import shutil  # Für Sicherungskopien

from pathlib import Path

# Speicherpfad für Analyse-Ergebnisse
BASE_DIR = Path("/Users/marcus/Documents/GitHub/Abschlussprojekt/main_project/PyQt6/analysis/analysis_results")
BASE_DIR.mkdir(parents=True, exist_ok=True)  # Verzeichnis automatisch erstellen

def generate_survival_analysis(df):
    """Führt die Survival-Analyse mit den übergebenen Daten durch."""
    
    if df is None or df.empty:
        print("⚠️ Keine gültigen Daten für die Survival-Analyse vorhanden!")
        return {}

    df["Date"] = pd.to_datetime(df["Date"])

    # Stichtag setzen (letztes Kaufdatum im Datensatz)
    latest_date = df["Date"].max()

    # Letztes Kaufdatum pro Kunde berechnen
    last_purchase = df.groupby("Customer ID")["Date"].max().reset_index()
    last_purchase.columns = ["Customer ID", "Last Purchase"]

    # Zeit seit dem letzten Kauf berechnen
    last_purchase["Days_Since_Last_Purchase"] = (latest_date - last_purchase["Last Purchase"]).dt.days

    # Survival-Definition: Kunden, die zwischen 180 und 365 Tagen nicht mehr gekauft haben
    last_purchase["Survival"] = last_purchase["Days_Since_Last_Purchase"].apply(lambda x: "Ja" if 180 <= x <= 365 else "Nein")

    # Survival-Rate berechnen**
    survival_rate = last_purchase["Survival"].value_counts(normalize=True).reset_index()
    survival_rate.columns = ["Survival", "Percentage"]
    survival_rate["Percentage"] *= 100

    # Gesamt-Survival-Rate
    fig1 = px.pie(
        survival_rate, names="Survival", values="Percentage",
        title="📉 Gesamt-Survival-Rate",
        hole=0.4, color_discrete_sequence=["#FFA07A", "#4682B4"]
    )
    fig1.update_layout(template="plotly_dark")

    # Survival nach Industrie analysieren
    fig2 = None
    if "Industry" in df.columns:
        df = df.merge(last_purchase[["Customer ID", "Survival"]], on="Customer ID", how="left")
        survival_by_industry = df.groupby("Industry")["Survival"].value_counts(normalize=True).unstack().reset_index()
        survival_by_industry.columns = ["Industry", "Aktiv", "Inaktiv"]
        survival_by_industry["Inaktiv"] *= 100  

        fig2 = px.bar(
            survival_by_industry, x="Industry", y="Inaktiv",
            title="🏢 Survival-Rate nach Branche",
            color="Inaktiv", color_continuous_scale="Magma"
        )
        fig2.update_layout(template="plotly_dark")

    # Survival nach Vertriebskanal analysieren
    fig3 = None
    if "Purchase Channel" in df.columns:
        survival_by_channel = df.groupby("Purchase Channel")["Survival"].value_counts(normalize=True).unstack().reset_index()
        survival_by_channel.columns = ["Purchase Channel", "Aktiv", "Inaktiv"]
        survival_by_channel["Inaktiv"] *= 100

        fig3 = px.bar(
            survival_by_channel, x="Purchase Channel", y="Inaktiv",
            title="📦 Survival-Rate nach Vertriebskanal",
            color="Inaktiv", color_continuous_scale="Blues"
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
    survival_rate_path = BASE_DIR / "survival_rate.html"
    survival_by_industry_path = BASE_DIR / "survival_by_industry.html"
    survival_by_channel_path = BASE_DIR / "survival_by_channel.html"

    # Speichern der Diagramme mit Backup
    save_chart(fig1, survival_rate_path)
    save_chart(fig2, survival_by_industry_path) if fig2 else None
    save_chart(fig3, survival_by_channel_path) if fig3 else None

    return {
        "Gesamt-Survival-Rate": str(survival_rate_path),
        "Survival-Rate nach Industrie": str(survival_by_industry_path) if fig2 else None,
        "Survival-Rate nach Vertriebskanal": str(survival_by_channel_path) if fig3 else None,
    }

print("✅ Survival-Analyse bereit zur Nutzung in der Anwendung.")
