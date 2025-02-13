# Standard Libaries
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import shutil  # Für Sicherungskopien

from pathlib import Path

# Speicherpfad für Analyse-Ergebnisse
BASE_DIR = Path("/Users/marcus/Documents/GitHub/Abschlussprojekt/main_project/PyQt6/analysis/analysis_results")
BASE_DIR.mkdir(parents=True, exist_ok=True)  # Verzeichnis automatisch erstellen

def generate_wiederkaufsrate(df):
    """Führt die Wiederkaufsanalyse mit den übergebenen Daten durch."""
    
    if df is None or df.empty:
        print("⚠️ Keine gültigen Daten für die Wiederkaufsanalyse vorhanden!")
        return {}

    df["Date"] = pd.to_datetime(df["Date"])

    # Wiederkaufsrate pro Kunde berechnen
    repeat_customers = df.groupby("Customer ID")["Transaction ID"].count().reset_index()
    repeat_customers.columns = ["Customer ID", "Total Purchases"]
    repeat_customers["Repeat Customer"] = repeat_customers["Total Purchases"] > 1

    # Gesamt-Wiederkaufsrate berechnen
    repeat_rate = repeat_customers["Repeat Customer"].mean()

    # Wiederkaufsrate über die Zeit
    df["YearMonth"] = df["Date"].dt.to_period("M").astype(str)
    repeat_trend = df.groupby(["YearMonth", "Customer ID"])["Transaction ID"].count().reset_index()
    repeat_trend["Repeat Customer"] = repeat_trend["Transaction ID"] > 1
    repeat_rate_trend = repeat_trend.groupby("YearMonth")["Repeat Customer"].mean().reset_index()

    # Wiederkaufsrate nach Umsatzsegmenten
    if "Revenue Segment" not in df.columns:
        revenue_quantiles = df["Revenue"].quantile([0.2, 0.8])
        df["Revenue Segment"] = df["Revenue"].apply(lambda x: "High-Value" if x >= revenue_quantiles[0.8] 
                                                        else "Mid-Tier" if x >= revenue_quantiles[0.2] 
                                                        else "Low-Value")

    repeat_rate_by_segment = df.groupby("Revenue Segment")["Customer ID"].nunique().reset_index()
    repeat_rate_by_segment.columns = ["Revenue Segment", "Unique Customers"]
    repeat_rate_by_segment["Repeat Customers"] = df[df["Customer ID"].isin(repeat_customers[repeat_customers["Repeat Customer"]]["Customer ID"])] \
                                                 .groupby("Revenue Segment")["Customer ID"].nunique().values
    repeat_rate_by_segment["Repeat Rate"] = repeat_rate_by_segment["Repeat Customers"] / repeat_rate_by_segment["Unique Customers"]

    # Sicherstellen, dass der Speicherordner existiert & Backups erstellen
    def save_chart(fig, file_path):
        if fig:
            if file_path.exists():
                backup_path = file_path.with_suffix(".backup.html")
                shutil.move(file_path, backup_path)  # Bestehende Datei sichern
                print(f"📂 Bestehende Datei gesichert: {backup_path}")

            fig.write_html(file_path)
            print(f"✅ Diagramm gespeichert: {file_path}")

    # Visualisierung: Gesamt-Wiederkaufsrate
    fig1 = go.Figure()
    fig1.add_trace(go.Indicator(
        mode="gauge+number",
        value=repeat_rate * 100,
        title={"text": "🔄 Gesamt-Wiederkaufsrate"},
        gauge={"axis": {"range": [0, 100]}, "bar": {"color": "blue"}}
    ))
    fig1.update_layout(template="plotly_dark")

    # Wiederkaufsrate-Trend über die Zeit
    fig2 = px.line(
        repeat_rate_trend, x="YearMonth", y="Repeat Customer",
        title="📊 Wiederkaufsrate über die Zeit",
        labels={"Repeat Customer": "Wiederkaufsrate"},
        markers=True
    )
    fig2.update_layout(template="plotly_dark")

    # Wiederkaufsrate nach Umsatzsegmenten
    fig3 = px.bar(
        repeat_rate_by_segment, x="Revenue Segment", y="Repeat Rate",
        title="💰 Wiederkaufsrate nach Umsatzsegmenten",
        color="Repeat Rate", color_continuous_scale="Magma"
    )
    fig3.update_layout(template="plotly_dark")

    # Speicherpfade
    overall_repeat_rate_path = BASE_DIR / "overall_repeat_rate.html"
    repeat_rate_trend_path = BASE_DIR / "repeat_rate_trend.html"
    repeat_rate_by_segment_path = BASE_DIR / "repeat_rate_by_segment.html"

    # Speichern der Diagramme mit Backup
    save_chart(fig1, overall_repeat_rate_path)
    save_chart(fig2, repeat_rate_trend_path)
    save_chart(fig3, repeat_rate_by_segment_path)

    return {
        "Gesamt-Wiederkaufsrate": str(overall_repeat_rate_path),
        "Wiederkaufsrate über die Zeit": str(repeat_rate_trend_path),
        "Wiederkaufsrate nach Umsatzsegmenten": str(repeat_rate_by_segment_path),
    }

print("✅ Wiederkaufsanalyse bereit zur Nutzung in der Anwendung.")
