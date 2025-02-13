# Standard Libaries
import pandas as pd
import plotly.express as px
import shutil  # Für Sicherungskopien

from pathlib import Path

# Speicherpfad für Analyse-Ergebnisse
BASE_DIR = Path("/Users/marcus/Documents/GitHub/Abschlussprojekt/main_project/PyQt6/analysis/analysis_results")
BASE_DIR.mkdir(parents=True, exist_ok=True)  # Verzeichnis automatisch erstellen

def generate_rfm_analysis(df):
    """Führt die RFM-Analyse mit den übergebenen Daten durch."""
    
    if df is None or df.empty:
        print("⚠️ Keine gültigen Daten für die RFM-Analyse vorhanden!")
        return {}

    df["Date"] = pd.to_datetime(df["Date"])
    latest_date = df["Date"].max()  # Stichtag für die RFM-Berechnung

    # RFM-Werte berechnen
    rfm = df.groupby("Customer ID").agg(
        Recency=("Date", lambda x: (latest_date - x.max()).days),
        Frequency=("Transaction ID", "count"),
        Monetary=("Revenue", "sum")
    ).reset_index()

    # Labels-Anzahl setzen 
    try:
        rfm["R_Score"] = pd.qcut(rfm["Recency"], q=5, labels=[5, 4, 3, 2, 1], duplicates="drop")
        rfm["F_Score"] = pd.qcut(rfm["Frequency"], q=5, labels=[1, 2, 3, 4, 5], duplicates="drop")
        rfm["M_Score"] = pd.qcut(rfm["Monetary"], q=5, labels=[1, 2, 3, 4, 5], duplicates="drop")
    except ValueError:
        print("⚠️ `qcut()` schlägt fehl – Nutze `cut()` als Alternative.")
        rfm["R_Score"] = pd.cut(rfm["Recency"], bins=5, labels=[5, 4, 3, 2, 1])
        rfm["F_Score"] = pd.cut(rfm["Frequency"], bins=5, labels=[1, 2, 3, 4, 5])
        rfm["M_Score"] = pd.cut(rfm["Monetary"], bins=5, labels=[1, 2, 3, 4, 5])

    rfm["RFM_Score"] = rfm["R_Score"].astype(str) + rfm["F_Score"].astype(str) + rfm["M_Score"].astype(str)

    # Cluster-Bildung auf Basis von RFM-Scores
    segment_map = {
        "555": "VIP-Kunden",
        "511": "Neukunden",
        "111": "Abwanderungsrisiko",
        "155": "Wenig aktive Top-Kunden",
        "551": "Regelmäßige Käufer",
    }

    rfm["Segment"] = rfm["RFM_Score"].map(segment_map).fillna("Andere")

    # Sicherstellen, dass der Speicherordner existiert & Backups erstellen
    def save_chart(fig, file_path):
        if fig:
            if file_path.exists():
                backup_path = file_path.with_suffix(".backup.html")
                shutil.move(file_path, backup_path)  # Bestehende Datei sichern
                print(f"📂 Bestehende Datei gesichert: {backup_path}")

            fig.write_html(file_path)
            print(f"✅ Diagramm gespeichert: {file_path}")

    # RFM-Heatmap für Kundensegmente
    fig1 = px.scatter_3d(
        rfm, x="Recency", y="Frequency", z="Monetary",
        color="Segment", title="📊 RFM-Analyse der Kunden",
        color_discrete_sequence=px.colors.qualitative.Plotly
    )
    fig1.update_layout(template="plotly_dark")

    # RFM-Segmentverteilung
    segment_counts = rfm["Segment"].value_counts().reset_index()
    segment_counts.columns = ["Segment", "Customer Count"]

    fig2 = px.pie(
        segment_counts, names="Segment", values="Customer Count",
        title="🧑‍💼 Verteilung der RFM-Segmente",
        hole=0.4, color_discrete_sequence=px.colors.sequential.Teal
    )
    fig2.update_layout(template="plotly_dark")

    # Umsatzverteilung nach RFM-Segmenten
    rfm_revenue = rfm.groupby("Segment")["Monetary"].sum().reset_index()

    fig3 = px.bar(
        rfm_revenue, x="Segment", y="Monetary",
        title="💰 Umsatz pro RFM-Segment",
        color="Monetary", color_continuous_scale="Viridis"
    )
    fig3.update_layout(template="plotly_dark")

    # Speicherpfade
    rfm_3d_path = BASE_DIR / "rfm_3d.html"
    rfm_pie_path = BASE_DIR / "rfm_pie.html"
    rfm_revenue_path = BASE_DIR / "rfm_revenue.html"

    # Speichern der Diagramme mit Backup
    save_chart(fig1, rfm_3d_path)
    save_chart(fig2, rfm_pie_path)
    save_chart(fig3, rfm_revenue_path)

    return {
        "RFM-3D-Visualisierung": str(rfm_3d_path),
        "RFM-Segmentverteilung": str(rfm_pie_path),
        "Umsatz nach RFM-Segment": str(rfm_revenue_path),
    }

print("✅ RFM-Analyse bereit zur Nutzung in der Anwendung.")
