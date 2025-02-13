#  Plattformunabhängige Imports
import sys
import os
import json
import pandas as pd
import pickle

#  Basisverzeichnis setzen
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = "saved_data.pkl"  # Datei, in der die gespeicherten Daten abgelegt werden

# Sicherstellen, dass alle Module gefunden werden
sys.path.append(os.path.join(BASE_DIR, "gui"))
sys.path.append(os.path.join(BASE_DIR, "data_import"))
sys.path.append(os.path.join(BASE_DIR, "analysis"))
sys.path.append(os.path.join(BASE_DIR, "export"))
sys.path.append(os.path.join(BASE_DIR, "users"))

#  PyQt6-Imports für die GUI
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QMenuBar, QLineEdit, QWidgetAction, 
    QCompleter, QMessageBox, QPushButton, QFileDialog, QTableWidget, 
    QTableWidgetItem, QVBoxLayout
)
from PyQt6 import QtWidgets
from PyQt6.QtGui import (
    QAction, 
    QKeySequence,
    QFont
)
from PyQt6 import QtCore

from PyQt6.QtCore import (
    QPropertyAnimation,
    Qt,
    QUrl
)

from PyQt6.QtWebEngineWidgets import QWebEngineView


#  Eigene Module importieren
from gui.gui_main_window import Ui_MainWindow
from gui.gui_benutzerverwaltung import UserManagementDialog
from data_import.import_csv import ImportCSV
from data_import.import_drag_and_drop import DragDropArea
from analysis.analysis_layout import AnalysisLayout

from analysis.Kunden.segment_analyse import generate_segment_analysis
from analysis.Kunden.bestandskunden import generate_bestandskunden_analysis
from analysis.Kunden.neukunden import generate_neukunden_analysis
from analysis.Kunden.Kohorten import generate_kohorten_analysis
from analysis.Kaufverhalten.rfm import generate_rfm_analysis
from analysis.Kaufverhalten.kaufzyklus import generate_kaufzyklus_analysis
from analysis.Kaufverhalten.aov import generate_aov_analysis
from analysis.Kundenbewegung.churn import generate_churn_analysis
from analysis.Kundenbewegung.survival import generate_survival_analysis
from analysis.Kundenbewegung.inaktivität import generate_dormant_analysis
from analysis.Vertrieb.um_absatz import generate_umsatz_absatz_analysis
from analysis.Vertrieb.umsatzprognose import generate_umsatzprognose
from analysis.Vertrieb.benchmark import generate_benchmark_analysis
from analysis.Kundenwert.clv import generate_clv_analysis
from analysis.Kundenwert.wiederkaufsanalyse import generate_wiederkaufsrate

# 

