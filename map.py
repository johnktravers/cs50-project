import json
import urllib.request
import sqlite3
import csv
import folium
import pandas as pd
import os
import numpy as np


# Create a list of alpha iso2 country codes to iterate through
# Source: https://github.com/lukes/ISO-3166-Countries-with-Regional-Codes
with open('slim.csv', 'r') as file:
    reader = csv.DictReader(file)
    codes2 = []
    codes3 = []
    for row in reader:
        codes2.append(row['alpha_2'])
        codes3.append(row['alpha_3'])

# Import travel advisory information from API
traveldata = json.load(urllib.request.urlopen('https://www.travel-advisory.info/api'))

# Configure the use of the SQLite database
conn = sqlite3.connect('worldtravel.db')

# Create database in which to store travel advisory info
conn.execute('''DROP TABLE IF EXISTS countries;''')
conn.execute('''CREATE TABLE countries (
    iso_2 char(2) PRIMARY KEY NOT NULL,
    iso_3 char(3) NOT NULL,
    name varchar(255) NOT NULL,
    score numeric(2, 1) NOT NULL,
    sources_active smallint NOT NULL,
    updated datetime NOT NULL,
    source varchar(255) NOT NULL);''')

for i, code in enumerate(codes2):
    conn.execute("INSERT INTO countries (iso_2, iso_3, name, score, sources_active, updated, source) VALUES (?, ?, ?, ?, ?, ?, ?)",
                 (code,
                  codes3[i],
                  traveldata['data'][f'{code}']['name'],
                  traveldata['data'][f'{code}']['advisory']['score'],
                  traveldata['data'][f'{code}']['advisory']['sources_active'],
                  traveldata['data'][f'{code}']['advisory']['updated'],
                  traveldata['data'][f'{code}']['advisory']['source']))

# Commit the changes to the database
conn.commit()

# Write country and score data into csv file
with open('scores.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerow(['Country', 'Score'])
    for row in conn.execute("SELECT iso_3, score FROM countries"):
        writer.writerow(row)

# World map data
world = os.path.join('data', 'countries.geojson')
scores = os.path.join('', 'scores.csv')
country_scores = pd.read_csv(scores)

m = folium.Map(width=1000, height=700, location=[20, 4], zoom_start=2,
               tiles='https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}',
               attr='Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ')

# Add attributes to create choropleth map
folium.Choropleth(
    geo_data=world,
    data=country_scores,
    columns=['Country', 'Score'],
    key_on='feature.properties.ISO_A3',
    fill_color='RdYlGn_r',
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name='Travel Risk Rating',
    name='choropleth',
    nan_fill_color='#D3D3D3',
    nan_fill_opacity=0.5,
    bins=10,
    line_weight=1.5
).add_to(m)

# # Add tooltips for hovering over countries
# folium.GeoJson(

# ).add_to(m)

# Save the map to an html file
m.save('map.html')

# Close the sqlite database
conn.close()
