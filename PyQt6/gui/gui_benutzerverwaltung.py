# Standard Libaries
import os
import json

# PyQt6 Imports
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QPushButton, 
    QLabel,
    QComboBox,
    QListWidget,
    QLineEdit
)

# Pfad zur Benutzerverwaltungsdatei
USER_MANAGEMENT_FILE = os.path.join(os.path.dirname(__file__), "users", "benutzerverwaltung.json")

class UserManagementDialog(QDialog):
    """Fenster zur Verwaltung von Benutzerrechten."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Benutzerverwaltung")
        self.setGeometry(400, 200, 400, 300)
        
        # Theme laden
        try:
            with open("styles.qss", "r", encoding="utf-8") as file:
                self.setStyleSheet(file.read())
        except FileNotFoundError:
            print("⚠️ Stylesheet 'styles.qss' nicht gefunden! Standard-Design wird verwendet.")

        # Layout erstellen
        layout = QVBoxLayout()

        # Benutzerliste
        self.user_list = QListWidget()
        layout.addWidget(QLabel("Benutzer auswählen:"))
        layout.addWidget(self.user_list)

        # Rollen-Auswahl
        self.role_selector = QComboBox()
        self.role_selector.addItems(["admin", "user"])  
        layout.addWidget(QLabel("Rolle zuweisen:"))
        layout.addWidget(self.role_selector)

        # Speichern-Button
        self.save_button = QPushButton("Änderungen speichern")
        self.save_button.clicked.connect(self.save_permissions)
        layout.addWidget(self.save_button)

        # Neuen Benutzer hinzufügen
        self.new_user_input = QLineEdit()
        self.new_user_input.setPlaceholderText("Neuen Benutzer hinzufügen...")
        self.add_user_button = QPushButton("Benutzer hinzufügen")
        self.add_user_button.clicked.connect(self.add_user)
        layout.addWidget(self.new_user_input)
        layout.addWidget(self.add_user_button)

        # Layout setzen
        self.setLayout(layout)

        # Benutzerrechte laden
        self.load_permissions()

        # Theme aus der Hauptanwendung übernehmen
        if parent:
            self.setStyleSheet(parent.styleSheet())

    def load_permissions(self):
        """Lädt die Benutzerrechte aus `benutzerverwaltung.json` und füllt die Liste."""
        if not os.path.exists(USER_MANAGEMENT_FILE):
            print(f"⚠️ Benutzerverwaltung nicht gefunden: {USER_MANAGEMENT_FILE}")
            self.permissions = {"admin": ["Dashboard", "Analysen", "Vergleich", "Import", "Export", "Einstellungen", "Themes", "Benutzerverwaltung"], "user": ["Dashboard", "Vergleich"]}
            with open(USER_MANAGEMENT_FILE, "w") as file:
                json.dump(self.permissions, file, indent=4)
        else:
            try:
                with open(USER_MANAGEMENT_FILE, "r") as file:
                    self.permissions = json.load(file)
            except json.JSONDecodeError:
                print("⚠️ Fehler beim Laden von `benutzerverwaltung.json`! Datei könnte beschädigt sein.")
                self.permissions = {"admin": ["Dashboard", "Analysen", "Vergleich", "Import", "Export", "Einstellungen", "Themes", "Benutzerverwaltung"], "user": ["Dashboard", "Vergleich"]}

        # Benutzerliste füllen
        self.user_list.clear()
        self.user_list.addItems(self.permissions.keys())

    def save_permissions(self):
        """Speichert die geänderten Benutzerrechte in `benutzerverwaltung.json`."""
        selected_user = self.user_list.currentItem()
        if selected_user:
            username = selected_user.text()
            new_role = self.role_selector.currentText()
            
            # Korrekte Speicherung der Berechtigungen
            self.permissions[username] = self.permissions[new_role]  

            # Speichern in JSON
            with open(USER_MANAGEMENT_FILE, "w") as file:
                json.dump(self.permissions, file, indent=4)
            
            self.close()

    def add_user(self):
        """Fügt einen neuen Benutzer zur Liste hinzu."""
        new_user = self.new_user_input.text().strip()
        if new_user and new_user not in self.permissions:
            self.permissions[new_user] = self.permissions["user"]  # ✅ Standardrechte für neue Nutzer
            self.user_list.addItem(new_user)
            self.new_user_input.clear()

            # Speichern nach Hinzufügen eines neuen Benutzers
            with open(USER_MANAGEMENT_FILE, "w") as file:
                json.dump(self.permissions, file, indent=4)
