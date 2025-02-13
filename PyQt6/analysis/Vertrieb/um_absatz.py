# Standard Libaries
import pandas as pd
import plotly.express as px
import shutil  # Für Sicherungskopien

from pathlib import Path

# Speicherpfad für Analyse-Ergebnisse
BASE_DIR = Path("/Users/marcus/Documents/GitHub/Abschlussprojekt/main_project/PyQt6/analysis/analysis_results")
BASE_DIR.mkdir(parents=True, exist_ok=True)  # Verzeichnis automatisch erstellen

def generate_umsatz_absatz_analysis(df):
    """Führt die Umsatz- & Absatzanalyse mit den übergebenen Daten durch."""
    
    if df is None or df.empty:
        print("⚠️ Keine gültigen Daten für die Umsatz- & Absatzanalyse vorhanden!")
        return {}

    df["Date"] = pd.to_datetime(df["Date"])

    # Monatliche Umsatz- und Absatzentwicklung
    df["Month"] = df["Date"].dt.to_period("M").astype(str)

    monthly_revenue = df.groupby("Month")["Revenue"].sum().reset_index()
    monthly_revenue.columns = ["Month", "Total Revenue"]

    monthly_sales = df.groupby("Month")["Transaction ID"].count().reset_index()
    monthly_sales.columns = ["Month", "Total Sales"]

    # Umsatz nach Produktkategorie, Vertriebskanal & Industrie
    fig3, fig4, fig5 = None, None, None

    if "Product" in df.columns:
        revenue_by_product = df.groupby("Product")["Revenue"].sum().reset_index()
        revenue_by_product.columns = ["Product", "Total Revenue"]

        fig3 = px.bar(
            revenue_by_product, x="Product", y="Total Revenue",
            title="🛠 Umsatz nach Produktkategorie",
            color="Total Revenue", color_continuous_scale="Viridis"
        )
        fig3.update_layout(template="plotly_dark")

    if "Purchase Channel" in df.columns:
        revenue_by_channel = df.groupby("Purchase Channel")["Revenue"].sum().reset_index()
        revenue_by_channel.columns = ["Purchase Channel", "Total Revenue"]

        fig4 = px.bar(
            revenue_by_channel, x="Purchase Channel", y="Total Revenue",
            title="🛒 Umsatz nach Vertriebskanal",
            color="Total Revenue", color_continuous_scale="Blues"
        )
        fig4.update_layout(template="plotly_dark")

    if "Industry" in df.columns:
        revenue_by_industry = df.groupby("Industry")["Revenue"].sum().reset_index()
        revenue_by_industry.columns = ["Industry", "Total Revenue"]

        fig5 = px.bar(
            revenue_by_industry, x="Industry", y="Total Revenue",
            title="🏢 Umsatz nach Branche",
            color="Total Revenue", color_continuous_scale="Magma"
        )
        fig5.update_layout(template="plotly_dark")

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
    monthly_revenue_path = BASE_DIR / "monthly_revenue.html"
    monthly_sales_path = BASE_DIR / "monthly_sales.html"
    revenue_by_product_path = BASE_DIR / "revenue_by_product.html"
    revenue_by_channel_path = BASE_DIR / "revenue_by_channel.html"
    revenue_by_industry_path = BASE_DIR / "revenue_by_industry.html"

    # Speichern der Diagramme mit Backup
    fig1 = px.line(
        monthly_revenue, x="Month", y="Total Revenue",
        title="📈 Monatliche Umsatzentwicklung",
        markers=True, line_shape="spline", color_discrete_sequence=["#FF5733"]
    )
    fig1.update_layout(template="plotly_dark")

    fig2 = px.line(
        monthly_sales, x="Month", y="Total Sales",
        title="📦 Monatliche Absatzentwicklung",
        markers=True, line_shape="spline", color_discrete_sequence=["#2E86C1"]
    )
    fig2.update_layout(template="plotly_dark")

    save_chart(fig1, monthly_revenue_path)
    save_chart(fig2, monthly_sales_path)
    save_chart(fig3, revenue_by_product_path) if fig3 else None
    save_chart(fig4, revenue_by_channel_path) if fig4 else None
    save_chart(fig5, revenue_by_industry_path) if fig5 else None

    return {
        "Monatliche Umsatzentwicklung": str(monthly_revenue_path),
        "Monatliche Absatzentwicklung": str(monthly_sales_path),
        "Umsatz nach Produktkategorie": str(revenue_by_product_path) if fig3 else None,
        "Umsatz nach Vertriebskanal": str(revenue_by_channel_path) if fig4 else None,
        "Umsatz nach Branche": str(revenue_by_industry_path) if fig5 else None,
    }

print("✅ Umsatz- & Absatzanalyse bereit zur Nutzung in der Anwendung.")
