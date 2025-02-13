# Standard Libaries
import pandas as pd
import plotly.express as px
import shutil  # Für Sicherungskopien

from pathlib import Path

# Speicherpfad für Analyse-Ergebnisse
BASE_DIR = Path("/Users/marcus/Documents/GitHub/Abschlussprojekt/main_project/PyQt6/analysis/analysis_results")
BASE_DIR.mkdir(parents=True, exist_ok=True)  # Verzeichnis automatisch erstellen

def generate_neukunden_analysis(df):
    """Führt die Neukundenanalyse mit den übergebenen Daten durch."""
    
    if df is None or df.empty:
        print("⚠️ Keine gültigen Daten für die Neukundenanalyse vorhanden!")
        return {}

    df["Date"] = pd.to_datetime(df["Date"])
    df["Year-Month"] = df["Date"].dt.to_period("M").astype(str)  

    # Neukunden identifizieren
    first_purchase = df.groupby("Customer ID")["Date"].min().reset_index()
    first_purchase.columns = ["Customer ID", "First Purchase Date"]

    df = df.merge(first_purchase, on="Customer ID", how="left")
    df["Customer Type"] = df.apply(lambda x: "Neukunde" if x["First Purchase Date"] == x["Date"] else "Bestandskunde", axis=1)

    # Wachstum der Neukunden über Zeit
    neukunden_trends = df[df["Customer Type"] == "Neukunde"].groupby("Year-Month")["Customer ID"].nunique().reset_index()

    fig1 = px.line(
        neukunden_trends, x="Year-Month", y="Customer ID",
        title="Neukundenwachstum über Zeit",
        markers=True, line_shape="spline"
    )
    fig1.update_layout(template="plotly_dark")

    # Neukundenverteilung nach Akquisitionskanälen
    fig2 = None
    if "Purchase Channel" in df.columns:
        channel_counts = df[df["Customer Type"] == "Neukunde"].groupby("Purchase Channel")["Customer ID"].count().reset_index()
        channel_counts.columns = ["Purchase Channel", "Customer Count"]
        fig2 = px.pie(
            channel_counts, names="Purchase Channel", values="Customer Count",
            title="Neukunden nach Vertriebskanal", hole=0.4,
            color_discrete_sequence=px.colors.sequential.Teal
        )
        fig2.update_layout(template="plotly_dark")

    # Erstkaufwert & Umsatzanalyse der Neukunden
    neukunden_revenue = df[df["Customer Type"] == "Neukunde"].groupby("Year-Month")["Revenue"].sum().reset_index()

    fig3 = px.bar(
        neukunden_revenue, x="Year-Month", y="Revenue",
        title="Gesamtumsatz der Neukunden über Zeit",
        color="Revenue", color_continuous_scale="Blues"
    )
    fig3.update_layout(template="plotly_dark")

    # Branchenverteilung der Neukunden
    fig4 = None
    if "Industry" in df.columns:
        industry_counts = df[df["Customer Type"] == "Neukunde"].groupby("Industry")["Customer ID"].count().reset_index()
        industry_counts.columns = ["Industry", "Customer Count"]
        fig4 = px.treemap(
            industry_counts, path=["Industry"], values="Customer Count",
            title="Neukunden nach Branche", color="Customer Count",
            color_continuous_scale="Viridis"
        )
        fig4.update_layout(template="plotly_dark")

    # **📊 Länderbasierte Verteilung der Neukunden**
    fig5 = None
    if "Country" in df.columns:
        country_counts = df[df["Customer Type"] == "Neukunde"].groupby("Country")["Customer ID"].count().reset_index()
        country_counts.columns = ["Country", "Customer Count"]
        fig5 = px.choropleth(
            country_counts, locations="Country", locationmode="country names",
            color="Customer Count", hover_name="Country",
            color_continuous_scale="Plasma", title="Neukundenverteilung nach Ländern"
        )
        fig5.update_layout(template="plotly_dark")

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
    neukunden_trend_path = BASE_DIR / "neukunden_trend.html"
    neukunden_channels_path = BASE_DIR / "neukunden_channels.html"
    neukunden_revenue_path = BASE_DIR / "neukunden_revenue.html"
    neukunden_industry_path = BASE_DIR / "neukunden_industry.html"
    neukunden_country_path = BASE_DIR / "neukunden_country.html"

    # **📌 Speichern der Diagramme mit Backup-Funktion**
    save_chart(fig1, neukunden_trend_path)
    save_chart(fig2, neukunden_channels_path) if fig2 else None
    save_chart(fig3, neukunden_revenue_path)
    save_chart(fig4, neukunden_industry_path) if fig4 else None
    save_chart(fig5, neukunden_country_path) if fig5 else None

    return {
        "Neukundenwachstum": str(neukunden_trend_path),
        "Neukunden nach Vertriebskanal": str(neukunden_channels_path) if fig2 else None,
        "Neukundenumsatz": str(neukunden_revenue_path),
        "Branchenverteilung der Neukunden": str(neukunden_industry_path) if fig4 else None,
        "Neukunden nach Ländern": str(neukunden_country_path) if fig5 else None,
    }

print("✅ Neukundenanalyse bereit zur Nutzung in der Anwendung.")
