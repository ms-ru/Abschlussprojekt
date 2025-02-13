# Standardbibliotheken
import sys
import os
import json
import pickle
import pandas as pd

from pathlib import Path

# Basisverzeichnis setzen
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = "saved_data.pkl"  # Datei zur Speicherung von Daten

# Prüfen, dass alle Modulpfade gefunden werden
MODULE_DIRS = ["gui", "data_import", "analysis", "export", "users"]
for directory in MODULE_DIRS:
    sys.path.append(os.path.join(BASE_DIR, directory))

# PyQt6 imports
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QMenuBar, QLineEdit, QWidgetAction,
    QCompleter, QMessageBox, QPushButton, QFileDialog, QTableWidget,
    QTableWidgetItem, QVBoxLayout
)
from PyQt6.QtGui import QAction, QKeySequence, QFont
from PyQt6.QtCore import Qt, QUrl, QPropertyAnimation, QObject
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6 import QtCore
from PyQt6 import QtWidgets

# Eigene Module 

# GUI
from gui.gui_main_window import Ui_MainWindow
from gui.gui_benutzerverwaltung import UserManagementDialog

# Datenimport
from data_import.import_csv import ImportCSV
from data_import.import_drag_and_drop import DragDropArea

# Analyse-Module 

# Kundenanalyse
from analysis.analysis_layout import AnalysisLayout
from analysis.Kunden.segment_analyse import generate_segment_analysis
from analysis.Kunden.bestandskunden import generate_bestandskunden_analysis
from analysis.Kunden.neukunden import generate_neukunden_analysis
from analysis.Kunden.Kohorten import generate_kohorten_analysis

# Kaufverhalten-Analysen
from analysis.Kaufverhalten.rfm import generate_rfm_analysis
from analysis.Kaufverhalten.kaufzyklus import generate_kaufzyklus_analysis
from analysis.Kaufverhalten.aov import generate_aov_analysis

# Kundenbewegung-Analysen
from analysis.Kundenbewegung.churn import generate_churn_analysis
from analysis.Kundenbewegung.survival import generate_survival_analysis
from analysis.Kundenbewegung.inaktivität import generate_dormant_analysis

# Vertriebsanalysen
from analysis.Vertrieb.um_absatz import generate_umsatz_absatz_analysis
from analysis.Vertrieb.Absatzprognose import generate_absatzprognose
from analysis.Vertrieb.umsatzprognose import generate_umsatzprognose
from analysis.Vertrieb.benchmark import generate_benchmark_analysis

# Kundenwert-Analysen
from analysis.Kundenwert.clv import generate_clv_analysis
from analysis.Kundenwert.wiederkaufsanalyse import generate_wiederkaufsrate


