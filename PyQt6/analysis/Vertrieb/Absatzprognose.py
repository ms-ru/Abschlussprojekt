
import pandas as pd
import plotly.graph_objects as go
import shutil  # Für Sicherungskopien
from statsmodels.tsa.holtwinters import ExponentialSmoothing

from pathlib import Path

# Speicherpfad für Analyse-Ergebnisse
BASE_DIR = Path("/Users/marcus/Documents/GitHub/Abschlussprojekt/main_project/PyQt6/analysis/analysis_results")
BASE_DIR.mkdir(parents=True, exist_ok=True)  # Verzeichnis automatisch erstellen

def generate_absatzprognose(df):
    """Führt die Absatzprognose mit den übergebenen Daten durch."""
    
    if df is None or df.empty:
        print("⚠️ Keine gültigen Daten für die Absatzprognose vorhanden!")
        return {}

    df["Date"] = pd.to_datetime(df["Date"])

    # Monatliche Verkaufszahlen aggregieren
    df["Month"] = df["Date"].dt.to_period("M").astype(str)
    monthly_sales = df.groupby("Month")["Transaction ID"].count().reset_index()
    monthly_sales["Month"] = pd.to_datetime(monthly_sales["Month"])
    monthly_sales.columns = ["Month", "Total Sales"]

    # Holt-Winters Exponential Smoothing Modell anwenden
    try:
        model = ExponentialSmoothing(
            monthly_sales["Total Sales"], seasonal="add", seasonal_periods=12, trend="add"
        )
        fit = model.fit()
    except Exception as e:
        print(f"⚠️ Fehler beim Erstellen des Prognosemodells: {e}")
        return {}

    # Absatzprognose für die nächsten 12 Monate
    forecast_periods = 12
    future_months = pd.date_range(start=monthly_sales["Month"].max(), periods=forecast_periods+1, freq="M")[1:]
    forecast_values = fit.forecast(forecast_periods)

    forecast_df = pd.DataFrame({"Month": future_months, "Forecasted Sales": forecast_values})

    # Sicherstellen, dass der Speicherordner existiert & Backups erstellen
    forecast_file = BASE_DIR / "forecast_sales.html"

    def save_chart(fig, file_path):
        if fig:
            if file_path.exists():
                backup_path = file_path.with_suffix(".backup.html")
                shutil.move(file_path, backup_path)  # Bestehende Datei sichern
                print(f"📂 Bestehende Datei gesichert: {backup_path}")

            fig.write_html(file_path)
            print(f"✅ Diagramm gespeichert: {file_path}")

    # Visualisierung: Absatzentwicklung mit Prognose
    fig = go.Figure()

    # Historische Verkaufszahlen
    fig.add_trace(
        go.Scatter(
            x=monthly_sales["Month"], y=monthly_sales["Total Sales"],
            mode="lines+markers", name="Historische Verkaufszahlen",
            line=dict(color="blue")
        )
    )
    
    # Prognostizierte Verkaufszahlen
    fig.add_trace(
        go.Scatter(
            x=forecast_df["Month"], y=forecast_df["Forecasted Sales"],
            mode="lines+markers", name="Prognose",
            line=dict(color="red", dash="dash")
        )
    )

    fig.update_layout(
        title="📦 Absatzprognose für die nächsten 12 Monate",
        xaxis_title="Monat",
        yaxis_title="Verkaufszahlen",
        template="plotly_dark"
    )

    # Speichern der Diagramme mit Backup
    save_chart(fig, forecast_file)

    return {
        "Absatzprognose": str(forecast_file),
    }

print(f"✅ Absatzprognose bereit zur Nutzung in der Anwendung.")
