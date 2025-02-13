# Standard Libaries
import pandas as pd
import plotly.express as px
import shutil  # Für Sicherungskopien

from pathlib import Path

# Speicherpfad für Analyse-Ergebnisse
BASE_DIR = Path("/Users/marcus/Documents/GitHub/Abschlussprojekt/main_project/PyQt6/analysis/analysis_results")
BASE_DIR.mkdir(parents=True, exist_ok=True)  # Verzeichnis automatisch erstellen

def generate_dormant_analysis(df):
    """Führt die Inaktivitätsanalyse mit den übergebenen Daten durch."""
    
    if df is None or df.empty:
        print("⚠️ Keine gültigen Daten für die Inaktivitätsanalyse vorhanden!")
        return {}

    df["Date"] = pd.to_datetime(df["Date"])

    # Stichtag setzen (letztes Kaufdatum im Datensatz)
    latest_date = df["Date"].max()

    # Letztes Kaufdatum pro Kunde berechnen
    last_purchase = df.groupby("Customer ID")["Date"].max().reset_index()
    last_purchase.columns = ["Customer ID", "Last Purchase"]

    # Zeit seit dem letzten Kauf berechnen
    last_purchase["Days_Since_Last_Purchase"] = (latest_date - last_purchase["Last Purchase"]).dt.days

    # Inaktivitäts-Definition: Kunden, die zwischen 180 und 365 Tagen nicht mehr gekauft haben
    last_purchase["Dormant"] = last_purchase["Days_Since_Last_Purchase"].apply(lambda x: "Ja" if 180 <= x <= 365 else "Nein")

    # Inaktivitätsrate berechnen
    dormant_rate = last_purchase["Dormant"].value_counts(normalize=True).reset_index()
    dormant_rate.columns = ["Dormant", "Percentage"]
    dormant_rate["Percentage"] *= 100

    # Gesamt-Inaktivitätsrate
    fig1 = px.pie(
        dormant_rate, names="Dormant", values="Percentage",
        title="📉 Gesamt-Inaktivitätsrate",
        hole=0.4, color_discrete_sequence=["#FFA07A", "#4682B4"]
    )
    fig1.update_layout(template="plotly_dark")

    # Inaktivität nach Industrie analysieren
    fig2 = None
    if "Industry" in df.columns:
        df = df.merge(last_purchase[["Customer ID", "Dormant"]], on="Customer ID", how="left")
        dormant_by_industry = df.groupby("Industry")["Dormant"].value_counts(normalize=True).unstack().reset_index()
        dormant_by_industry.columns = ["Industry", "Aktiv", "Inaktiv"]
        dormant_by_industry["Inaktiv"] *= 100  

        fig2 = px.bar(
            dormant_by_industry, x="Industry", y="Inaktiv",
            title="🏢 Inaktivitätsrate nach Branche",
            color="Inaktiv", color_continuous_scale="Magma"
        )
        fig2.update_layout(template="plotly_dark")

    # Inaktivität nach Vertriebskanal analysieren
    fig3 = None
    if "Purchase Channel" in df.columns:
        dormant_by_channel = df.groupby("Purchase Channel")["Dormant"].value_counts(normalize=True).unstack().reset_index()
        dormant_by_channel.columns = ["Purchase Channel", "Aktiv", "Inaktiv"]
        dormant_by_channel["Inaktiv"] *= 100

        fig3 = px.bar(
            dormant_by_channel, x="Purchase Channel", y="Inaktiv",
            title="📦 Inaktivitätsrate nach Vertriebskanal",
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
    dormant_rate_path = BASE_DIR / "dormant_rate.html"
    dormant_by_industry_path = BASE_DIR / "dormant_by_industry.html"
    dormant_by_channel_path = BASE_DIR / "dormant_by_channel.html"

    # Speichern der Diagramme mit Backup
    save_chart(fig1, dormant_rate_path)
    save_chart(fig2, dormant_by_industry_path) if fig2 else None
    save_chart(fig3, dormant_by_channel_path) if fig3 else None

    return {
        "Gesamt-Inaktivitätsrate": str(dormant_rate_path),
        "Inaktivitätsrate nach Industrie": str(dormant_by_industry_path) if fig2 else None,
        "Inaktivitätsrate nach Vertriebskanal": str(dormant_by_channel_path) if fig3 else None,
    }

print("✅ Inaktivitätsanalyse bereit zur Nutzung in der Anwendung.")
