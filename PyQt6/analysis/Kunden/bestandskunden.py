#
import pandas as pd
import plotly.express as px
import shutil  # Für Sicherungskopien

from pathlib import Path

# Speicherpfad für Analyse-Ergebnisse
BASE_DIR = Path("/Users/marcus/Documents/GitHub/Abschlussprojekt/main_project/PyQt6/analysis/analysis_results")
BASE_DIR.mkdir(parents=True, exist_ok=True)  # Verzeichnis automatisch erstellen

def generate_bestandskunden_analysis(df):
    """Führt die Bestandskundenanalyse mit den übergebenen Daten durch."""
    
    if df is None or df.empty:
        print("⚠️ Keine gültigen Daten für die Bestandskundenanalyse vorhanden!")
        return {}

    df["Date"] = pd.to_datetime(df["Date"])
    df["Year"] = df["Date"].dt.year  
    df["Year-Month"] = df["Date"].dt.to_period("M").astype(str)  

    # Bestandskunden definieren
    first_purchase = df.groupby("Customer ID")["Date"].min().reset_index()
    first_purchase.columns = ["Customer ID", "First Purchase Date"]

    df = df.merge(first_purchase, on="Customer ID", how="left")
    df["Customer Type"] = df.apply(lambda x: "Neukunde" if x["First Purchase Date"] == x["Date"] else "Bestandskunde", axis=1)

    # Bestandskundenentwicklung & Abwanderung
    bestandskunden_trends = df[df["Customer Type"] == "Bestandskunde"].groupby("Year")["Customer ID"].nunique().reset_index()
    bestandskunden_trends["Churn"] = bestandskunden_trends["Customer ID"].diff().fillna(0)  

    fig0 = px.line(
        bestandskunden_trends, x="Year", y=["Customer ID", "Churn"],
        title="Bestandskundenentwicklung & Abwanderung",
        markers=True, line_shape="spline"
    )
    fig0.update_layout(template="plotly_dark")

    # Bestandskunden vs. Neukunden Anteil
    customer_type_counts = df["Customer Type"].value_counts().reset_index()
    customer_type_counts.columns = ["Customer Type", "Count"]

    fig1 = px.pie(
        customer_type_counts, names="Customer Type", values="Count",
        title="Anteil Bestandskunden vs. Neukunden",
        color_discrete_sequence=px.colors.sequential.Teal
    )
    fig1.update_layout(template="plotly_dark")

    # Entwicklung von Bestandskunden über Zeit
    customer_trends = df.groupby(["Year-Month", "Customer Type"])["Customer ID"].nunique().reset_index()

    fig2 = px.line(
        customer_trends, x="Year-Month", y="Customer ID", color="Customer Type",
        title="Entwicklung Bestandskunden vs. Neukunden",
        markers=True, line_shape="spline"
    )
    fig2.update_layout(template="plotly_dark")

    # Churn-Rate Analyse
    churn_rate = df.groupby(["Year-Month", "Customer Type"])["Customer ID"].nunique().unstack().fillna(0)
    churn_rate["Churn Rate"] = churn_rate["Bestandskunde"].pct_change().fillna(0) * -1

    fig3 = px.line(
        churn_rate.reset_index(), x="Year-Month", y="Churn Rate",
        title="Churn-Rate Entwicklung (Bestandskunden, die abgesprungen sind)",
        markers=True, line_shape="spline"
    )
    fig3.update_layout(template="plotly_dark")

    # Kaufverhalten von Bestandskunden analysieren
    purchase_behavior = df[df["Customer Type"] == "Bestandskunde"].groupby(["Year-Month"])["Revenue"].sum().reset_index()

    fig4 = px.bar(
        purchase_behavior, x="Year-Month", y="Revenue",
        title="Gesamtausgaben der Bestandskunden über Zeit",
        color="Revenue", color_continuous_scale="Blues"
    )
    fig4.update_layout(template="plotly_dark")

    # Durchschnittliche Kaufanzahl von Bestandskunden
    purchase_count = df[df["Customer Type"] == "Bestandskunde"].groupby(["Year-Month"])["Customer ID"].count().reset_index()

    fig5 = px.bar(
        purchase_count, x="Year-Month", y="Customer ID",
        title="Durchschnittliche Kaufanzahl pro Bestandskunde",
        color="Customer ID", color_continuous_scale="Magma"
    )
    fig5.update_layout(template="plotly_dark")

    # Sicherstellen, dass der Speicherordner existiert & Backups erstellen**
    def save_chart(fig, file_path):
        if fig:
            if file_path.exists():
                backup_path = file_path.with_suffix(".backup.html")
                shutil.move(file_path, backup_path)  # Bestehende Datei sichern
                print(f"📂 Bestehende Datei gesichert: {backup_path}")

            fig.write_html(file_path)
            print(f"✅ Diagramm gespeichert: {file_path}")

    # Speicherpfade
    customer_growth_path = BASE_DIR / "customer_growth.html"
    customer_type_pie_path = BASE_DIR / "customer_type_pie.html"
    customer_trend_path = BASE_DIR / "customer_trend.html"
    churn_rate_path = BASE_DIR / "churn_rate.html"
    revenue_bestandskunden_path = BASE_DIR / "revenue_bestandskunden.html"
    purchase_count_path = BASE_DIR / "purchase_count.html"

    # Speichern der Diagramme mit Backup
    save_chart(fig0, customer_growth_path)
    save_chart(fig1, customer_type_pie_path)
    save_chart(fig2, customer_trend_path)
    save_chart(fig3, churn_rate_path)
    save_chart(fig4, revenue_bestandskunden_path)
    save_chart(fig5, purchase_count_path)

    return {
        "Bestandskunden-Wachstum & Abwanderung": str(customer_growth_path),
        "Bestandskunden vs. Neukunden": str(customer_type_pie_path),
        "Kundenentwicklung": str(customer_trend_path),
        "Churn-Rate": str(churn_rate_path),
        "Umsatz Bestandskunden": str(revenue_bestandskunden_path),
        "Kaufanzahl Bestandskunden": str(purchase_count_path),
    }

print("✅ Bestandskundenanalyse bereit zur Nutzung in der Anwendung.")
