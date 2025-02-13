# Standard libaries
import pandas as pd
import plotly.express as px
import shutil  # Für Sicherungskopien

from pathlib import Path

# Speicherpfad für Analyse-Ergebnisse
BASE_DIR = Path("/Users/marcus/Documents/GitHub/Abschlussprojekt/main_project/PyQt6/analysis/analysis_results")
BASE_DIR.mkdir(parents=True, exist_ok=True)  # Verzeichnis automatisch erstellen

def generate_kohorten_analysis(df):
    """Führt die Kohortenanalyse mit den übergebenen Daten durch."""
    
    if df is None or df.empty:
        print("⚠️ Keine gültigen Daten für die Kohortenanalyse vorhanden!")
        return {}

    df["Date"] = pd.to_datetime(df["Date"])
    df["Year-Month"] = df["Date"].dt.to_period("M").astype(str)  # ✅ Fix für JSON-Speicherung

    # **📌 Kohorten identifizieren: Erstkauf für jeden Kunden**
    df["Cohort"] = df.groupby("Customer ID")["Year-Month"].transform("min")

    # **📌 Kohorten-Matrix erstellen**
    cohort_pivot = df.groupby(["Cohort", "Year-Month"])["Customer ID"].nunique().unstack().fillna(0)

    # **📌 Umwandlung in Prozentuale Retention-Rate**
    cohort_size = cohort_pivot.iloc[:, 0]  # Erste Spalte enthält Anzahl Erstkäufe pro Kohorte
    retention_matrix = cohort_pivot.divide(cohort_size, axis=0)

    # Heatmap der Kohorten-Analyse
    fig1 = px.imshow(
        retention_matrix, text_auto=".1%", color_continuous_scale="Blues",
        labels=dict(x="Monat", y="Kohorte", color="Retention-Rate"),
        title="📊 Kundenbindung & Kohortenanalyse"
    )
    fig1.update_layout(template="plotly_dark")

    # Entwicklung der Kohorten-Retention
    retention_trends = retention_matrix.mean(axis=0).reset_index()
    retention_trends.columns = ["Month", "Retention Rate"]

    fig2 = px.line(
        retention_trends, x="Month", y="Retention Rate",
        title="📈 Durchschnittliche Retention-Rate über Monate",
        markers=True, line_shape="spline"
    )
    fig2.update_layout(template="plotly_dark")

    # Kohorten nach Umsatz analysieren
    cohort_revenue = df.groupby(["Cohort", "Year-Month"])["Revenue"].sum().unstack().fillna(0)
    revenue_matrix = cohort_revenue.divide(cohort_size, axis=0)

    fig3 = px.imshow(
        revenue_matrix, text_auto=".2f", color_continuous_scale="Viridis",
        labels=dict(x="Monat", y="Kohorte", color="Umsatz pro Kunde"),
        title="💰 Umsatzentwicklung je Kohorte"
    )
    fig3.update_layout(template="plotly_dark")

    # Prüfen, dass der Speicherordner existiert 
    def save_chart(fig, file_path):
        if fig:
            if file_path.exists():
                backup_path = file_path.with_suffix(".backup.html")
                shutil.move(file_path, backup_path)  # Bestehende Datei sichern
                print(f"📂 Bestehende Datei gesichert: {backup_path}")

            fig.write_html(file_path)
            print(f"✅ Diagramm gespeichert: {file_path}")

    # Speicherpfade
    cohort_retention_path = BASE_DIR / "cohort_retention.html"
    retention_trend_path = BASE_DIR / "retention_trend.html"
    cohort_revenue_path = BASE_DIR / "cohort_revenue.html"

    # Speichern der Diagramme mit Backup
    save_chart(fig1, cohort_retention_path)
    save_chart(fig2, retention_trend_path)
    save_chart(fig3, cohort_revenue_path)

    return {
        "Kohorten-Retention": str(cohort_retention_path),
        "Retention-Rate Trends": str(retention_trend_path),
        "Kohorten-Umsatzentwicklung": str(cohort_revenue_path),
    }

print("✅ Kohortenanalyse bereit zur Nutzung in der Anwendung.")