class MainApp(QMainWindow):
    
    # Globale Konstanten
    analysis_pages = [
    "Segment-Analyse", "Bestandskundenanalyse", "Neukundenanalyse", "Kohortenanalyse",
    "RFM-Analyse", "Kaufzyklusanalyse", "Durchschnittlicher Bestellwert (AOV)",
    "Churn-Analyse", "Survival-Analyse", "Inaktivitätsanalyse",
    "Um- & Ansatzanalyse","Umsatzprognose", "Absatzprognose", "Benchmark-Analyse",
    "Customer Lifetime Value (CLV)", "Wiederkaufsrate"
    ]
    
    def __init__(self):
        """ Initialisiert das Hauptfenster und alle UI-Komponenten. """
        super().__init__()
        
        # UI und Layouts laden
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)  # UI-Layout laden
        
        # Kern-Variablen
        self.tableWidget = None  # Tabelle erst später erstellen
        self.current_df = None  # Keine geladenen Daten beim Start
        self.current_page = None  # Speichert die aktuelle Seite
        
        # Benutzerverwaltung
        self.user_role = "admin"  # Standardrolle
        self.permissions = self.load_user_permissions()  # Berechtigungen laden
        
        # Analyse-Kategorien initialisieren
        self.setup_analysis_categories()
        
        # Analyse-Seiten Initialisieren
        self.analysis_pages = [analysis for sublist in self.analysen_categories.values() for analysis in sublist]
        
        # Import Initialisieren 
        self.import_csv = ImportCSV(self)
    
        # Anwendung gestalten
        self.setup_analysis_layout()
        self.load_styles()  # Stylesheets laden
        self.create_menu_bar()  # Menüleiste erstellen
        self.add_search_bar()  # Suchleiste hinzufügen
        self.add_floating_button()  # Floating-Button hinzufügen
        
        # Drag and Drop-Fläche einrichten
        self.setup_drag_drop_area()
        
        # Startseite setzen
        self.update_content("Dashboard")

        # Gespeicherte Daten laden
        self.load_previous_data()
        
        # Standard Theme
        self.change_theme("Luxuriös & Innovativ")
        
    def load_user_permissions(self):
        """Lädt die Benutzerrechte aus der JSON-Datei 'benutzerverwaltung.json'"""
        default_permissions = [
            "Dashboard", "Vergleich", "Import", "Export",
            "Einstellungen", "Themes", "Benutzerverwaltung"
        ]
        
        try:
            with open(os.path.join(BASE_DIR, "users/benutzerverwaltung.json"), "r", encoding="utf-8") as file:
                permissions = json.load(file)
                
                # Sicherstellen, dass es ein Dictionary ist
                if not isinstance(permissions, dict):
                    raise ValueError("Ungültiges JSON-Format: Erwartet ein Dictionary mit Benutzerrollen.")
                
                return permissions.get(self.user_role, default_permissions)
        
        except FileNotFoundError:
            print("⚠️  'benutzerverwaltung.json' nicht gefunden! Standardrechte werden gesetzt.")
        except json.JSONDecodeError:
            print("⚠️  Fehler beim Laden der JSON-Datei! Standardrechte werden gesetzt.")
        except ValueError as e:
            print(f"⚠️  {e} Standardrechte werden gesetzt.")
            
        return default_permissions

    def setup_analysis_layout(self):
        """Erstellt das Analyse-Layout und bindet es in das Hauptfenster ein."""
        self.analysis_layout = AnalysisLayout()
        if not self.ui.mainContentFrame.layout():
            self.ui.mainContentFrame.setLayout(QVBoxLayout())
        self.ui.mainContentFrame.layout().addWidget(self.analysis_layout)

        # Events für Filter & Updates
        self.analysis_layout.chart_selector.currentIndexChanged.connect(self.update_analysis)
        self.analysis_layout.date_from.dateChanged.connect(self.update_analysis)
        self.analysis_layout.date_to.dateChanged.connect(self.update_analysis)

    def setup_analysis_categories(self):
        """Definiert Analyse-Kategorien"""
        self.analysen_categories = {
            "📂 Kundenstamm & Segmente": [
                "Segment-Analyse", "Bestandskundenanalyse", "Neukundenanalyse", "Kohortenanalyse"
            ],
            "📂 Kaufverhalten & Verkaufsdynamik": [
                "RFM-Analyse", "Kaufzyklusanalyse", "Durchschnittlicher Bestellwert (AOV)"
            ],
            "📂 Kundenabwanderung & Risikoanalyse": [
                "Churn-Analyse", "Survival-Analyse", "Inaktivitätsanalyse"
            ],
            "📂 Umsatz- & Absatzanalyse": [
                "Um- & Absatzanalyse", "Umsatzprognose", "Absatzprognose", "Benchmark-Analyse"
            ],
            "📂 Kundenwert & CLV": [
                "Customer Lifetime Value (CLV)", "Wiederkaufsrate"
            ]
        }
        
    def create_menu_bar(self):
        """Erstellt die Menüleiste mit Flyout-Menüs"""

        menu_bar = self.menuBar()  # Menüleiste erstellen

        # Dashboard-Menü
        if "Dashboard" in self.permissions:
            dashboard_menu = menu_bar.addMenu("🏠 Dashboard")
            dashboard_action = QAction("Dashboard anzeigen", self)
            dashboard_action.setShortcut(QKeySequence("Ctrl+D"))
            dashboard_action.triggered.connect(lambda: self.update_content("Dashboard"))
            dashboard_menu.addAction(dashboard_action)

        # Analysen-Menü mit Kategorien
        if "Analysen" in self.permissions:
            analysen_menu = menu_bar.addMenu("📊 Analysen")
            for category, analyses in self.analysen_categories.items():
                category_menu = analysen_menu.addMenu(category)  # Kategorie-Untermenü
                for analysis in analyses:
                    action = QAction(analysis, self)
                    action.triggered.connect(lambda _, a=analysis: self.update_content(a))
                    category_menu.addAction(action)

        # Vergleich-Menü
        if "Vergleich" in self.permissions:
            vergleich_menu = menu_bar.addMenu("📈 Vergleich")
            vergleich_action = QAction("Vergleich starten", self)
            vergleich_action.setShortcut(QKeySequence("Ctrl+V"))
            vergleich_action.triggered.connect(lambda: self.update_content("Vergleich"))
            vergleich_menu.addAction(vergleich_action)

        # Import-Menü
        if "Import" in self.permissions:
            import_menu = menu_bar.addMenu("📥 Import")
            
            import_action = QAction("Datei importieren", self)
            import_action.setShortcut(QKeySequence("Ctrl+I"))
            import_action.triggered.connect(lambda: self.update_content("Import"))
            import_menu.addAction(import_action)

            load_last_data_action = QAction("Letzte Daten laden", self)
            load_last_data_action.triggered.connect(self.load_last_saved_data)
            import_menu.addAction(load_last_data_action)  

            clear_data_action = QAction("Daten löschen", self)
            clear_data_action.triggered.connect(self.clear_data)
            import_menu.addAction(clear_data_action)

        # Export-Menü
        if "Export" in self.permissions:
            export_menu = menu_bar.addMenu("📤 Export")
            export_action = QAction("Datei exportieren", self)
            export_action.setShortcut(QKeySequence("Ctrl+E"))
            export_action.triggered.connect(lambda: self.update_content("Export"))
            export_menu.addAction(export_action)

        # Einstellungen-Menü
        if "Einstellungen" in self.permissions:
            einstellungen_menu = menu_bar.addMenu("⚙️ Einstellungen")
            einstellungen_action = QAction("Einstellungen öffnen", self)
            einstellungen_action.setShortcut(QKeySequence("Ctrl+S"))
            einstellungen_action.triggered.connect(lambda: self.update_content("Einstellungen"))
            einstellungen_menu.addAction(einstellungen_action)

            # Benutzerverwaltung-Menü 
            if "Benutzerverwaltung" in self.permissions:
                user_management_action = QAction("Benutzerverwaltung", self)
                user_management_action.triggered.connect(self.open_user_management)
                einstellungen_menu.addAction(user_management_action)

        # Themes-Menü
        themes_menu = menu_bar.addMenu("🎨 Themes")
        for theme in ["Luxuriös & Innovativ", "Serious Business-Mode", "Cyber Tech-Mode"]:
            theme_action = QAction(theme, self)
            theme_action.triggered.connect(lambda _, t=theme: self.change_theme(t))
            themes_menu.addAction(theme_action)
            
    def load_styles(self):
        """Lädt das QSS-Stylesheet und setzt es als Anwendungsthema."""
        
        stylesheet_path = os.path.join(BASE_DIR, "styles.qss")  # Absolute Pfadangabe

        try:
            with open(stylesheet_path, "r", encoding="utf-8") as file:  
                self.setStyleSheet(file.read())
        except FileNotFoundError:
            warning_message = "⚠️ Stylesheet 'styles.qss' nicht gefunden!"
            self.update_status_bar(warning_message, duration=15000)  # Warnung in Statusbar
            print(warning_message)  # für Debugging
            
            
    def change_theme(self, theme):
        """Wechselt das Theme zur Laufzeit & passt Farben von MainWindow, MainFrame, Statusbar & Labels an."""
        
        # Definiert die verfügbaren Themes
        theme_styles = {
            "Luxuriös & Innovativ": """
                QMainWindow { background: #242424; }  
                #mainContentFrame, QStatusBar {
                    background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #1E1E1E, stop:1 #292929);
                }
                QLabel { color: white; }
            """,
            "Serious Business-Mode": """
                QMainWindow { background: #DADADA; }  
                #mainContentFrame, QStatusBar {
                    background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #DDDDDD, stop:1 #9A9A9A);
                }
                QLabel { color: black; }
            """,
            "Cyber Tech-Mode": """
                QMainWindow { background: #080808; }  
                #mainContentFrame, QStatusBar {
                    background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #0F0F0F, stop:1 #1C1C1C);
                }
                QLabel { color: #18FFFF; }
            """
        }

        # Überprüfen, ob Theme existiert
        if theme not in theme_styles:
            self.show_error_message(f"❌ Unbekanntes Theme: {theme}")
            return  # ⛔ Funktion abbrechen

        # styles.qss laden
        try:
            with open("styles.qss", "r", encoding="utf-8") as file:
                base_styles = file.read()
        except FileNotFoundError:
            self.show_error_message("⚠️ styles.qss nicht gefunden! Standard-Styles werden ignoriert.")
            base_styles = ""

        # Kombiniert "styles.qss" mit dem Theme-Design
        final_styles = f"{base_styles}\n{theme_styles[theme]}"

        # Setzt das neue Stylesheet
        self.setStyleSheet(final_styles)

        # Sanfter Übergang 
        easing_type = QtCore.QEasingCurve.Type.InOutQuad if hasattr(QtCore.QEasingCurve.Type, "InOutQuad") else QtCore.QEasingCurve.Type.Linear
        self.animation = QPropertyAnimation(self.ui.mainContentFrame, b"windowOpacity")
        self.animation.setDuration(400)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.setEasingCurve(easing_type)
        self.animation.start()

        # Statusbar-Update 
        self.update_status_bar(f"🎨 Theme geändert: {theme}", duration=10000)

    def open_user_management(self):
        """Öffnet das Benutzerverwaltungs-Fenster."""
        
        # Prüfen, ob der aktuelle Benutzer Zugriff auf die Benutzerverwaltung hat
        if "Benutzerverwaltung" in self.permissions:
            try:
                dialog = UserManagementDialog(self)  # Dialog erstellen
                dialog.exec()  # Benutzerverwaltung öffnen
            except Exception as e:
                QMessageBox.critical(self, "Fehler", f"Fehler beim Öffnen der Benutzerverwaltung:\n{e}")
        else:
            QMessageBox.critical(
                self, "Zugriff verweigert",
                "⚠️ Zugriff verweigert: Nur Admins dürfen die Benutzerverwaltung öffnen."
            )
            
            
    def add_search_bar(self):
        """Fügt eine Suchleiste mit Autovervollständigung zur Menüleiste hinzu"""
        
        # 🔍 Menü für die Suche in der Menüleiste erstellen
        search_menu = self.menuBar().addMenu("🔍 Suche")

        # Verfügbare Seiten für die Suche generieren
        base_pages = ["Dashboard", "Vergleich", "Import", "Export", "Einstellungen"]
        analysis_pages = [analysis for sublist in self.analysen_categories.values() for analysis in sublist] \
            if hasattr(self, "analysen_categories") else []

        self.available_pages = base_pages + analysis_pages  # Speichern 

        # Suchleiste initialisieren
        self.search_bar = QLineEdit(self)
        self.search_bar.setPlaceholderText("🔍 Seiten durchsuchen...")

        # Autovervollständigung 
        completer = QCompleter(self.available_pages, self)
        completer.setCaseSensitivity(QtCore.Qt.CaseSensitivity.CaseInsensitive)
        self.search_bar.setCompleter(completer)

        # Navigation bei Eingabe auslösen
        self.search_bar.returnPressed.connect(self.navigate_to_search_result)

        # Suchleiste in die Menüleiste integrieren
        search_action = QWidgetAction(self)
        search_action.setDefaultWidget(self.search_bar)
        search_menu.addAction(search_action)
        
        
    def add_floating_button(self):
        """Erstellt einen Floating Action Button (FAB) mit sanftem Einblenden."""
        
        # Erstellt Floating-Button im mainContentFrame
        self.floating_button = QPushButton("➕", self.ui.mainContentFrame)
        self.floating_button.setObjectName("floatingButton")
        self.floating_button.setFixedSize(50, 50)  # Standardgröße des Buttons
        
        # Stylesheet für das Button-Design
        self.floating_button.setStyleSheet("""
            QPushButton {
                background-color: #FF6F00;
                color: white;
                font-size: 18px;
                border-radius: 25px;
                border: none;
            }
            QPushButton:hover {
                background-color: #E65100;
            }
        """)

        # Klick-Ereignis für den Button (Platzhalterfunktion)
        self.floating_button.clicked.connect(lambda: self.show_error_message("Noch keine Funktion!"))

        # Positioniere den Button dynamisch bei Größenänderungen
        self.ui.mainContentFrame.installEventFilter(self) 
        self.resize_floating_button()

        # Sanfte Einblendung 
        self.animation_fab = QPropertyAnimation(self.floating_button, b"windowOpacity")  # ✅ Speichert Animation als Instanzvariable
        self.animation_fab.setDuration(400)
        self.animation_fab.setStartValue(0)
        self.animation_fab.setEndValue(1)
        self.animation_fab.start()

        self.floating_button.show()
        

    def eventFilter(self, obj, event):
        """Überwacht UI-Ereignisse für dynamische Button-Anpassung."""
        if obj == self.ui.mainContentFrame and event.type() == QtCore.QEvent.Type.Resize:
            self.resize_floating_button()
        return QObject.eventFilter(self, obj, event)  # ✅ Richtige Methode direkt aufrufen


    def resize_floating_button(self):
        """Passt die Position des Floating-Buttons automatisch an das Fenster an."""
        if self.floating_button:
            frame_width = self.ui.mainContentFrame.width()
            frame_height = self.ui.mainContentFrame.height()

            # Button-Größe anpassen, falls Fenster zu klein ist
            button_size = 50 if frame_width > 400 else 35  # Kleinerer Button bei kleinen Fenstern
            self.floating_button.setFixedSize(button_size, button_size)

            # Position des Buttons anpassen (rechts unten mit Abstand)
            margin = 20
            self.floating_button.move(frame_width - button_size - margin, frame_height - button_size - margin)

        
    def navigate_to_search_result(self):
        """Durchsucht die Seiten und navigiert zur entsprechenden Ansicht"""
        
        search_text = self.search_bar.text().strip()  # Eingabetext bereinigen
        
        # Liste der verfügbaren Seiten (self.available_pages)
        if search_text in self.available_pages:
            self.update_content(search_text)  
        else:
            QMessageBox.critical(self, "Fehler", f"❌ Die Seite '{search_text}' wurde nicht gefunden.")
            

    def setup_drag_drop_area(self):
        """ Erstellt die Drag-and-Drop-Fläche und stellt sicher, dass sie existiert. """
        
        # Falls `self.dragDropArea` noch nicht existiert, erstelle es
        if not hasattr(self, "dragDropArea") or self.dragDropArea is None:
            print("🛠 Erstelle `dragDropArea`...")
            self.dragDropArea = DragDropArea(self)
            self.dragDropArea.setFixedSize(350, 200)
            self.dragDropArea.setVisible(False)  # Standardmäßig verstecken
        else:
            print("✅ `dragDropArea` existiert bereits.")
        
        
    def update_status_bar(self, message, duration=10000):
        """Aktualisiert die Statusbar mit der gegebenen Nachricht."""
        
        if self.statusBar():  # Prüfen, dass eine Statusbar existiert
            self.statusBar().showMessage(f"ℹ️ {message}", duration)
        else:
            print(f"[StatusBar] {message}")  
            
            
    def show_error_message(self, error_message):
        """Zeigt eine Fehlermeldung in der Statusleiste, aber blockiert nicht das Laden."""

        # Fehlertext für Statusbar formatieren (max. 100 Zeichen)
        status_message = f"❌ Fehler: {error_message[:100]}..." if len(error_message) > 100 else f"❌ Fehler: {error_message}"
        
        # Fehlermeldung in Statusbar anzeigen (nur wenn GUI sichtbar ist)
        if hasattr(self, "statusBar") and self.statusBar():
            self.statusBar().showMessage(status_message, 10000)

        # Kritische Fehlermeldung als PopUp, aber nur wenn Fenster sichtbar
        if self.isVisible():
            QMessageBox.critical(self, "Fehler", error_message)
        else:
            print(f"⚠️ Fehler während des Startens: {error_message}") 
        
        
    def load_previous_data(self):
        """Lädt beim Start des Programms die zuletzt gespeicherten Daten, falls vorhanden."""

        # Falls keine gespeicherten Daten vorhanden sind, Warnung ausgeben
        if not os.path.exists("saved_data.pkl"):
            print("ℹ️ Keine gespeicherten Daten gefunden.")
            return  # Abbruch

        print("🔄 Lade letzte gespeicherte Daten...")

        try:
            # Speicherdatei öffnen & Daten laden
            with open("saved_data.pkl", "rb") as f:
                df = pickle.load(f)

            # Falls df kein DataFrame oder leer ist, Warnung ausgeben
            if not isinstance(df, pd.DataFrame) or df.empty:
                print("⚠️ Fehler: Gespeicherte Daten sind leer oder ungültig.")
                return  # Keine gültigen Daten, Abbruch

            # Speichert die geladenen Daten in "self.current_df"
            self.current_df = df

            # Falls Tabelle nicht existiert, neu erstellen
            if self.tableWidget is None:
                self.create_table_widget()

            # Tabelle mit den geladenen Daten aktualisieren
            self.update_table(df)
            self.format_table_widget(self.tableWidget)
            self.adjust_table_rows(self.tableWidget)

            # Falls Daten vorhanden sind, Drag-and-Drop verstecken & Tabelle anzeigen
            if self.dragDropArea and df is not None and not df.empty:
                self.dragDropArea.setVisible(False)
                self.tableWidget.setVisible(True)

            # UI-Updates verarbeiten, um Freeze zu verhindern
            QtWidgets.QApplication.processEvents()

            # Floating-Button richtig positionieren
            self.resize_floating_button()
            self.ui.mainContentFrame.updateGeometry()

            # Statusbar aktualisieren
            self.update_status_bar("✅ Letzte gespeicherte Daten erfolgreich geladen!", duration=10000)

            # Prüfen, ob bereits Analyse-Ergebnisse vorhanden sind
            analysis_results_path = Path("/Users/marcus/Documents/GitHub/Abschlussprojekt/main_project/PyQt6/analysis/analysis_results")

            if analysis_results_path.exists() and any(analysis_results_path.glob("*.html")):
                print("✅ Analyseergebnisse vorhanden – kein Neuladen erforderlich.")
                return

            print("🚀 Keine gespeicherten Analysen gefunden – Starte Analyseprozess...")
            self.process_loaded_data(df)  # Analysen nur starten, wenn sie noch nicht existieren

        except Exception as e:
            print(f"❌ Fehler beim Laden von saved_data.pkl: {e}")
            QMessageBox.critical(self, "Fehler", f"❌ Fehler beim Laden der gespeicherten Daten: {e}")
        
        
    def create_table_widget(self):
        """Erstellt das TableWidget, falls es nicht existiert, und setzt das richtige Format."""

        if self.tableWidget is not None:
            print("ℹ️ `tableWidget` existiert bereits – mache es sichtbar.")
            self.tableWidget.setVisible(True)
            return  # Falls bereits vorhanden, Abbruch

        print("🛠 Erstelle `tableWidget`...")

        try:
            self.tableWidget = QtWidgets.QTableWidget(self.ui.mainContentFrame)
            self.tableWidget.setObjectName("tableWidget")

            # Größe & Layout-Einstellungen
            self.tableWidget.setFixedSize(1300, 800)
            self.tableWidget.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)

            # Header-Einstellungen
            self.tableWidget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
            self.tableWidget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.ResizeToContents)

            # Falls "gridLayout" existiert, Tabelle hinzufügen
            if hasattr(self.ui, "gridLayout") and self.ui.gridLayout is not None:
                self.ui.gridLayout.addWidget(self.tableWidget, 0, 0, 1, 1)
            else:
                # Falls "gridLayout" fehlt, eigenes Layout erstellen
                print("⚠️ `gridLayout` nicht gefunden! Erstelle eigenes Layout.")
                layout = QtWidgets.QVBoxLayout(self.ui.mainContentFrame)
                layout.addWidget(self.tableWidget)
                self.ui.mainContentFrame.setLayout(layout)

            # Standardmäßig sichtbar machen
            self.tableWidget.setVisible(True)

            # Formatierung & Zeilenanpassung
            self.format_table_widget(self.tableWidget)
            self.adjust_table_rows(self.tableWidget)

            print("✅ `tableWidget` wurde erfolgreich erstellt & formatiert!")

        except Exception as e:
            self.show_error_message(f"❌ Fehler beim Erstellen der Tabelle: {e}")

            
    def format_table_widget(self, tableWidget):
        """Sorgt dafür, dass die Tabelle das gleiche Format hat wie bei neuem Import."""
        
        if tableWidget is None:
            return

        print("🎨 Formatiere TableWidget...")

        # Header sichtbar machen
        tableWidget.horizontalHeader().setVisible(True)
        tableWidget.verticalHeader().setVisible(True)
        
        # Header-Höhe explizit setzen
        tableWidget.horizontalHeader().setFixedHeight(60)

        # Spalten- und Zeilenkonfiguration
        tableWidget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        tableWidget.horizontalHeader().setStretchLastSection(True)
        tableWidget.horizontalHeader().setMinimumSectionSize(120)
        tableWidget.verticalHeader().setFixedWidth(45)  # Breite der vertikalen Header

        # Zeilenhöhe dynamisch anpassen
        total_height = tableWidget.viewport().height()
        row_count = max(1, tableWidget.rowCount())  # Sicher stellen, dass es mindestens 1 Zeile gibt
        row_height = total_height // row_count

        for row in range(row_count):  
            tableWidget.setRowHeight(row, row_height)

        # Spaltenbreite automatisch anpassen
        tableWidget.resizeColumnsToContents()

        # UI-Updates, um Freeze zu vermeiden
        QtWidgets.QApplication.processEvents()

        # UI-Layout aktualisieren
        self.ui.mainContentFrame.updateGeometry()
        self.ui.gridLayout.invalidate()

        print("✅ TableWidget-Formatierung abgeschlossen!")
        
        
    def update_table(self, data):
        """Aktualisiert die Tabelle mit neuen Daten und stellt sicher, dass sie korrekt formatiert bleibt."""

        # Prüfen, ob "data" ein gültiger DataFrame ist
        if not isinstance(data, pd.DataFrame) or data.empty:
            print("⚠️ Fehler: Ungültiges oder leeres Datenformat!")
            self.show_error_message("⚠️ Ungültiges oder leeres Datenformat!")
            self.tableWidget.clear()
            self.tableWidget.setRowCount(0)
            self.tableWidget.setColumnCount(0)
            return

        print(f"📊 Aktualisiere Tabelle mit {len(data)} Zeilen & {len(data.columns)} Spalten...")

        # Tabelle während der Aktualisierung sperren, um Events zu verhindern
        self.tableWidget.blockSignals(True)

        # Größe der Tabelle setzen (Anzahl der Zeilen & Spalten)
        self.tableWidget.setRowCount(len(data))
        self.tableWidget.setColumnCount(len(data.columns))
        self.tableWidget.setHorizontalHeaderLabels(data.columns)

        # Header-Höhe explizit setzen
        self.tableWidget.horizontalHeader().setFixedHeight(60)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.ResizeToContents)

        # Asynchrone Verarbeitung, um UI nicht zu blockieren
        QtCore.QTimer.singleShot(50, lambda: self._update_table_internal(data))

    def _update_table_internal(self, data):
        """Interne Methode für Tabellenaktualisierung, um UI-Blockade zu verhindern."""
        try:
            # Daten in die Tabelle einfügen
            for row in range(len(data)):
                for col in range(len(data.columns)):
                    item = QTableWidgetItem(str(data.iloc[row, col]))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.tableWidget.setItem(row, col, item)

            # Tabelle wieder freigeben
            self.tableWidget.blockSignals(False)

            # Formatierung & Layout aktualisieren
            self.format_table_widget(self.tableWidget)
            self.adjust_table_rows(self.tableWidget)

            # Floating-Button & UI-Layout anpassen
            self.resize_floating_button()
            self.ui.mainContentFrame.updateGeometry()

            # Tabelle sichtbar machen
            self.tableWidget.setVisible(True)
            self.dragDropArea.setVisible(False)

            print("✅ Tabellenaktualisierung abgeschlossen!")

        except Exception as e:
            print(f"❌ Fehler beim Aktualisieren der Tabelle: {e}")
            self.show_error_message(f"❌ Fehler beim Aktualisieren der Tabelle: {e}")
        

    def clear_data(self):
        """Löscht aktuelle Daten, Tabellen und gespeicherte Analysen."""
        
        confirmation = QMessageBox.question(
            self, "Daten löschen", "Möchtest du wirklich ALLE Daten & Analysen löschen?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirmation == QMessageBox.StandardButton.No:
            return

        # Daten im Programm zurücksetzen
        self.current_df = None

        # Tabelle leeren und verstecken
        if self.tableWidget:
            self.tableWidget.clear()
            self.tableWidget.setRowCount(0)
            self.tableWidget.setColumnCount(0)
            self.tableWidget.setVisible(False)

        # Drag-and-Drop anzeigen
        if self.dragDropArea:
            self.dragDropArea.setVisible(True)

        # Gespeicherte Daten-Datei löschen
        data_file = Path("saved_data.pkl")
        if data_file.exists():
            try:
                data_file.unlink()
                print("🗑 Gespeicherte Datei gelöscht.")
                self.update_status_bar("📁 Gespeicherte Daten erfolgreich gelöscht!")
            except Exception as e:
                self.show_error_message(f"⚠️ Fehler beim Löschen von saved_data.pkl: {e}")

        # Analyse-Ordner leeren & löschen
        analysis_results_path = Path("/Users/marcus/Documents/GitHub/Abschlussprojekt/main_project/PyQt6/analysis/analysis_results")

        if analysis_results_path.exists():
            try:
                for file in analysis_results_path.glob("*.html"):  # Löscht alle gespeicherten Diagramme
                    file.unlink()
                print("🗑 Alle gespeicherten Analysen wurden gelöscht.")
                self.update_status_bar("📊 Alle gespeicherten Analysen wurden erfolgreich gelöscht!")

                # Falls der Ordner jetzt leer ist, löschen
                if not any(analysis_results_path.iterdir()):
                    analysis_results_path.rmdir()
                    print("📁 Der leere Ordner 'analysis_results' wurde entfernt.")
            except Exception as e:
                self.show_error_message(f"⚠️ Fehler beim Löschen der Analyse-Dateien: {e}")

        # Status-Bar-Update
        self.update_status_bar("❌ Alle Daten & Analysen wurden gelöscht!", duration=10000)

        
    def adjust_table_rows(self, tableWidget):
        """Passt die Zeilenhöhe so an, dass sie den gesamten Tabellenbereich ausfüllen."""
        
        if tableWidget is None or tableWidget.rowCount() == 0:
            return  # Abbruch, falls keine Zeilen existieren oder "tableWidget" nicht definiert ist

        print("📏 Passe Zeilenhöhe dynamisch an...")

        # Nutze die Viewport-Höhe für eine exakte Berechnung
        total_height = tableWidget.viewport().height()
        row_height = total_height // tableWidget.rowCount()

        # Maximale Zeilenhöhe begrenzen (z. B. 100 Pixel)
        row_height = min(row_height, 100)

        # Setze die Höhe jeder Zeile
        for row in range(tableWidget.rowCount()):
            tableWidget.setRowHeight(row, row_height)

        # UI-Updates, um Freezes zu verhindern
        QtWidgets.QApplication.processEvents()

        print(f"✅ Zeilenhöhe angepasst: {row_height}px pro Zeile")
            
    
    def load_last_saved_data(self, content):
        """Lädt gespeicherte Daten und zeigt sie nur in der Import-Tabelle an."""
        
        # Falls keine gespeicherten Daten vorhanden sind, Warnung anzeigen
        if not os.path.exists("saved_data.pkl"):
            print("❌ Keine gespeicherten Daten gefunden.")
            QMessageBox.warning(self, "Fehler", "⚠️ Es wurden keine gespeicherten Daten gefunden.")
            return

        print("📂 Lade gespeicherte Daten...")

        try:
            with open("saved_data.pkl", "rb") as f:
                df = pickle.load(f)

            # Falls df kein DataFrame oder leer ist, Abbruch
            if not isinstance(df, pd.DataFrame) or df.empty:
                QMessageBox.warning(self, "Fehler", "⚠️ Die gespeicherten Daten sind ungültig oder leer.")
                print("❌ Fehler: Gespeicherte Daten sind leer oder nicht im richtigen Format.")
                return

            # Speichert die geladenen Daten in `self.current_df`
            self.current_df = df

            # Prüfen, dass die Tabelle existiert
            if self.tableWidget is None:
                self.create_table_widget()

            # ✅ Tabelle nur aktualisieren, wenn die Import-Seite aktiv ist
            if content == "Import":
                self.update_status_bar("🔄 Letzte gespeicherte Daten werden geladen...")

                # ✅ Tabelle mit gespeicherten Daten aktualisieren
                self.update_table(df)
                self.format_table_widget(self.tableWidget)
                self.adjust_table_rows(self.tableWidget)

                # Falls Daten vorhanden sind, Drag-and-Drop verstecken & Tabelle anzeigen
                if self.dragDropArea and df is not None and not df.empty:
                    self.dragDropArea.setVisible(False)
                    self.tableWidget.setVisible(True)

                # ✅ UI-Updates verarbeiten, um Freeze zu verhindern
                QtWidgets.QApplication.processEvents()

                # ✅ Floating-Button richtig positionieren
                self.resize_floating_button()
                self.ui.mainContentFrame.updateGeometry()

                self.update_status_bar("✅ Letzte gespeicherte Daten erfolgreich geladen!", duration=10000)

            else:
                print("🔄 Daten geladen, aber nicht angezeigt, weil die Import-Seite nicht aktiv ist.")

            # ✅ Nach erfolgreichem Laden Analysen starten – unabhängig von der Import-Seite!
            self.process_loaded_data(df)

        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"❌ Fehler beim Laden der gespeicherten Daten: {e}")
            print(f"❌ Fehler beim Laden von saved_data.pkl: {e}")
            
            
    def process_loaded_data(self, df):
        """Startet automatisch die relevanten Analysen nach dem Laden der Daten, falls notwendig."""
        
        if df is None or df.empty:
            print("⚠️ Keine Daten für die Analyse verfügbar.")
            self.update_status_bar("⚠️ Keine Daten für Analysen vorhanden.")
            return  # Bricht die Funktion ab, wenn keine Daten geladen wurden

        print("🚀 Überprüfe, ob Analysen bereits existieren...")

        # Prüfen, ob bereits analysierte Daten vorliegen
        analysis_results_path = Path("/Users/marcus/Documents/GitHub/Abschlussprojekt/main_project/PyQt6/analysis/analysis_results")
        
        if analysis_results_path.exists() and any(analysis_results_path.glob("*.html")):
            print("✅ Bereits vorhandene Analyseergebnisse gefunden. Kein Neuladen notwendig.")
            return

        print("🚀 Keine gespeicherten Analysen gefunden – Starte Analyseprozess...")
        self.update_analysis()  # Analysen nur starten, wenn sie nicht existieren

        self.update_status_bar("✅ Analysen erfolgreich gestartet!")
        
        
    def update_analysis(self):
        """Lädt die Analyse, falls sie existiert. Falls nicht, wird sie neu generiert."""
        
        if self.current_df is None or self.current_df.empty:
            print("⚠️ Keine Daten geladen – Analysen werden nicht gestartet.")
            return  
        
        selected_analysis = self.analysis_layout.chart_selector.currentText()
        print(f"📊 Debug: Starte Analyse für '{selected_analysis}'")
        
        # Überprüfen, ob "self.analysis_layout" existiert
        if not hasattr(self, "analysis_layout"):
            print("❌ Fehler: Analyse-Layout nicht gefunden!")
            self.show_error_message("❌ Fehler: Analyse-Layout nicht gefunden!")
            return

        # Die aktuell ausgewählte Analyse abrufen
        selected_analysis = self.analysis_layout.chart_selector.currentText()
        print(f"📊 Debug: Ausgewählte Analyse = '{selected_analysis}'")  

        # Mapping der Analysen zu den Funktionen
        analysis_mapping = {
            "Segmentanalyse": generate_segment_analysis,
            "Bestandskundenanalyse": generate_bestandskunden_analysis,
            "Neukundenanalyse": generate_neukunden_analysis,
            "Kohortenanalyse": generate_kohorten_analysis,
            "RFM-Analyse": generate_rfm_analysis,
            "Kaufzyklusanalyse": generate_kaufzyklus_analysis,
            "AOV-Analyse": generate_aov_analysis,
            "Churn-Analyse": generate_churn_analysis,
            "Survival-Analyse": generate_survival_analysis,
            "Inaktivitätsanalyse": generate_dormant_analysis,
            "Umsatz- & Absatzanalyse": generate_umsatz_absatz_analysis,
            "Umsatzprognose": generate_umsatzprognose,
            "Benchmark-Analyse": generate_benchmark_analysis,
            "CLV-Analyse": generate_clv_analysis,
            "Wiederkaufsanalyse": generate_wiederkaufsrate,
        }

        # Prüfen, ob die gewählte Analyse gültig ist
        if selected_analysis not in analysis_mapping:
            error_msg = f"❌ Fehler: '{selected_analysis}' ist keine gültige Analyse!"
            print(error_msg)
            print(f"📜 Verfügbare Optionen: {list(analysis_mapping.keys())}")
            self.show_error_message(error_msg)
            return

        # Starte die ausgewählte Analyse
        try:
            analysis_results = analysis_mapping[selected_analysis]()
        except Exception as e:
            self.show_error_message(f"⚠️ Fehler beim Ausführen der Analyse: {e}")
            return

        # Überprüfen, ob die HTML-Ergebnisse existieren
        if analysis_results:
            first_html_path = list(analysis_results.values())[0]  # Nimmt die erste Datei
            if os.path.exists(first_html_path):
                print(f"✅ Analyse existiert bereits: {first_html_path}")
                self.analysis_layout.chart_view.setUrl(QUrl.fromLocalFile(os.path.abspath(first_html_path)))
            else:
                print(f"❌ Fehler: HTML-Datei nicht gefunden – {first_html_path}")
                self.show_error_message(f"❌ Fehler: Analyse-Ergebnis nicht gefunden ({first_html_path})")
        else:
            self.show_error_message("❌ Fehler: Keine Ergebnisse aus der Analyse-Funktion erhalten.")
            
            
    def load_data(self):
        """Lädt gespeicherte Daten aus `saved_data.pkl`, wenn sie existieren und gültig sind."""
        
        self.current_df = None  # Standardwert setzen
        
        if not os.path.exists(DATA_FILE):
            print("ℹ️ Keine gespeicherten Daten gefunden. Erstelle leeren DataFrame.")
            return pd.DataFrame()  # Neuen leeren DataFrame zurückgeben

        try:
            with open(DATA_FILE, "rb") as f:
                df = pickle.load(f)

            # Überprüfen, ob geladene Daten ein DataFrame sind
            if isinstance(df, pd.DataFrame) and not df.empty:
                print(f"✅ Erfolgreich geladene Daten: {len(df)} Zeilen, {len(df.columns)} Spalten")
                return df
            else:
                print("⚠️ Warnung: Geladene Daten sind leer oder nicht im richtigen Format.")
                return pd.DataFrame()  # Leeren DataFrame zurückgeben
        
        except Exception as e:
            print(f"⚠️ Fehler beim Laden der Daten: {e}")
            return pd.DataFrame()  # Fallback: Leeren DataFrame zurückgeben
            
            
    def import_csv(self, file_path):
        """Importiert Daten aus einer Datei und aktualisiert die Tabelle."""
        print(f"🔍 Debug: Datei-Pfad: {file_path}")

        # Falls Datei nicht existiert, Fehlermeldung ausgeben & Abbrechen
        if not os.path.exists(file_path):
            self.show_error_message(f"❌ Datei nicht gefunden: {file_path}")
            return

        try:
            # Prüfen, ob "self.import_csv" existiert
            if hasattr(self, "import_csv") and self.import_csv:
                print("✅ `import_csv` existiert, starte Import...")
                self.import_csv.import_from_file(file_path)
            else:
                print("❌ Fehler: `import_csv` wurde nicht korrekt initialisiert!")
                return

            # Daten nach dem Import prüfen
            if self.current_df is None or self.current_df.empty:
                print("⚠️ Warnung: Importierte Daten sind leer!")
                self.show_error_message("⚠️ Importierte Datei enthält keine Daten!")
                return

            # Falls Tabelle nicht existiert, neu erstellen
            if self.tableWidget is None:
                self.create_table_widget()

            # Tabelle mit importierten Daten aktualisieren
            self.update_table(self.current_df)
            self.format_table_widget(self.tableWidget)
            self.adjust_table_rows(self.tableWidget)

            # Falls Daten vorhanden sind, Drag-and-Drop verstecken & Tabelle anzeigen
            if self.dragDropArea and self.current_df is not None and not self.current_df.empty:
                self.dragDropArea.setVisible(False)
                self.tableWidget.setVisible(True)

            # UI-Updates verarbeiten, um Freeze zu verhindern
            QtWidgets.QApplication.processEvents()

            # Floating-Button richtig positionieren
            self.resize_floating_button()
            self.ui.mainContentFrame.updateGeometry()

            # Statusbar-Update nach erfolgreichem Import
            self.update_status_bar(f"✅ Datei erfolgreich importiert: {file_path}", duration=10000)

            # Gespeicherte Daten direkt laden
            self.load_previous_data()

        except Exception as e:
            print(f"❌ Fehler beim Import: {e}")
            self.show_error_message(f"❌ Fehler beim Import: {e}")
            
        
    def update_content(self, content):
        """Aktualisiert den Seiteninhalt dynamisch und stellt sicher, dass die Tabelle auf der Import-Seite bleibt."""

        print(f"🔄 Wechsel zur Seite: {content}")
        self.current_page = content
        self.ui.mainContentLabel.setText(f"⏳ Lade {content}...")

        # Falls die Tabelle nicht existiert, erstelle sie sofort
        if self.tableWidget is None:
            self.create_table_widget()  # 🔹 Stellt sicher, dass `self.tableWidget` existiert

        # Falls nicht "Import", Tabelle und Drag-and-Drop ausblenden
        if content != "Import":
            if self.tableWidget:
                self.tableWidget.setVisible(False)  
            if self.dragDropArea:
                self.dragDropArea.setVisible(False)
            return  # Funktion beenden, um unnötige Berechnungen zu vermeiden

        # Alle Widgets aus `mainContentFrame` entfernen, außer "dragDropArea" & "tableWidget"
        for i in reversed(range(self.ui.gridLayout.count())):
            widget = self.ui.gridLayout.itemAt(i).widget()
            if widget and widget not in [self.dragDropArea, self.tableWidget]:
                widget.hide()

        # Import-Seite
        if content == "Import":
            self.ui.mainContentLabel.setText("📥 Datei importieren")
            print("📥 Wechsle zur Import-Seite")

            # Falls Drag-and-Drop nicht existiert, neu erstellen
            if not isinstance(self.dragDropArea, DragDropArea):
                self.dragDropArea = DragDropArea(self)
                self.dragDropArea.setFixedSize(350, 200)

            # Import-Seiten-Layout erstellen
            self.importPage = QtWidgets.QWidget(self.ui.mainContentFrame)
            import_layout = QtWidgets.QVBoxLayout(self.importPage)

            self.dragDropArea.setParent(self.importPage)
            self.tableWidget.setParent(self.importPage)

            # Falls Daten vorhanden sind, Tabelle anzeigen & Drag-and-Drop ausblenden
            if self.current_df is not None and not self.current_df.empty:
                print("✅ Zeige gespeicherte Daten in der Tabelle")
                self.update_table(self.current_df)
                self.format_table_widget(self.tableWidget)
                self.adjust_table_rows(self.tableWidget)

                self.dragDropArea.setVisible(False)
                self.tableWidget.setVisible(True)
            else:
                print("⚠️ Keine gespeicherten Daten – Zeige Drag-and-Drop")
                self.dragDropArea.setVisible(True)
                self.tableWidget.setVisible(False)

            # Layout setzen 
            import_layout.addWidget(self.dragDropArea, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
            import_layout.addWidget(self.tableWidget, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)

            self.importPage.setLayout(import_layout)
            self.ui.gridLayout.addWidget(self.importPage, 0, 0, 1, 1)
            self.resize_floating_button()
            self.ui.mainContentFrame.updateGeometry()

            self.update_status_bar("📥 Import-Seite geladen. Bitte Datei auswählen.")

        #  Analyse-Seiten
        elif content in self.analysis_pages:
            print(f"📊 Lade Analyse-Seite: {content}")
            self.ui.mainContentLabel.setText(f"📊 {content}")
            self.update_analysis()

        # Dashboard 
        elif content == "Dashboard":
            print("🏠 Wechsel zum Dashboard")
            self.ui.mainContentLabel.setText("🏠 Willkommen im Dashboard")
            self.statusBar().showMessage("🏠 Dashboard geladen", 5000)

            # Tabelle & Drag-and-Drop sicher ausblenden
            if self.tableWidget:
                self.tableWidget.setVisible(False)
            if self.dragDropArea:
                self.dragDropArea.setVisible(False)

            # Platzhalter für das Dashboard setzen
            placeholder = QtWidgets.QLabel("📊 Übersicht & Statistiken folgen hier...", self.ui.mainContentFrame)
            placeholder.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            self.ui.gridLayout.addWidget(placeholder, 0, 0, 1, 1)

        # Alle anderen Seiten
        else:
            print(f"📄 Lade allgemeine Seite: {content}")
            self.ui.mainContentLabel.setText(f"🏠 {content}")
            self.statusBar().showMessage(f"Seite '{content}' geladen", 5000)

            placeholder = QtWidgets.QLabel(f"Inhalt für {content}", self.ui.mainContentFrame)
            placeholder.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            self.ui.gridLayout.addWidget(placeholder, 0, 0, 1, 1)

        # UI-Updates verarbeiten
        QtWidgets.QApplication.processEvents()
            
    def animate_page_transition(self, content):
        """Führt eine sanfte Seitenwechsel-Animation aus."""
        
        # Setzt den neuen Text vor der Animation
        self.ui.mainContentLabel.setText(content)

        # Erstellen und Speichern der Animation in einer Variable
        self.animation = QPropertyAnimation(self.ui.mainContentLabel, b"windowOpacity")
        self.animation.setDuration(250)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)

        # Weicher Übergang
        self.animation.setEasingCurve(QtCore.QEasingCurve.InOutQuad)

        # Start der Animation
        self.animation.start()
        
    def resizeEvent(self, event):
        """Reagiert auf Änderungen der Fenstergröße und passt die UI-Elemente dynamisch an."""
        
        super().resizeEvent(event)  # Resize-Verhalten beibehalten

        # Falls die Import-Seite aktiv ist, Tabellenzeilen anpassen
        if hasattr(self, "tableWidget") and self.tableWidget and self.current_page == "Import":
            self.adjust_table_rows(self.tableWidget)

        # Floating-Button ebenfalls anpassen
        self.resize_floating_button()

        # Layout-Updates ausführen
        self.ui.mainContentFrame.updateGeometry()
        QtWidgets.QApplication.processEvents()  # UI-Updates sofort verarbeiten

if __name__ == "__main__":
    
    # Erstellt die QApplication-Instanz (Hauptanwendung)
    app = QApplication(sys.argv)
    
    # Erstellt das Hauptfenster der Anwendung
    window = MainApp()
    window.show() # Zeigt die Anwendung
    
    # Beendet das Programm, wenn Hauptfenster geschlossen wird
    sys.exit(app.exec())