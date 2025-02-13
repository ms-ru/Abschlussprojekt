# Standard Libaries
import pandas as pd
import plotly.graph_objects as go
import shutil  # Für Sicherungskopien

from statsmodels.tsa.holtwinters import ExponentialSmoothing
from pathlib import Path

# Speicherpfad für Analyse-Ergebnisse
BASE_DIR = Path("/Users/marcus/Documents/GitHub/Abschlussprojekt/main_project/PyQt6/analysis/analysis_results")
BASE_DIR.mkdir(parents=True, exist_ok=True)  # Verzeichnis automatisch erstellen

def generate_umsatzprognose(df):
    """Führt die Umsatzprognose mit den übergebenen Daten durch."""
    
    if df is None or df.empty:
        print("⚠️ Keine gültigen Daten für die Umsatzprognose vorhanden!")
        return {}

    df["Date"] = pd.to_datetime(df["Date"])

    # Monatliche Umsatzaggregation
    df["Month"] = df["Date"].dt.to_period("M").astype(str)
    monthly_revenue = df.groupby("Month")["Revenue"].sum().reset_index()
    monthly_revenue["Month"] = pd.to_datetime(monthly_revenue["Month"])

    # Holt-Winters Exponential Smoothing Modell anwenden
    try:
        model = ExponentialSmoothing(
            monthly_revenue["Revenue"], seasonal="add", seasonal_periods=12, trend="add"
        )
        fit = model.fit()
    except Exception as e:
        print(f"⚠️ Fehler beim Erstellen des Prognosemodells: {e}")
        return {}

    # Umsatzprognose für die nächsten 12 Monate
    forecast_periods = 12
    future_months = pd.date_range(start=monthly_revenue["Month"].max(), periods=forecast_periods+1, freq="M")[1:]
    forecast_values = fit.forecast(forecast_periods)

    forecast_df = pd.DataFrame({"Month": future_months, "Forecasted Revenue": forecast_values})

    # Sicherstellen, dass der Speicherordner existiert & Backups erstellen
    forecast_revenue_path = BASE_DIR / "forecast_revenue.html"

    def save_chart(fig, file_path):
        if fig:
            if file_path.exists():
                backup_path = file_path.with_suffix(".backup.html")
                shutil.move(file_path, backup_path)  # Bestehende Datei sichern
                print(f"📂 Bestehende Datei gesichert: {backup_path}")

            fig.write_html(file_path)
            print(f"✅ Diagramm gespeichert: {file_path}")

    # Visualisierung: Umsatzentwicklung mit Prognose
    fig = go.Figure()

    # Historische Umsatzdaten
    fig.add_trace(
        go.Scatter(
            x=monthly_revenue["Month"], y=monthly_revenue["Revenue"],
            mode="lines+markers", name="Historische Umsätze",
            line=dict(color="blue")
        )
    )

    # Prognostizierte Umsätze
    fig.add_trace(
        go.Scatter(
            x=forecast_df["Month"], y=forecast_df["Forecasted Revenue"],
            mode="lines+markers", name="Prognose",
            line=dict(color="red", dash="dash")
        )
    )

    fig.update_layout(
        title="📈 Umsatzprognose für die nächsten 12 Monate",
        xaxis_title="Monat",
        yaxis_title="Umsatz",
        template="plotly_dark"
    )

    # Speichern des Diagramms mit Backup
    save_chart(fig, forecast_revenue_path)

    return {
        "Umsatzprognose": str(forecast_revenue_path),
    }

print("✅ Umsatzprognose bereit zur Nutzung in der Anwendung.")
