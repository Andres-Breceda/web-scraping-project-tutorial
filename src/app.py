import os
from bs4 import BeautifulSoup
import requests
import time
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import re
import numpy as np

## Obtencion de datos

url = "https://companies-market-cap-copy.vercel.app/index.html"
url1 = "https://companies-market-cap-copy.vercel.app/earnings.html"
req = requests.get(url)
req1 = requests.get(url1)
#print(req.text[:200]) #checar que si obtiene datos

soup = BeautifulSoup(req.text, 'lxml')
soup1 = BeautifulSoup(req1.text, 'lxml')

##Tabla de datos
rev_tesla = dict()
rev_tesla["Year"]=[ye.text for ye in soup.find('div', {'class': 'profile-container pt-3'}).find_all('span', {'class': 'year'}) ]

rev_tesla["Revenue"]= [rev.text for rev in soup.find('div', {'class': 'profile-container pt-3'}).find_all("td") if "B" in rev.text]
rev_tesla["Revenue"]= [x for x in rev_tesla["Revenue"][:16]]

rev_tesla["Change"]= [ch.text for ch in soup.find('div', {'class': 'profile-container pt-3'}).find_all('td', {'class': 'percentage-green'})]
rev_tesla["Change"]= [x for x in rev_tesla["Change"][:16]]+ ['NA']

rev_tesla["Earnings"] = [earn.text for earn in soup1.find('div', {'class': 'profile-container pt-3'}).find('div', {'style': 'overflow-y: scroll;'}).find("table",{'class': 'table', "style" : "width:100%" } ).find_all("td") if any(unit in earn.text for unit in ["Billion", "Million", "B", "M"]) ]
#Magnitud de listas
#max_length = (len(rev_tesla["Year"]), len(rev_tesla["Revenue"]), len(rev_tesla["Change"], len(rev_tesla["Earnings"]))

## DataFrame y filtrado de datos
rev_tesla["Revenue"] = [re.sub(r"[$, B]", "", x) for x in rev_tesla["Revenue"]]
rev_tesla["Change"] = [re.sub(r"[%]", "", x) for x in rev_tesla["Change"]]
pregunta= rev_tesla["Earnings"] 
rev_tesla["Earnings"] = [re.sub(r"[M,B,Billion,Million]", "", x) for x in rev_tesla["Earnings"]]
data = pd.DataFrame(rev_tesla)

#print(rev_tesla)
#print(data.head())

# Conectar a SQLite y guardar los datos
conn = sqlite3.connect("tesla.db")
cursor = conn.cursor()

## Hacer Tabla Annual_earnings SQL  

cursor.execute("""
CREATE TABLE IF NOT EXISTS Annual_earnings (
       Year TEXT PRIMARY KEY,  -- Evita duplicados
       Revenue TEXT,
       Change TEXT,
       Earnings TEXT
)
""")

## Insertar datos en la base de datos en tabla Annual_earnings 

for _, row in data.iterrows():
   cursor.execute("""
   INSERT OR IGNORE INTO Annual_earnings (Year, Revenue, Change, Earnings)
   VALUES (?, ?, ?, ?)""", 
   (row['Year'], row['Revenue'], row['Change'], row['Earnings']))

#print(cursor.execute("SELECT * FROM Annual_earnings;"))
#print(cursor.fetchall())  # Muestra el contenido de la tabla
conn.commit()
conn.close()

##Pregunta
print("Tesla gana ", pregunta[0],"illones en el año",rev_tesla["Year"][0])

##Grafico años revenue

# Asegurar que Revenue es numérico
data["Revenue"] = pd.to_numeric(data["Revenue"], errors="coerce")

# Ordenar por año en orden ascendente
data_sorted = data.sort_values(by="Year", ascending=True)

plt.figure(figsize=(10, 6))
plt.plot(data_sorted["Year"], data_sorted["Revenue"], marker='o', color="green", label="Ingresos")

# Configurar los ticks del eje Y en incrementos de 20 en 20
revenue_max = data_sorted["Revenue"].max()
plt.yticks(np.arange(0, revenue_max + 20, 20))  # Escala en Y de 20 en 20
plt.title("Ingresos anuales de Tesla")
plt.xlabel("Año")
plt.ylabel("Ingresos en billones (USD)")
plt.legend()
plt.grid(True, axis="y", linestyle="--", alpha=0.7)

plt.savefig("revenue_line_plot_scaled.png")
plt.show()

