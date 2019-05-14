import json
import urllib.request
import sqlite3
import csv


# Create a list of alpha iso2 country codes to iterate through
# Source: https://github.com/lukes/ISO-3166-Countries-with-Regional-Codes
with open('slim2.csv', 'r') as file:
    reader = csv.DictReader(file)
    codes = []
    for row in reader:
        codes.append(row['alpha_2'])

# Import travel advisory information from API
traveldata = json.load(urllib.request.urlopen('https://www.travel-advisory.info/api'))

# Configure the use of the SQLite database
conn = sqlite3.connect('worldtravel.db')

# Create database in which to store travel advisory info
conn.execute('''DROP TABLE IF EXISTS countries;''')
conn.execute('''CREATE TABLE countries (
    iso_2 char(2) PRIMARY KEY NOT NULL,
    name varchar(255) NOT NULL,
    score numeric(2, 1) NOT NULL,
    sources_active smallint NOT NULL,
    updated datetime NOT NULL,
    source varchar(255) NOT NULL);''')

for code in codes:
    try:
        conn.execute("INSERT INTO countries (iso_2, name, score, sources_active, updated, source) VALUES (?, ?, ?, ?, ?, ?)",
                     (traveldata['data'][f'{code}']['iso_alpha2'],
                      traveldata['data'][f'{code}']['name'],
                      traveldata['data'][f'{code}']['advisory']['score'],
                      traveldata['data'][f'{code}']['advisory']['sources_active'],
                      traveldata['data'][f'{code}']['advisory']['updated'],
                      traveldata['data'][f'{code}']['advisory']['source']))
    except KeyError:
        print(code)

conn.commit()
conn.close()
