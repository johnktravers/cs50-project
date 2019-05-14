import json
import requests
import sqlite3
from flask import Flask, render_template


# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure the use of the SQLite database
conn = sqlite3.connect('worldtravel.db')


@app.route("/")
def index():
    """Show the interactive map of world travel risks"""

    return render_template('index.html')


@app.route("/country", methods=["GET"])
def country():
    """Retrieve and show data for the selected country"""

    # Headers for the Travel Advisory API
    # See http://developer.tugo.com/docs/read/travelsafe for details
    headers = {
        'X-Auth-API-Key': 'h5bgsjdj9aaa8rjns645ahj7',
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    # Get the user's desired country code
    alpha = 'DZ'

    # Request response for the selected country
    response = requests.get('https://api.tugo.com/v1/travelsafe/countries/{}'.format(alpha),
                            headers=headers)

    # Load the specified country's data as a json object
    data = json.loads(response.content)

    # Compile data into variables to easily pass into html file
    # Name
    name = data['name']
    updated = data['dateCreated'][0:10]

    # Travel and regional advisory warning
    advisory = data['advisories']['description']
    if data['hasRegionalAdvisory']:
        regional_cat = []
        regional_desc = []
        for i in range(len(data['advisories']['regionalAdvisories'])):
            regional_cat.append(data['advisories']['regionalAdvisories'][i]['category'])
            regional_desc.append(data['advisories']['regionalAdvisories'][i]['description'])
    else:
        regional_cat = ["None"]
        regional_desc = ["Exercise normal security precautions"]

    # Visa entry and exit requirements:
    entry_exit_desc = data['entryExitRequirement']['description']
    req_cat = []
    req_desc = []
    for i in range(len(data['entryExitRequirement']['requirementInfo'])):
        req_cat.append(data['entryExitRequirement']['requirementInfo'][i]['category'])
        req_desc.append(data['entryExitRequirement']['requirementInfo'][i]['description'])

    # Health and safety advisories:
    health_desc = data['health']['description']

    # Animal-related health concerns
    animal_cat = []
    animal_desc = []
    for i in range(len(data['health']['diseasesAndVaccinesInfo']['Animals'])):
        animal_cat.append(data['health']['diseasesAndVaccinesInfo']['Animals'][i]['category'])
        animal_desc.append(data['health']['diseasesAndVaccinesInfo']['Animals'][i]['description'])

    # People-related health concerns
    person_cat = []
    person_desc = []
    for i in range(len(data['health']['diseasesAndVaccinesInfo']['Person-to-Person'])):
        person_cat.append(data['health']['diseasesAndVaccinesInfo']['Person-to-Person'][i]['category'])
        person_desc.append(data['health']['diseasesAndVaccinesInfo']['Person-to-Person'][i]['description'])

    # Food or water-related health concerns
    food_cat = []
    food_desc = []
    for i in range(len(data['health']['diseasesAndVaccinesInfo']['Food/Water'])):
        food_cat.append(data['health']['diseasesAndVaccinesInfo']['Food/Water'][i]['category'])
        food_desc.append(data['health']['diseasesAndVaccinesInfo']['Food/Water'][i]['description'])

    # Vaccine Information
    vacc_cat = []
    vacc_desc = []
    for i in range(len(data['health']['diseasesAndVaccinesInfo']['Vaccines'])):
        vacc_cat.append(data['health']['diseasesAndVaccinesInfo']['Vaccines'][i]['category'])
        vacc_desc.append(data['health']['diseasesAndVaccinesInfo']['Vaccines'][i]['description'])

    # Insect-bourne illnesses
    insect_cat = []
    insect_desc = []
    for i in range(len(data['health']['diseasesAndVaccinesInfo']['Insects'])):
        insect_cat.append(data['health']['diseasesAndVaccinesInfo']['Insects'][i]['category'])
        insect_desc.append(data['health']['diseasesAndVaccinesInfo']['Insects'][i]['description'])
    insect_cat.append(data['health']['diseasesAndVaccinesInfo']['Malaria'][0]['category'])
    insect_desc.append(data['health']['diseasesAndVaccinesInfo']['Malaria'][0]['description'])

    # Health Info
    health_info_cat = []
    health_info_desc = []
    for i in range(len(data['health']['healthInfo'])):
        health_info_cat.append(data['health']['healthInfo'][i]['category'])
        health_info_desc.append(data['health']['healthInfo'][i]['description'])

    # Law and culture
    cult_desc = data['lawAndCulture']['description']
    law_cat = []
    law_desc = []
    for i in range(len(data['lawAndCulture']['lawAndCultureInfo'])):
        law_cat.append(data['lawAndCulture']['lawAndCultureInfo'][i]['category'])
        law_desc.append(data['lawAndCulture']['lawAndCultureInfo'][i]['description'])

    # Climate
    clim_desc = []
    if data['climate']['description']:
        clim_cat = ["General Climate"]
        clim_desc.append(data['climate']['description'])
    else:
        clim_cat = []
        for i in range(len(data['climate']['climateInfo'])):
            clim_cat.append(data['climate']['climateInfo'][i]['category'])
            clim_desc.append(data['climate']['climateInfo'][i]['description'])

    return render_template("country.html", name=name, advisory=advisory,
                           regional_cat=regional_cat, regional_desc=regional_desc,
                           entry_exit_desc=entry_exit_desc, req_cat=req_cat,
                           req_desc=req_desc, health_desc=health_desc,
                           animal_cat=animal_cat, animal_desc=animal_desc,
                           person_cat=person_cat, person_desc=person_desc,
                           food_cat=food_cat, food_desc=food_desc,
                           vacc_cat=vacc_cat, vacc_desc=vacc_desc,
                           insect_cat=insect_cat, insect_desc=insect_desc,
                           health_info_cat=health_info_cat, health_info_desc=health_info_desc,
                           cult_desc=cult_desc, law_cat=law_cat, law_desc=law_desc,
                           clim_cat=clim_cat, clim_desc=clim_desc, updated=updated)

@app.route("/test")
def test():
    """Try to get the map to show up. Fingers crossed"""

    return render_template('test.html')