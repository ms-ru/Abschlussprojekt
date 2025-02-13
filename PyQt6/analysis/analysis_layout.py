# Standardbibliotheken
from pathlib import Path

# PyQt6 imports
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QDateEdit,
    QGridLayout,
    QTableWidget,
    QTableWidgetItem
)

from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import Qt, QDate


class AnalysisLayout(QWidget):
    def __init__(self, parent=None, analysis_category=""):
        super().__init__(parent)
        self.analysis_category = analysis_category  # Speichert die aktuelle Analyse-Unterseite
        self.init_ui()

        # Theme der Hauptanwendung übernehmen
        if parent:
            self.setStyleSheet(parent.styleSheet())

    def init_ui(self):
        self.setLayout(self.create_analysis_layout())

    def create_analysis_layout(self):
        layout = QVBoxLayout()

        # Header mit Titel, Datum & Steuerung
        layout.addLayout(self.create_header())

        # Dropdown zur Auswahl der Diagramm-Anzahl (Max. 3 Diagramme)
        self.num_charts_selector = QComboBox()
        self.num_charts_selector.addItems(["1 Diagramm", "2 Diagramme", "3 Diagramme"])
        self.num_charts_selector.currentIndexChanged.connect(self.update_analysis)
        layout.addWidget(self.num_charts_selector)

        # Hauptbereich mit Diagrammen & Key Metrics
        self.chart_grid = QGridLayout()
        self.chart_views = []  # Speichert mehrere Diagramm-Widgets
        for _ in range(3):  # Standard: 3 Diagrammplätze
            chart_view = QWebEngineView()
            chart_view.setMinimumHeight(500)
            self.chart_views.append(chart_view)

        # Positionierung der Diagramme im Raster (dynamisch)
        self.chart_grid.addWidget(self.chart_views[0], 0, 0, 1, 2)  # Erstes Diagramm groß
        self.chart_grid.addWidget(self.chart_views[1], 1, 0)  # Zweites Diagramm (links)
        self.chart_grid.addWidget(self.chart_views[2], 1, 1)  # Drittes Diagramm (rechts)

        layout.addLayout(self.chart_grid)

        # Tabelle für Metriken
        self.metrics_table = QTableWidget(3, 2)
        self.metrics_table.setHorizontalHeaderLabels(["Kennzahl", "Wert"])
        layout.addWidget(self.metrics_table)

        return layout

    def create_header(self):
        header_layout = QHBoxLayout()
        title_label = QLabel(f"📊 {self.analysis_category} Analyse")
        title_label.setObjectName("analysisTitle")  # Stylesheet für Titel anwenden
        header_layout.addWidget(title_label)

        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate().addMonths(-6))
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())

        header_layout.addWidget(QLabel("📅 Von:"))
        header_layout.addWidget(self.date_from)
        header_layout.addWidget(QLabel("📅 Bis:"))
        header_layout.addWidget(self.date_to)

        # Dropdown für Diagramme 
        self.chart_selector = QComboBox()
        self.chart_selector.addItems(self.get_analysis_options())
        header_layout.addWidget(self.chart_selector)

        # Aktualisieren-Button
        self.update_button = QPushButton("🔄 Aktualisieren")
        self.update_button.setStyleSheet("background-color: #673AB7; color: white; font-weight: bold;")
        self.update_button.clicked.connect(self.update_analysis)
        header_layout.addWidget(self.update_button)

        return header_layout

    def get_analysis_options(self):
        """Filtert die Analysen basierend auf der aktuellen Unterseite."""
        analysis_mapping = {
            "Segmentanalyse": ["Segmentanalyse"],
            "Bestandskundenanalyse": ["Bestandskundenanalyse"],
            "Neukundenanalyse": ["Neukundenanalyse"],
            "Kohortenanalyse": ["Kohortenanalyse"],
            "RFM-Analyse": ["RFM-Analyse"],
            "Kaufzyklusanalyse": ["Kaufzyklusanalyse"],
            "AOV-Analyse": ["AOV-Analyse"],
            "Churn-Analyse": ["Churn-Analyse"],
            "Survival-Analyse": ["Survival-Analyse"],
            "Inaktivitätsanalyse": ["Inaktivitätsanalyse"],
            "Umsatz- & Absatzanalyse": ["Umsatz- & Absatzanalyse"],
            "Umsatzprognose": ["Umsatzprognose"],
            "Absatzprognose": ["Absatzprognose"],
            "Benchmark-Analyse": ["Benchmark-Analyse"],
            "CLV-Analyse": ["CLV-Analyse"],
            "Wiederkaufsanalyse": ["Wiederkaufsanalyse"]
        }
        return analysis_mapping.get(self.analysis_category, [])

    def update_analysis(self):
        """Lädt Diagramme & aktualisiert die Metriken."""
        num_charts = self.num_charts_selector.currentIndex() + 1
        selected_analysis = self.chart_selector.currentText()
        print(f"📊 Lade {num_charts} Diagramm(e) für {selected_analysis}")

        # Diagramme laden
        for i, chart_view in enumerate(self.chart_views):
            if i < num_charts:
                chart_view.setVisible(True)
                self.load_chart(selected_analysis, chart_view)
            else:
                chart_view.setVisible(False)

        # Dummy-Werte für Key Metrics setzen
        self.metrics_table.setItem(0, 0, QTableWidgetItem("Metrik 1"))
        self.metrics_table.setItem(0, 1, QTableWidgetItem("120"))
        self.metrics_table.setItem(1, 0, QTableWidgetItem("Metrik 2"))
        self.metrics_table.setItem(1, 1, QTableWidgetItem("340"))
        self.metrics_table.setItem(2, 0, QTableWidgetItem("Metrik 3"))
        self.metrics_table.setItem(2, 1, QTableWidgetItem("89"))

    def load_chart(self, analysis_name, chart_view):
        """Lädt das HTML-Diagramm für die gewählte Analyse."""
        base_dir = Path("/Users/marcus/Documents/GitHub/Abschlussprojekt/main_project/PyQt6/analysis/analysis_results")
        
        analysis_files = {
            
            # Kundenstamm & Segmente (Kunden)
            
            #Bestandskunden-Analyse
            "Bestandskunden-Wachstum & Abwanderung": "customer_growth.html",
            "Bestandskunden vs. Neukunden": "customer_type_pie.html",
            "Kundenentwicklung": "customer_trend.html",
            "Churn-Rate": "churn_rate.html",
            "Umsatz Bestandskunden": "revenue_bestandskunden.html",
            "Kaufanzahl Bestandskunden": "purchase_count.html",
            
            # Kohorten-Analyse
            "Kohorten-Retention": "cohort_retention.html",
            "Retention-Rate Trends": "retention_trend.html",
            "Kohorten-Umsatzentwicklung": "cohort_revenue.html",
            
            # Neukunden-Analyse
            "Neukundenwachstum": "neukunden_trend.html",
            "Neukunden nach Vertriebskanal": "neukunden_channels.html",
            "Neukundenumsatz": "neukunden_revenue.html",
            "Branchenverteilung der Neukunden": "neukunden_industry.html",
            "Neukunden nach Ländern": "neukunden_country.html",
            
            #Segment-Analyse
            "Segment Sunburst": "segment_sunburst.html",
            "Branchen-Treemap": "industry_treemap.html",
            "Länderkarte": "country_map.html",
            "Vertriebskanäle": "purchase_channel.html",
            "Segment-Trends": "segment_trends.html",
            "Industrie-Trends": "industry_trends.html",
            
            # Kaufverhalten & Verkaufsdynamik (Kaufverhalten)
            
            # AOV-Analyse
            "AOV-Entwicklung über Zeit": "aov_trend.html",
            "Verteilung des AOV": "aov_distribution.html",
            "AOV nach Industrie": "aov_industry.html",
            "AOV nach Vertriebskanal": "aov_channel.html",
            
            # kaufzyklusnalyse
            "Kaufaktivität pro Monat": "kaufzyklus_trend.html",
            "Verteilung der Kaufzyklen": "kaufzyklus_distribution.html",
            "Kaufzyklen nach Segmenten": "kaufzyklus_segments.html",
            
            # RFM-Analyse
            "RFM-3D-Visualisierung": "rfm_3d.html",
            "RFM-Segmentverteilung": "rfm_pie.html",
            "Umsatz nach RFM-Segment": "rfm_revenue.html",
            
            # Kundenabwanderung & Risikoanalyse (Kundenbewegung)
            
            # Churn-Analyse
            "Gesamt-Churn-Rate": "churn_rate.html",
            "Churn-Rate nach Industrie": "churn_by_industry.html",
            "Churn-Rate nach Vertriebskanal": "churn_by_channel.html",
            
            # Inaktivitäts-Analyse
            "Gesamt-Inaktivitätsrate": "dormant_rate.html",
            "Inaktivitätsrate nach Industrie": "dormant_by_industry.html",
            "Inaktivitätsrate nach Vertriebskanal": "dormant_by_channel.html",
            
            # Survival-Analyse
            "Gesamt-Inaktivitätsrate": "survival_rate.html",
            "Inaktivitätsrate nach Industrie": "survival_by_industry.html",
            "Inaktivitätsrate nach Vertriebskanal": "survival_by_channel.html",
            
            # Umsatz- & Absatzanalyse (Vertrieb)
            
            # Absatzprognose
            "Absatzprognose": "forecast_sales.html",
            
            # Benchmark-Analyse
            "Gesamtumsatz nach Branche": "benchmark_revenue.html",
            "Durchschnittlicher Umsatz pro Kunde": "benchmark_avg_revenue.html",
            "Gesamtverkäufe nach Branche": "benchmark_total_sales.html",
            "Umsatz nach Vertriebskanal": "benchmark_revenue_channel.html",
            
            # Um- & Absatzanalyse
            "Monatliche Umsatzentwicklung": "monthly_revenue.html",
            "Monatliche Absatzentwicklung": "monthly_sales.html",
            "Umsatz nach Produktkategorie": "revenue_by_product.html",
            "Umsatz nach Vertriebskanal": "revenue_by_channel.html",
            "Umsatz nach Branche": "revenue_by_industry.html",
            
            # Umsatzprognose
            "Umsatzprognose": "forecast_revenue.html",
            
            # Kundenwert & CLV
            
            # CLV-Analyse
            "Verteilung des Customer Lifetime Value": "clv_distribution.html",
            "CLV im Verhältnis zur Kundenlebensdauer":"clv_vs_lifetime.html",
            "CLV nach Umsatzsegmenten": "clv_by_segment.html",
            
            # Wiederkaufs-Analyse
             "Gesamt-Wiederkaufsrate": "overall_repeat_rate.html",
            "Wiederkaufsrate über die Zeit": "repeat_rate_trend.html",
            "Wiederkaufsrate nach Umsatzsegmenten": "repeat_rate_by_segment.html"
        }

        # Prüfen, ob die gewählte Analyse existiert
        if analysis_name in analysis_files:
            html_path = base_dir / analysis_files[analysis_name]

            if html_path.exists():
                print(f"✅ Lade Diagramm: {html_path}")
                chart_view.setUrl(f"file://{html_path.resolve()}")
            else:
                print(f"❌ Datei nicht gefunden: {html_path}")
                chart_view.setHtml("<html><body><h3>Fehler: Datei nicht gefunden</h3></body></html>")

                # Fehler in der "statusBar" anzeigen, falls "parent" existiert
                if self.parent():
                    self.parent().statusBar().showMessage(f"❌ Analyse nicht gefunden: {analysis_name}", 5000)
        else:
            print(f"❌ Fehler: Ungültige Analyse ausgewählt ({analysis_name})")
            chart_view.setHtml("<html><body><h3>Fehler: Keine gültige Analyse</h3></body></html>")

            if self.parent():
                self.parent().statusBar().showMessage(f"❌ Fehler: '{analysis_name}' nicht verfügbar!", 5000)
