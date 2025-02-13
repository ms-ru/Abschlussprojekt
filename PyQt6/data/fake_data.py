from faker import Faker
import pandas as pd
import random

# Faker-Instanz erstellen
fake = Faker()

# Anzahl der zu generierenden Einträge
num_entries = 1000000

# Datenliste erstellen
data = []

# Aerosolequipment-Produkte und deren Preisgrenzen
products_with_prices = {
    "Partikelzähler": (8000, 40000),
    "Aerosolgenerator": (2000, 12000),
    "Filterprüfstand": (100000, 500000),
    "Verdünnungssystem": (2000, 12000),
    "Staubgenerator": (7000, 20000)
}

# Industrien / Kunden
industries = [
    "Universität", "Filterproduzent", "Handelsgesellschaft", 
    "Institut", "Pharmaunternehmen", "Forschungszentrum", "Laborausrüster"
]

# Datengenerierung
for _ in range(num_entries):
    # IDs generieren
    customer_id = fake.uuid4()[:8]  # Kürzere UUID für Kunden
    transaction_id = fake.uuid4()  # Volle UUID für Transaktionen

    # Zufällige Daten
    date = fake.date_between(start_date='-30y', end_date='today')  # Datum innerhalb der letzten 5 Jahre
    product = random.choice(list(products_with_prices.keys()))  # Produkt auswählen
    industry = random.choice(industries)  # Industrie auswählen
    price_range = products_with_prices[product]  # Preisbereich des Produkts abrufen
    cost = round(random.uniform(price_range[0], price_range[1]), 2)  # Kosten innerhalb des Bereichs
    revenue = round(cost * random.uniform(1.1, 2), 2)  # Umsatz basierend auf Gewinn
    discount = round(random.uniform(0, 25), 2)  # Rabatt in Prozent
    country = fake.country()  # Zufälliges Land
    purchase_channel = random.choice(["Online", "Direktvertrieb", "Messe"])  # Kaufkanal

    # Hinzufügen der generierten Daten zur Liste
    data.append([
        customer_id, transaction_id, date, product, industry, cost, revenue, discount, country, purchase_channel
    ])

# Spaltennamen
columns = [
    "Customer ID", "Transaction ID", "Date", "Product", "Industry", "Cost", "Revenue", "Discount", "Country", "Purchase Channel"
]

# DataFrame erstellen und als CSV speichern
df = pd.DataFrame(data, columns=columns)
df.to_csv("aerosol_equipment_sales_data.csv", index=False)

print("Fertig!")
