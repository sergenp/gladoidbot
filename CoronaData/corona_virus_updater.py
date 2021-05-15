from requests_html import HTMLSession
from user_agent import generate_user_agent
import os
import json
from datetime import datetime

session = HTMLSession()

try:
    os.mkdir(os.path.join("CoronaData", "news"))
except (FileExistsError, FileNotFoundError):
    pass


def update_data():

    r = session.get("https://api.covid19api.com/summary").json()

    with open(os.path.join("CoronaData", "total_inf.json"), "w") as outfile:
        json.dump(r["Global"], outfile)

    with open(os.path.join("CoronaData", "data.json"), "w") as outfile:
        json.dump(r["Countries"], outfile)


def get_corona_news():
    header = {"User-Agent": generate_user_agent(), "X-Requested-With": "XMLHttpRequest"}
    r = session.get("https://www.worldometers.info/coronavirus/", headers=header)
    now = datetime.now()
    div_id = f"newsdate{now.year}-{now.month:02d}-{now.day:02d}"
    news = [
        x.text.replace("[source]", "") for x in r.html.find(f"#{div_id} > .news_post")
    ]
    info = {"0": news}
    file_path = os.path.join("CoronaData", "news", f"{div_id}.json")
    # lets check if there any new news
    if os.path.exists(file_path):
        old_news = json.load(open(file_path, "r"))
        if len(old_news["0"]) == len(info["0"]):
            return False
        else:
            with open(file_path, "w") as outfile:
                json.dump(info, outfile)
            return list(set(info["0"]) - set(old_news["0"]))
    else:
        with open(file_path, "w") as outfile:
            json.dump(info, outfile)
        return news
