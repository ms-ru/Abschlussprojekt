# PyQt6 Imports
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QLabel, QFileDialog, QMessageBox
from PyQt6 import QtCore

class DragDropArea(QLabel):
    """QLabel-Klasse für Drag and Drop"""

    def __init__(self, main_app):
        super().__init__(main_app)
        self.main_app = main_app  # Verbindung zum Hauptfenster

        # Textausrichtung zentriert
        self.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        # Setzt Standardtext im Label
        self.setText("📂 Ziehe eine Datei hierher oder klicke, um eine auszuwählen")

        # Setzt Styling
        self.setStyleSheet("""
            QLabel {
                background: rgba(103, 58, 183, 0.23); 
                color: white;
                font-size: 16px;
                border-radius: 12px; 
                border: 2px dashed rgba(255, 255, 255, 0.6);
                padding: 20px;
            }               
        """)
        self.setAcceptDrops(True)  # Drag and Drop aktivieren

    def dragEnterEvent(self, event):
        """Wird ausgelöst, wenn eine Datei über das Widget gezogen wird."""
        print("🔍 dragEnterEvent() wurde aufgerufen!")  # Debugging

        if event.mimeData().hasUrls():
            print("✅ Datei erkannt!")  # Debugging
            event.acceptProposedAction()

    def dropEvent(self, event):
        """Wird ausgelöst, wenn eine Datei auf das Widget fallen gelassen wird."""
        print("🔍 dropEvent() wurde aufgerufen!")  # Debugging

        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            print(f"📂 Datei gezogen: {file_path}")  # Debugging

            main_app = self.main_app  # Verbindung zur Hauptanwendung (MainApp)

            # **Richtiger Zugriff auf `import_csv`!**
            if hasattr(main_app, "import_csv") and hasattr(main_app.import_csv, "import_from_file"):
                print("✅ `import_from_file()` wird aufgerufen mit Datei:", file_path)
                main_app.import_csv.import_from_file(file_path)  # **Hier richtige Instanz verwenden!**
            else:
                QMessageBox.critical(self, "Fehler", "❌ `import_from_file()` existiert nicht in `ImportCSV`!")

    def mousePressEvent(self, event): 
        """Öffnet einen Datei-Dialog zur manuellen Dateiauswahl."""
        print("🔍 mousePressEvent() wurde aufgerufen!")  # Debugging

        file_path, _ = QFileDialog.getOpenFileName(
            self, "Datei auswählen", "", "CSV-Dateien (*.csv);;Excel-Dateien (*.xls *.xlsx)"
        )

        if not file_path:
            QMessageBox.warning(self, "Keine Datei ausgewählt", "⚠️ Bitte wähle eine Datei aus.")
            return

        print(f"📂 Datei über Dialog ausgewählt: {file_path}")  # Debugging

        main_app = self.main_app  # Direkter Zugriff auf "MainApp"

        # Falls "import_handler" existiert, rufe "import_from_file()" auf
        if hasattr(main_app, "import_handler") and hasattr(main_app.import_handler, "import_from_file"):
            print("✅ import_from_file() wird aufgerufen...")
            main_app.import_handler.import_from_file(file_path)
        else:
            QMessageBox.critical(self, "Fehler", "❌ `import_from_file()` existiert nicht in `ImportCSV`!")