# Main-Window
class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)  # UI aus main_window.py laden

        # 
        self.dragDropArea = None  # Drag-and-Drop erst später erstellen
        self.tableWidget = None  # Tabelle erst später erstellen
        self.current_df = None  # Keine geladenen Daten beim Start
        self.current_page = None  # Speichert die aktuelle Seite
        
        # Analysis Layout in mainContentFrame einbinden
        self.analysis_layout = AnalysisLayout()
        if not self.ui.mainContentFrame.layout():
            self.ui.mainContentFrame.setLayout(QVBoxLayout())
        self.ui.mainContentFrame.layout().addWidget(self.analysis_layout)
        
        # Events für Filter & Update-Funktionalität
        self.analysis_layout.chart_selector.currentIndexChanged.connect(self.update_analysis)
        self.analysis_layout.date_from.dateChanged.connect(self.update_analysis)
        self.analysis_layout.date_to.dateChanged.connect(self.update_analysis)

        # Benutzerverwaltung laden, Standardrolle setzen 
        self.user_role = "admin"  # Standard-Benutzerrolle (Admin)
        self.permissions = self.load_user_permissions()  # Berechtigungen aus benutzerverwaltung.json laden

        # Vordefinierte Analyse-Kategorien für verschiedene Bereiche
        self.analysen_categories = {
            "📂 Kundenstamm & Segmente": [
                "Segment-Analyse", 
                "Bestandskundenanalyse",
                "Neukundenanalyse",
                "Kohortenanalyse"
                ],
            
            "📂 Kaufverhalten & Verkaufsdynamik": [
                "RFM-Analyse", 
                "Kaufzyklusanalyse", 
                "Durchschnittlicher Bestellwert (AOV)"
                ],
            
            "📂 Kundenabwanderung & Risikoanalyse": [
                "Churn-Analyse",
                "Survival-Analyse",
                "Inaktivitätsanalyse"
                ],
            
            "📂 Umsatz- & Absatzanalyse": [
                "Umsatzprognose", "Absatzprognose",
                "Benchmark-Analyse"
                ],
            
            "📂 Kundenwert & CLV": [
                "Customer Lifetime Value (CLV)",
                "Wiederkaufsrate"
                ]
        }

        # Laden des Stylesheet
        self.load_styles()

        # Menüleiste initialisieren
        self.create_menu_bar()

        # Setzt Standard-Theme der Anwendung
        self.change_theme("Luxuriös & Innovativ")

        # Suchleiste hinzufügen
        self.add_search_bar()

        # Floating-Button hinzufügen 
        self.add_floating_button()

        # Startseite initialisieren
        #self.update_status_bar("Willkommen im Analyse-Tool!")
        self.update_content("Dashboard")
        
        # Erstellen der Drag and Drop Area
        self.dragDropArea = DragDropArea(self)  # ✅ Wird nun immer initialisiert
        self.dragDropArea.setFixedSize(350, 200)
        self.dragDropArea.setVisible(False)  # ✅ Standardmäßig versteckt

        # **✅ Falls `dragDropArea` noch nicht existiert → Jetzt erstellen**
        if self.dragDropArea is None:
            print("🛠 Erstelle Drag-and-Drop-Bereich beim Start...")
            self.dragDropArea = DragDropArea(self)
            self.dragDropArea.setFixedSize(350, 200)
            self.dragDropArea.setVisible(True)  # Standardmäßig sichtbar

        # **Beim Start gespeicherte Daten laden**
        df = self.load_data()
        if df is not None and not df.empty:
            print("📂 Gespeicherte Daten werden in der Tabelle angezeigt.")

            # **Tabelle nur erstellen, falls sie nicht existiert**
            if self.tableWidget is None:
                self.create_table_widget()

            # **Daten in die Tabelle laden (mit ImportCSV-Instanz)**
            importer = ImportCSV(self)  # ✅ Instanz von ImportCSV erstellen
            importer.show_data_preview(df, self.tableWidget)  # ✅ Funktion richtig aufrufen
            self.format_table_widget(self.tableWidget)
            self.adjust_table_rows(self.tableWidget)

            # **Drag-and-Drop-Fläche nur ausblenden, wenn Daten existieren**
            if self.dragDropArea is not None:
                self.dragDropArea.setVisible(False)
                
    # Funktion zum Laden der benutzerverwaltung.json
    def load_user_permissions(self):
        """Lädt die Benutzerrechte aus einer JSON-Datei oder setzt Standardwerte."""
        try:
            # Öffnet die JSON-Datei mit den Benutzerrechten
            with open("users/benutzerverwaltung.json", "r") as file:
                permissions = json.load(file)
            # Gibt die Berechtigungen für die aktuelle Benutzerrolle zurück
            return permissions.get(self.user_role, ["Dashboard", "Vergleich", "Import", "Export", "Einstellungen", "Themes", "Benutzerverwaltung"])
        except FileNotFoundError:
            # Gibt Warunung zurück fall die Datei fehlt
            print("⚠️  'benutzerverwaltung.json' nicht gefunden! Standardrechte werden gesetzt.")
            return ["Dashboard", "Vergleich", "Import", "Export", "Einstellungen", "Themes", "Benutzerverwaltung"]

    # Funktion zum Erstellen und anpassen der Menübar 
    def create_menu_bar(self):
        """Erstellt die Menüleiste mit Flyout-Menüs"""
        
        # Erstellen der Menübar
        menu_bar = self.menuBar()

        # Menüpunkt Dashboard 
        if "Dashboard" in self.permissions:
            dashboard_menu = menu_bar.addMenu("🏠 Dashboard")
            dashboard_action = QAction("Dashboard anzeigen", self)
            dashboard_action.triggered.connect(lambda: self.update_content("Dashboard"))
            dashboard_action.setShortcut(QKeySequence("Ctrl+D")) # Tastenkürzel
            dashboard_menu.addAction(dashboard_action)
            
            # Direkter Aufruf
            dashboard_menu.triggered.connect(lambda: self.update_content("Dashboard"))  # Direktzugriff

        # Menüpunkt Analysen mit Kategorien und den jeweiligen Inhalten
        if "Analysen" in self.permissions:
            analysen_menu = menu_bar.addMenu("📊 Analysen")
            for category, analyses in self.analysen_categories.items():
                category_menu = analysen_menu.addMenu(category) # Kategorie als Untermenü
                for analysis in analyses:
                    action = QAction(analysis, self)
                    action.triggered.connect(lambda _, a=analysis: self.update_content(a))
                    category_menu.addAction(action) # Analyse zur Kategorie hinzufügen

        # Menüpunkt Vergleich
        if "Vergleich" in self.permissions:
            vergleich_menu = menu_bar.addMenu("📈 Vergleich")
            vergleich_action = QAction("Vergleich starten", self)
            vergleich_action.triggered.connect(lambda: self.update_content("Vergleich"))
            vergleich_action.setShortcut(QKeySequence("Ctrl+V")) # Tastenkürzel
            vergleich_menu.addAction(vergleich_action)
            
            # Direkter Aufruf
            vergleich_menu.triggered.connect(lambda: self.update_content("Vergleich"))

        # Menüpunkt Import
        if "Import" in self.permissions:
            import_menu = menu_bar.addMenu("📥 Import")
            import_action = QAction("Datei importieren", self)
            import_action.triggered.connect(lambda: self.update_content("Import"))
            import_action.setShortcut(QKeySequence("Ctrl+I")) # Tastenkürzel
            import_menu.addAction(import_action)
            
            load_last_data_action = QAction("Letzte Daten laden", self)
            load_last_data_action = QAction("Letzte Daten laden", self)
            load_last_data_action.triggered.connect(self.load_last_saved_data)
            import_menu.addAction(load_last_data_action)
            
            clear_data_action = QAction("Daten löschen", self)
            clear_data_action.triggered.connect(self.clear_data)
            import_menu.addAction(clear_data_action)

        # Menüpunkt Export
        if "Export" in self.permissions:
            export_menu = menu_bar.addMenu("📤 Export")
            export_action = QAction("Datei exportieren", self)
            export_action.triggered.connect(lambda: self.update_content("Export"))
            export_action.setShortcut(QKeySequence("Ctrl+E")) # Tastenkürzel
            export_menu.addAction(export_action)

        # Menüpunkt Einstellungen
        if "Einstellungen" in self.permissions:
            einstellungen_menu = menu_bar.addMenu("⚙️ Einstellungen")
            einstellungen_action = QAction("Einstellungen öffnen", self)
            einstellungen_action.triggered.connect(lambda: self.update_content("Einstellungen"))
            einstellungen_action.setShortcut(QKeySequence("Ctrl+S")) # Tastenkürzel
            einstellungen_menu.addAction(einstellungen_action)

            # Menüpunkt Benutzerverwaltung
            if "Benutzerverwaltung" in self.permissions:
                user_management_action = QAction("Benutzerverwaltung", self)
                user_management_action.triggered.connect(self.open_user_management)
                einstellungen_menu.addAction(user_management_action)

        # Menüpunkt Themes 
        themes_menu = self.menuBar().addMenu("🎨 Themes")
        theme_names = ["Luxuriös & Innovativ", "Serious Business-Mode", "Cyber Tech-Mode"]
        for theme in theme_names:
            theme_action = QAction(theme, self)
            theme_action.triggered.connect(lambda _, t=theme: self.change_theme(t))
            themes_menu.addAction(theme_action)

    # Funktionn zum Hinzufügen der Suchleiste 
    def add_search_bar(self):
        """Fügt eine Suchleiste mit Autovervollständigung zur Menüleiste hinzu."""
        search_menu = self.menuBar().addMenu("🔍 Suche")

        available_pages = ["Dashboard", "Vergleich", "Import", "Export", "Einstellungen"] + \
                        [analysis for sublist in self.analysen_categories.values() for analysis in sublist]

        self.search_bar = QLineEdit(self)
        self.search_bar.setPlaceholderText("🔍 Seiten durchsuchen...")
        completer = QCompleter(available_pages, self)
        completer.setCaseSensitivity(QtCore.Qt.CaseSensitivity.CaseInsensitive)
        self.search_bar.setCompleter(completer)
        self.search_bar.returnPressed.connect(self.search_navigation)

        search_action = QWidgetAction(self)
        search_action.setDefaultWidget(self.search_bar)
        search_menu.addAction(search_action)

    # Funktion für Schnellnavigation der Suchleiste
    def search_navigation(self):
        """Durchsucht die Seiten und navigiert."""
        # Holt den aktuellen Text aus der Suchleiste
        search_text = self.search_bar.text()
        
        # Liste aller verfügbaren Seiten
        available_pages = ["Dashboard", "Vergleich", "Import", "Export", "Einstellungen"] + \
                        [analysis for sublist in self.analysen_categories.values() for analysis in sublist]

        # Überprüfen, ob die eingegebene Seite existier
        if search_text in available_pages:
            # Falls die Seite existiert, wird inhalt aktualisiert
            self.update_content(search_text)
        else:
            # Falls die Seite nicht gefunden, wird eine Fehlermeldung ausgegeben
            self.show_error_message(f"Seite '{search_text}' nicht gefunden.")

    # Funktion zum Öffnen der Benutzerverwaltung
    def open_user_management(self):
        """Öffnet das Benutzerverwaltungs-Fenster (nur für Admins sichtbar)."""
        # Überprüfen ob der aktuelle Benutzer die Berechtigung zur Benutzerverwaltung hat
        if "Benutzerverwaltung" in self.permissions:
            # Erstelle ein neues Fenster für die Benutzerverwaltung
            dialog = UserManagementDialog(self)
            dialog.exec()
        else:
            # Falls der Benutzer keine Admin-Rechte hat, Fehlermeldung anzeigen
            self.show_error_message("Zugriff verweigert! Nur Admins dürfen Benutzer verwalten.")
 
    # Funktion zum Aktualisieren der Statusbar
    def update_status_bar(self, message):
        """Aktualisiert die Statusbar mit der gegebenen Nachricht."""
        # Zeigt übergebene Nachricht in der Statusbar an
        self.statusBar().showMessage(message, 10000)

    # Funktion zum Anzeigen einer Fehlermeldung in der Statusbar 
    def show_error_message(self, error_message):
        """Zeigt eine Fehlermeldung in der Statusleiste und als Popup an."""
        
        # Zeigt die Fehlermeldung in der Statusleiste
        self.update_status_bar(error_message)
        
        # Erstellt und setzt style für Fehlermeldung
        error_dialog = QMessageBox(self)
        error_dialog.setIcon(QMessageBox.Icon.Critical)
        error_dialog.setWindowTitle("Fehler")
        error_dialog.setText(error_message)
        error_dialog.exec()
     
    # Funktion zum Laden der styles.qss    
    def load_styles(self):
        """Lädt die QSS-Stylesheet Datei."""
        try:
            # Öffnet die Datei und liest den Inhalt
            with open("styles.qss", "r") as file:
                self.setStyleSheet(file.read())
        except FileNotFoundError:
            # Falls die Datei fehlt, wird eine Warnung ausgegeben
            print("⚠️  Stylesheet 'styles.qss' nicht gefunden!")
             
    # Funktion zum Aktualisieren des Main Contents         
    def update_content(self, content):
        """Aktualisiert den Seiteninhalt dynamisch."""
        self.current_page = content
        self.ui.mainContentLabel.setText(f"⏳ Lade {content}...")

        # **Verstecke die Tabelle & Drag-and-Drop, wenn nicht auf der Import-Seite**
        if content != "Import":
            if self.tableWidget is not None:
                self.tableWidget.setVisible(False)
                self.tableWidget.setParent(None)  # ✅ Entfernt die Tabelle aus dem Layout
            if self.dragDropArea is not None:
                self.dragDropArea.setVisible(False)
                self.dragDropArea.setParent(None)  # ✅ Entfernt Drag-and-Drop aus dem Layout

        # Entferne vorherige Widgets aus mainContentFrame, aber NICHT `dragDropArea` und `tableWidget`
        for i in reversed(range(self.ui.gridLayout.count())):
            widget = self.ui.gridLayout.itemAt(i).widget()
            if widget and widget not in [self.dragDropArea, self.tableWidget]:
                widget.hide()

        # **Seite: Import**
        if content == "Import":
            self.ui.mainContentLabel.setText("📥 Datei importieren")

            # **Import-Seite erstellen**
            self.importPage = QtWidgets.QWidget(self.ui.mainContentFrame)
            import_layout = QtWidgets.QVBoxLayout(self.importPage)

            # **Falls `dragDropArea` gelöscht wurde, neu erstellen**
            if self.dragDropArea is None or not isinstance(self.dragDropArea, DragDropArea):
                self.dragDropArea = DragDropArea(self)
                self.dragDropArea.setFixedSize(350, 200)

            self.dragDropArea.setParent(self.importPage)
            self.dragDropArea.setVisible(True)

            # **Falls `tableWidget` gelöscht wurde, neu erstellen**
            if self.tableWidget is None:
                self.create_table_widget()
            else:
                self.tableWidget.setParent(self.importPage)
                self.tableWidget.setVisible(True)

            # **Falls keine Daten existieren → Drag-and-Drop anzeigen, Tabelle verstecken**
            if self.current_df is None:
                self.dragDropArea.setVisible(True)
                self.tableWidget.setVisible(False)
            else:
                if content == "Import":
                    self.update_table(self.current_df,)  # ✅ Zeigt die Daten in der Tabelle nur auf der Import-Seite
                    importer = ImportCSV(self)
                    importer.show_data_preview(self.current_df, self.tableWidget)
                    self.dragDropArea.setVisible(False)

            # **Größe und Layout der Tabelle optimieren**
            self.format_table_widget(self.tableWidget)

            # **Layout setzen (Drag-and-Drop oben, Tabelle unten)**
            import_layout.addWidget(self.dragDropArea, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
            import_layout.addWidget(self.tableWidget, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)

            self.importPage.setLayout(import_layout)
            self.ui.gridLayout.addWidget(self.importPage, 0, 0, 1, 1)
            self.resize_floating_button()
            self.ui.mainContentFrame.updateGeometry()

            self.update_status_bar("📥 Import-Seite geladen. Bitte Datei auswählen.")
            
        elif content in ["Segment-Analyse", "Bestandskundenanalyse", "Neukundenanalyse", "Kohortenanalyse"
                         "RFM-Analyse", "Kaufzyklusanalyse", "Durchschnittlicher Bestellwert (AOV)"
                         "Churn-Analyse", "Survival-Analyse", "Inaktivitätsanalyse"
                         "Umsatzprognose", "Absatzprognose", "Benchmark-Analyse"
                         "Customer Lifetime Value (CLV)", "Wiederkaufsrate"]:
            self.ui.mainContentLabel.setText(f"📊 {content}")
            self.update_analysis()  # **Analysen laden!**
            

        # **Alle anderen Seiten**
        else:
            self.ui.mainContentLabel.setText(f"🏠 {content}")
            self.statusBar().showMessage(f"Seite '{content}' geladen", 5000)

            placeholder = QtWidgets.QLabel(f"Inhalt für {content}", self.ui.mainContentFrame)
            placeholder.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            self.ui.gridLayout.addWidget(placeholder, 0, 0, 1, 1)
                
    # Funktion zum Aufrufen der Drag und Drop-Funktionen    
    def import_csv(self, file_path):
        """Importiert Daten und aktualisiert die Tabelle."""
        try:
            import_handler = ImportCSV(self)
            import_handler.import_from_file(file_path)

            # Tabelle nach dem Import sichtbar machen
            self.tableWidget.setVisible(True)

            # Drag-and-Drop-Bereich ausblenden
            self.dragDropArea.setVisible(False)

            # Statusbar-Update
            self.statusBar().showMessage(f"📂 Datei erfolgreich importiert: {file_path}")

        except Exception as e:
            print(f"⚠️ Fehler beim Import: {e}")
            
    # Funktion für animierte Einblendung des Navigationsprüflabels 
    def animate_page_transition(self, content):
        """Führt eine sanfte Seitenwechsel-Animation aus."""
        animation = QPropertyAnimation(self.ui.mainContentLabel, b"windowOpacity")
        animation.setDuration(250)
        animation.setStartValue(0)
        animation.setEndValue(1)
        animation.start()
        self.ui.mainContentLabel.setText(content)
      
    # Funktion zum Wechseln der Themes   
    def change_theme(self, theme):
        """Wechselt das Theme zur Laufzeit & passt Farben von MainWindow, MainFrame, Statusbar & Labels an."""
        
        # Deniert verschiedene Themes 
        theme_styles = {
            "Luxuriös & Innovativ": """
                QMainWindow { background: #242424; }  /* Dunkler als MainFrame */
                #mainContentFrame, QStatusBar {
                    background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #1E1E1E, stop:1 #292929);
                }
                QLabel {
                    color: white; /* Schriftfarbe für Labels */
                }
            """,
            "Serious Business-Mode": """
                QMainWindow { background: #DADADA; } /* Hintergrund leicht dunkler */
                #mainContentFrame, QStatusBar {
                    background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, 
                        stop:0 #DDDDDD, stop:1 #9A9A9A);
                }
                QLabel {
                    color: black; /* Schriftfarbe für Labels */
                }
            """,
            "Cyber Tech-Mode": """
                QMainWindow { background: #080808; } /* Fast Schwarz */
                #mainContentFrame, QStatusBar {
                    background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #0F0F0F, stop:1 #1C1C1C);
                }
                QLabel {
                    color: #18FFFF; /* Neon-blau für Labels */
                }
            """
        }

        # Laden der styles.qss, um Standard-Styles beizubehalten
        with open("styles.qss", "r") as file:
            base_styles = file.read()

        # Kombiniert styles.qss mit dem Theme-Design
        final_styles = f"{base_styles}\n{theme_styles.get(theme, '')}"

        # Setze das neue Stylesheet
        self.setStyleSheet(final_styles)

        # Sanfter Übergang des Theme-Wechsels
        animation = QPropertyAnimation(self.ui.mainContentFrame, b"windowOpacity")
        animation.setDuration(400)
        animation.setStartValue(0)
        animation.setEndValue(1)
        animation.start()

        # Statusbar-Update zur Bestätigung des Theme-Wechsels
        self.update_status_bar(f"Theme geändert: {theme}")
    
    # Funktion zum Hinzufügen und Anpassen des Floating-Knopfes    
    def add_floating_button(self):
        """Erstellt einen Floating Action Button (FAB) mit sanftem Einblenden."""
        
        # Erstellt den Floating-Button im mainContentFrame
        self.floating_button = QPushButton("➕", self.ui.mainContentFrame)
        self.floating_button.setObjectName("floatingButton")
        self.floating_button.setFixedSize(50, 50)
        
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

        # Verknüpft das Resize-Event des Frames mit der Positionierung des Button
        self.ui.mainContentFrame.resizeEvent = self.resize_floating_button
        self.resize_floating_button()

        # Klick-Ereignis für den Button (aktuell nur eine Platzhaltermeldung)
        self.floating_button.clicked.connect(lambda: self.show_error_message("Noch keine Funktion!"))

        # Sanfte Einblendung des Floating-Buttons
        self.floating_button.setGraphicsEffect(None)
        animation = QPropertyAnimation(self.floating_button, b"windowOpacity")
        animation.setDuration(400)
        animation.setStartValue(0)
        animation.setEndValue(1)
        animation.start()

        self.floating_button.show()

    # Funktion zur Aktualisierung der Positionierunf des Floating-Buttons
    def resize_floating_button(self, event=None):
        """Aktualisiert die Position des Floating Buttons, wenn das Fenster skaliert wird."""
        
        # Platziert den Button immer in der unteren rechten Ecke des `mainContentFrame`
        self.floating_button.move(self.ui.mainContentFrame.width() - 70, self.ui.mainContentFrame.height() - 70)

    # Daten Speichern
    def load_data(self):
        """Lädt gespeicherte Daten aus der Datei, falls vorhanden."""
        try:
            if os.path.exists("saved_data.pkl"):
                with open("saved_data.pkl", "rb") as f:
                    df = pickle.load(f)
                self.current_df = df
                return df
            return None
        except Exception as e:
            print(f"Fehler beim Laden der Daten: {e}")
            return None
        
    def load_last_saved_data(self, content):
        """Lädt gespeicherte Daten und integriert sie nur in der Import-Tabelle."""
        df = self.load_data()  

        if df is None:
            QMessageBox.warning(self, "Keine gespeicherten Daten", "Es wurden keine gespeicherten Daten gefunden.")
            return

        print("📂 Gespeicherte Daten werden in der Tabelle angezeigt.")

        # Speichert die geladenen Daten temporär
        self.current_df = df  

        # **Sicherstellen, dass das TableWidget existiert**
        if self.tableWidget is None:
            self.create_table_widget()

        # **Nur wenn die Import-Seite aktiv ist, die Tabelle aktualisieren!**
        if content == "Import":
            self.update_table(df)  
            self.format_table_widget(self.tableWidget)  
            self.adjust_table_rows(self.tableWidget)

            # **Drag-and-Drop-Bereich ausblenden, falls Daten vorhanden sind**
            if hasattr(self, 'dragDropArea') and df is not None and not df.empty:
                self.dragDropArea.setVisible(False)
                self.tableWidget.setVisible(True)  

            self.resize_floating_button()
            self.ui.mainContentFrame.updateGeometry()
                    
            self.update_status_bar("✅ Letzte gespeicherte Daten erfolgreich geladen!")

            # **Nach erfolgreichem Laden Analysen starten**
            self.process_loaded_data(df)

        else:
            print("🔄 Daten geladen, aber nicht angezeigt, weil die Import-Seite nicht aktiv ist.")
            
    
        # Funktion zum automatischen Starten aller Analysen nach dem Laden der Daten
    def process_loaded_data(self, df):
        """Startet automatisch die relevanten Analysen."""
        print("🚀 Starte automatische Analysen...")
        self.update_analysis()      
            
            
    def create_table_widget(self):
        """Erstellt das TableWidget, falls es nicht existiert."""
        if self.tableWidget is None:
            print("🛠 Erstelle `tableWidget`...")
            self.tableWidget = QtWidgets.QTableWidget(self.ui.mainContentFrame)
            self.tableWidget.setObjectName("tableWidget")
            
            # **Größe & Layout-Einstellungen**
            self.tableWidget.setSizePolicy(
                QtWidgets.QSizePolicy.Policy.Expanding,
                QtWidgets.QSizePolicy.Policy.Expanding
            )

            # **Header-Einstellungen**
            self.tableWidget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
            self.tableWidget.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.ResizeToContents)

            # **Tabelle dem Layout hinzufügen**
            self.ui.gridLayout.addWidget(self.tableWidget, 0, 0, 1, 1)

            # **Standardmäßig unsichtbar machen**
            self.tableWidget.setVisible(False)
            
            self.format_table_widget(self.tableWidget)
            self.adjust_table_rows(self.tableWidget)

            print("✅ `tableWidget` wurde erfolgreich erstellt!")
        
    def format_table_widget(self, tableWidget):
        """Sorgt dafür, dass die Tabelle das gleiche Format hat wie beim normalen Import."""
        if tableWidget is None:
            return

        # Header sichtbar machen
        tableWidget.horizontalHeader().setVisible(True)
        tableWidget.verticalHeader().setVisible(True)
        
        # **Header-Höhe explizit setzen**
        tableWidget.horizontalHeader().setFixedHeight(60)

        # Spalten- und Zeilenkonfiguration
        tableWidget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        tableWidget.horizontalHeader().setStretchLastSection(True)
        tableWidget.horizontalHeader().setMinimumSectionSize(120)
        tableWidget.verticalHeader().setFixedWidth(45)  # Breite der vertikalen Header

        # Zeilenhöhe anpassen
        total_height = tableWidget.viewport().height()
        row_count = max(1, tableWidget.rowCount())  # Stelle sicher, dass mindestens 1 Zeile existiert
        row_height = total_height // row_count
        for row in range(10):
            tableWidget.setRowHeight(row, row_height)

        # Automatische Spaltenbreite
        tableWidget.resizeColumnsToContents()
        self.ui.mainContentFrame.updateGeometry()
        self.ui.gridLayout.invalidate()
        
    def update_table(self, data):
        """ Aktualisiert die Tabelle mit neuen Daten """
        if data is None or data.empty:
            self.tableWidget.clear()
            self.tableWidget.setRowCount(0)
            self.tableWidget.setColumnCount(0)
            return

        # Tabelle initialisieren
        self.tableWidget.setRowCount(min(10, len(data)))  # Max. 10 Zeilen
        self.tableWidget.setColumnCount(len(data.columns))
        self.tableWidget.setHorizontalHeaderLabels(data.columns)
        
        # **Header-Höhe explizit setzen**
        self.tableWidget.horizontalHeader().setFixedHeight(60)

        # Daten in die Tabelle einfügen
        for row in range(min(10, len(data))):
            for col in range(len(data.columns)):
                item = QTableWidgetItem(str(data.iloc[row, col]))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.tableWidget.setItem(row, col, item)

        # Style und Layout aktualisieren
        self.format_table_widget(self.tableWidget)
        self.adjust_table_rows(self.tableWidget)
        self.resize_floating_button()
        self.ui.mainContentFrame.updateGeometry()
        
    def adjust_table_rows(self, tableWidget):
        """Passt die Zeilenhöhe so an, dass sie den gesamten Tabellenbereich ausfüllen."""
        if tableWidget.rowCount() > 0:
            # Nutze die Viewport-Höhe für eine exakte Berechnung
            total_height = tableWidget.viewport().height()
            row_height = total_height // tableWidget.rowCount()

            # Setze die Höhe jeder Zeile
            for row in range(tableWidget.rowCount()):
                tableWidget.setRowHeight(row, row_height)

            print(f"✅ Zeilenhöhe angepasst: {row_height}px pro Zeile")
        
    def clear_data(self):
        """Löscht aktuelle Daten, Tabellen & gespeicherte Analysen."""
        confirmation = QMessageBox.question(
            self, "Daten löschen", "Möchtest du wirklich ALLE Daten & Analysen löschen?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirmation == QMessageBox.StandardButton.No:
            return

        # 🔹 1️⃣ Daten im Programm zurücksetzen
        self.current_df = None

        # 🔹 2️⃣ Tabelle leeren und verstecken
        if self.tableWidget:
            self.tableWidget.clear()
            self.tableWidget.setRowCount(0)
            self.tableWidget.setColumnCount(0)
            self.tableWidget.setVisible(False)

        # 🔹 3️⃣ Drag-and-Drop anzeigen
        if self.dragDropArea:
            self.dragDropArea.setVisible(True)

        # 🔹 4️⃣ Gespeicherte Daten-Datei löschen
        if os.path.exists("saved_data.pkl"):
            os.remove("saved_data.pkl")
            print("🗑 Gespeicherte Datei gelöscht.")

        # 🔹 5️⃣ Analyse-Ordner löschen
        analysis_results_path = "/Users/marcus/Documents/GitHub/Abschlussprojekt/main_project/PyQt6/analysis/analysis_results"
        if analysis_results_path.exists():
            for file in analysis_results_path.glob("*.html"):  # Löscht alle gespeicherten Diagramme
                file.unlink()
            print("🗑 Alle gespeicherten Analysen wurden gelöscht.")

        # 🔹 6️⃣ Status-Update
        self.update_status_bar("❌ Alle Daten & Analysen wurden gelöscht!")
        
    def resizeEvent(self, event):
        """Reagiert auf Änderungen der Fenstergröße."""
        super().resizeEvent(event)
        if self.tableWidget and self.current_page == "Import":
            self.adjust_table_rows(self.tableWidget)
        self.ui.mainContentFrame.updateGeometry()#
        
    def update_analysis(self):
        """Lädt die Analyse, falls sie existiert. Falls nicht, wird sie neu generiert."""
        if self.current_df is None:
            print("⚠️ Keine Daten geladen – Analysen werden nicht gestartet.")
            return
        
        selected_analysis = self.analysis_layout.chart_selector.currentText()
        print(f"📊 Debug: Ausgewählte Analyse = '{selected_analysis}'")  # DEBUG

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

        if selected_analysis not in analysis_mapping:
            print(f"❌ Fehler: '{selected_analysis}' ist keine gültige Analyse!")
            print(f"📜 Verfügbare Optionen: {list(analysis_mapping.keys())}")
            return

        # 🔹 Überprüfe, ob die Analyse bereits existiert
        analysis_results = analysis_mapping[selected_analysis]()
        first_html_path = list(analysis_results.values())[0]  # Nimmt die erste Datei

        if os.path.exists(first_html_path):
            print(f"✅ Analyse existiert bereits: {first_html_path}")
            self.analysis_layout.chart_view.setUrl(QUrl.fromLocalFile(os.path.abspath(first_html_path)))
        else:
            print(f"❌ Fehler: HTML-Datei nicht gefunden – {first_html_path}")

if __name__ == "__main__":
    
    # Erstellt die QApplication-Instanz (Hauptanwendung)
    app = QApplication(sys.argv)
    
    # Erstellt das Hauptfenster der Anwendung
    window = MainApp()
    window.show() # Zeigt die Anwendung
    
    # Beendet das Programm, wenn Hauptfenster geschlossen wird
    sys.exit(app.exec())
