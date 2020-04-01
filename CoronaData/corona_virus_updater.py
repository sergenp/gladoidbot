from requests_html import HTMLSession, HTML
import pandas as pd
import os
import json
import requests
from datetime import datetime

session = HTMLSession()
try:
    os.mkdir("CoronaData/news")
except (FileExistsError, FileNotFoundError):
    pass


header = {
  "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246",
  "X-Requested-With": "XMLHttpRequest"
}

def update_data():
    r = session.get('https://www.worldometers.info/coronavirus/', headers=header)

    title = ["Total Cases","Total Deaths","Total Recovered"]
    count = []
    for k in r.html.find("#maincounter-wrap"):
        count.append(k.find("span", first=True).text)

    total_inf = dict(zip(title, count))

    if total_inf:
        with open('CoronaData/total_inf.json', 'w') as outfile:
            json.dump(total_inf, outfile)

    cv19_table = pd.read_html(r.text)[0]
    cv19_table = cv19_table.drop("Tot Cases/1M pop", axis=1).rename(columns = {"Country,Other" : "Country", "Serious,Critical" : "Serious"})[:-1]
    cv19_table.to_json("CoronaData/data.json", orient='records')

    

def get_corona_news():
    r = session.get('https://www.worldometers.info/coronavirus/', headers=header)
    now = datetime.now()
    div_id = f"newsdate{now.year}-{now.month:02d}-{now.day:02d}"
    news = [x.text.replace("[source]", "") for x in r.html.find(f"#{div_id} > .news_post")]
    info = {"0" : news}
    print(news)
    # lets check if there any new news
    if os.path.exists(f'CoronaData/news/{div_id}.json'):
        old_news = json.load(open(f'CoronaData/news/{div_id}.json', 'r'))
        if len(old_news["0"]) == len(info["0"]):
            return False
        else:
            with open(f'CoronaData/news/{div_id}.json', 'w') as outfile:
                json.dump(info, outfile)
            return list(set(info["0"]) - set(old_news["0"]))
    else:    
        with open(f'CoronaData/news/{div_id}.json', 'w') as outfile:
            json.dump(info, outfile)
        return news
        