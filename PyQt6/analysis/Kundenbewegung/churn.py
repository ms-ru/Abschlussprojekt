# Standard Libaries
import pandas as pd
import plotly.express as px
import shutil  # Für Sicherungskopien

from pathlib import Path

# Speicherpfad für Analyse-Ergebnisse
BASE_DIR = Path("/Users/marcus/Documents/GitHub/Abschlussprojekt/main_project/PyQt6/analysis/analysis_results")
BASE_DIR.mkdir(parents=True, exist_ok=True)  # Verzeichnis automatisch erstellen

def generate_churn_analysis(df):
    """Führt die Churn-Analyse mit den übergebenen Daten durch."""
    
    if df is None or df.empty:
        print("⚠️ Keine gültigen Daten für die Churn-Analyse vorhanden!")
        return {}

    df["Date"] = pd.to_datetime(df["Date"])

    # Stichtag setzen (letztes Kaufdatum im Datensatz)
    latest_date = df["Date"].max()

    # Letztes Kaufdatum pro Kunde berechnen
    last_purchase = df.groupby("Customer ID")["Date"].max().reset_index()
    last_purchase.columns = ["Customer ID", "Last Purchase"]

    # Zeit seit dem letzten Kauf berechnen
    last_purchase["Days_Since_Last_Purchase"] = (latest_date - last_purchase["Last Purchase"]).dt.days

    # Churn-Definition: Kunden, die seit 365+ Tagen nicht mehr gekauft haben
    last_purchase["Churned"] = last_purchase["Days_Since_Last_Purchase"].apply(lambda x: "Ja" if x > 365 else "Nein")

    # Churn-Rate berechnen
    churn_rate = last_purchase["Churned"].value_counts(normalize=True).reset_index()
    churn_rate.columns = ["Churned", "Percentage"]
    churn_rate["Percentage"] *= 100

    # Gesamt-Churn-Rate
    fig1 = px.pie(
        churn_rate, names="Churned", values="Percentage",
        title="📉 Gesamt-Churn-Rate",
        hole=0.4, color_discrete_sequence=["#FF5733", "#17BECF"]
    )
    fig1.update_layout(template="plotly_dark")

    # Churn nach Industrie analysieren
    fig2 = None
    if "Industry" in df.columns:
        df = df.merge(last_purchase[["Customer ID", "Churned"]], on="Customer ID", how="left")
        churn_by_industry = df.groupby("Industry")["Churned"].value_counts(normalize=True).unstack().reset_index()
        churn_by_industry.columns = ["Industry", "Nicht abgewandert", "Abgewandert"]
        churn_by_industry["Abgewandert"] *= 100  

        fig2 = px.bar(
            churn_by_industry, x="Industry", y="Abgewandert",
            title="🏢 Churn-Rate nach Branche",
            color="Abgewandert", color_continuous_scale="Magma"
        )
        fig2.update_layout(template="plotly_dark")

    # Churn nach Vertriebskanal analysieren
    fig3 = None
    if "Purchase Channel" in df.columns:
        churn_by_channel = df.groupby("Purchase Channel")["Churned"].value_counts(normalize=True).unstack().reset_index()
        churn_by_channel.columns = ["Purchase Channel", "Nicht abgewandert", "Abgewandert"]
        churn_by_channel["Abgewandert"] *= 100

        fig3 = px.bar(
            churn_by_channel, x="Purchase Channel", y="Abgewandert",
            title="📦 Churn-Rate nach Vertriebskanal",
            color="Abgewandert", color_continuous_scale="Blues"
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
    churn_rate_path = BASE_DIR / "churn_rate.html"
    churn_by_industry_path = BASE_DIR / "churn_by_industry.html"
    churn_by_channel_path = BASE_DIR / "churn_by_channel.html"

    # Speichern der Diagramme mit Backup
    save_chart(fig1, churn_rate_path)
    save_chart(fig2, churn_by_industry_path) if fig2 else None
    save_chart(fig3, churn_by_channel_path) if fig3 else None

    return {
        "Gesamt-Churn-Rate": str(churn_rate_path),
        "Churn-Rate nach Industrie": str(churn_by_industry_path) if fig2 else None,
        "Churn-Rate nach Vertriebskanal": str(churn_by_channel_path) if fig3 else None,
    }

print("✅ Churn-Analyse bereit zur Nutzung in der Anwendung.")
