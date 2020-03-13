from requests_html import HTMLSession
import pandas as pd
import os
import json

session = HTMLSession()
try:
    os.mkdir("CoronaData/news")
except FileExistsError:
    pass


def update_data():
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

def get_corona_news():
    r = session.get('https://www.worldometers.info/coronavirus/')
    today = r.html.find("#innercontent > h4", first=True).text.replace("(GMT):", "").replace(" ", "")
    news = [x.text.replace("[source]", "") for x in r.html.find("#innercontent > ul > li")]
    info = {today : news}

    # lets check if there any new news
    if os.path.exists(f'CoronaData/news/{today}.json'):
        old_news = json.load(open(f'CoronaData/news/{today}.json', 'r'))
        if len(old_news[today]) == len(info[today]):
            return False
    
    with open(f'CoronaData/news/{today}.json', 'w') as outfile:
        json.dump(info, outfile)
    return True

