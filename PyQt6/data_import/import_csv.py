# Standard libaries
import pandas as pd
import pickle

#PyQt6 imports
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QTableWidgetItem, QMessageBox
from PyQt6.QtCore import Qt

DATA_FILE = "saved_data.pkl"

class ImportCSV:
    def __init__(self, main_app):
        """Initialisiert die Import-Klasse mit Zugriff auf das Hauptfenster."""
        self.main_app = main_app  # Hauptfenster (MainApp) speichern

    def import_from_file(self, file_path):
        """Diese Funktion lädt CSV/XLSX-Dateien und zeigt sie in der Tabelle an."""
        print(f"📂 import_from_file() aufgerufen mit Datei: {file_path}")  # Debugging

        try:
            if not file_path:
                print("⚠️ Keine Datei ausgewählt!")
                return

            # Datei einlesen
            if file_path.endswith(".csv"):
                df = pd.read_csv(file_path)
            elif file_path.endswith((".xls", ".xlsx")):
                df = pd.read_excel(file_path)
            else:
                print("⚠️ Fehler: Ungültiges Dateiformat!")
                return

            # Vorschau für Debugging
            print(f"📊 Typ von df: {type(df)}")
            if isinstance(df, pd.DataFrame):
                print(f"📊 Vorschau der ersten 3 Zeilen:\n{df.head()}")
            else:
                print("❌ Fehler: `df` ist kein DataFrame!")
                return

            # Überprüfung auf leere Daten
            if df is None or not isinstance(df, pd.DataFrame) or df.shape[0] == 0:
                QMessageBox.warning(None, "Warnung", "Die Datei enthält keine Daten!")
                return
            
            if self.main_app.current_df is not None and not self.main_app.current_df.empty:
                print("Datei wurde erfolgreich importiert – Starte Analysen automatisch...")
            self.main_app.process_loaded_data(self.main_app.current_df)  

            print("✅ Datei wurde erfolgreich eingelesen!")  # Test
            
            self.save_data(df)  # Speichert die Daten nach dem Import
            self.current_df = df

            # Begrenzung auf die ersten 10 Zeilen
            df = df.head(10)

            # Hauptfenster holen
            main_window = self.main_app
            if not isinstance(main_window, QtWidgets.QMainWindow):  
                print(f"❌ Fehler: `main_window` ist kein `QMainWindow`, sondern {type(main_window)}")
                return

            # `tableWidget` finden
            tableWidget = main_window.findChild(QtWidgets.QTableWidget, "tableWidget")
            if tableWidget is None:
                print("❌ `tableWidget` nicht gefunden!")
                return

            # Tabelle vorbereiten
            tableWidget.clear()
            tableWidget.setRowCount(len(df))
            tableWidget.setColumnCount(len(df.columns))
            tableWidget.setHorizontalHeaderLabels(df.columns.tolist())

            # Daten in die Tabelle einfügen
            for row in range(len(df)):
                for col in range(len(df.columns)):
                    item = QTableWidgetItem(str(df.iat[row, col]))
                    tableWidget.setItem(row, col, item)

            # Spaltenbreite dynamisch anpassen
            tableWidget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)

            # Tabelle sichtbar machen
            tableWidget.setVisible(True)
            self.main_app.dragDropArea.setVisible(False)  # Drag-and-Drop-Bereich ausblenden

            # Layout "tableWidget"
            self.main_app.format_table_widget(self.main_app.tableWidget)
            self.main_app.adjust_table_rows(self.main_app.tableWidget)
            self.main_app.tableWidget.setVisible(True)
        
            # Statusbar aktualisieren
            self.main_app.statusBar().showMessage(f"📂 Datei erfolgreich importiert: {file_path}")

        except Exception as e:
            print(f"⚠️ Fehler beim Import: {e}")

    def show_data_preview(self, df, tableWidget):
        """Zeigt eine Vorschau der geladenen Daten in der Tabelle, aber nur auf der Import-Seite."""
        
        #Falls die aktuelle Seite nicht 'Import' ist, Tabelle verstecken und Funktion beenden
        if self.main_app.current_page != "Import":
            print("🔄 Tabelle wird NICHT geladen, weil die Import-Seite nicht aktiv ist.")
            tableWidget.setVisible(False)  # ✅ Tabelle verstecken
            return  

        if df is None or df.empty:
            QMessageBox.warning(None, "Warnung", "Die Datei enthält keine Daten!")
            tableWidget.setVisible(False)
            return

        print(f"📂 Zeige Datenvorschau: {len(df)} Zeilen, {len(df.columns)} Spalten")

        # Feste Größe von 1300x800 beibehalten
        tableWidget.setFixedSize(1300, 800)
        tableWidget.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)

        max_rows = 10
        max_cols = min(len(df.columns), 50)
        tableWidget.clear()
        tableWidget.setRowCount(max_rows)
        tableWidget.setColumnCount(max_cols)
        tableWidget.setHorizontalHeaderLabels(df.columns[:max_cols])

        for row in range(min(len(df), max_rows)):
            for col in range(max_cols):
                item = QTableWidgetItem(str(df.iat[row, col]))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                tableWidget.setItem(row, col, item)

        tableWidget.horizontalHeader().setVisible(True)
        tableWidget.verticalHeader().setVisible(True)
        tableWidget.horizontalHeader().setFixedHeight(60)

        self.main_app.format_table_widget(tableWidget)
        self.main_app.adjust_table_rows(tableWidget)

        # Tabelle jetzt sichtbar machen, weil Import-Seite aktiv ist
        tableWidget.setVisible(True)

        self.main_app.statusBar().showMessage(f"✅ Daten erfolgreich geladen: {len(df)} Zeilen, {len(df.columns)} Spalten")
    
    # Geladene Daten Speichern  
    def save_data(self, df):
        """Speichert die Daten in einer binären Datei, wenn sie gültig sind."""
        if df is None or df.empty:
            print("⚠️ Warnung: Es wurden keine Daten gespeichert, da der DataFrame leer ist.")
            return  # **Kein Speichern, wenn df leer ist!**

        try:
            with open(DATA_FILE, "wb") as f:  # **wb = Write Binary**
                pickle.dump(df, f)
            print(f"✅ Daten erfolgreich gespeichert in {DATA_FILE} (binär)")
        except Exception as e:
            print(f"⚠️ Fehler beim Speichern der Daten: {e}")