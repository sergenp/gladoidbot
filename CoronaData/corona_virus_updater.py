from requests_html import HTMLSession
import pandas as pd
import os
import json

def update_data():
    session = HTMLSession()
    r = session.get('https://www.worldometers.info/coronavirus/')

    title = ["Total Cases","Total Deaths","Total Recovered"]
    count = []
    for k in r.html.find("#maincounter-wrap"):
        count.append(k.find("span", first=True).text)

    total_inf = dict(zip(title, count))

    with open('CoronaData/total_inf.json', 'w') as outfile:
        json.dump(total_inf, outfile)

    tables = pd.read_html('https://www.worldometers.info/coronavirus/')
    cv19_table = tables[0]
    cv19_table = cv19_table.drop("Tot Cases/1M pop", axis=1).rename(columns = {"Country,Other" : "Country", "Serious,Critical" : "Serious"})[:-1]
    cv19_table.to_json("CoronaData/data.json", orient='records')