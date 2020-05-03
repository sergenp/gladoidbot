import json
import os

def get_secondary_stat(main_stat_val=1, percentage_limit=10, scale_limit=0.5, divisor=1.25, round_to=1):
    exp = scale_limit*main_stat_val/divisor
    inner=1-(0.01/(0.01*percentage_limit))
    return round(percentage_limit * (1-inner**exp),round_to)


class GladiatorStats:
    def __init__(self, stats:dict = None, **kwargs):
        self.update_count = 0
        self.max_stat_value = 100
        self.min_stat_value = 0
        self.stats = stats
        self.stats.update(kwargs)
        self.conversion = json.load(open(os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "Settings", "GladiatorGameSettings.json"), "r"))["secondary_stats"]
        health_inf = self.conversion["Health"]
        self.stats["Health"] = get_secondary_stat(self.stats["Defence"], health_inf["limit"], health_inf["scale_limit"], health_inf["divisor"], health_inf["round_to"])

    def __add__(self, otherStat):
        other_dict = {}
        if isinstance(otherStat, dict):
            other_dict = otherStat
        elif isinstance(otherStat, GladiatorStats):
            other_dict = otherStat.stats

        for k in other_dict:
            try:
                self.stats[k] += other_dict[k]
                if self.stats[k] > self.max_stat_value:
                    self.stats[k] = self.max_stat_value
            except KeyError:
                self.stats[k] = otherStat[k]

        self.update_secondary_stats()
        return self

    def __sub__(self, otherStat):
        other_dict = {}
        if isinstance(otherStat, dict):
            other_dict = otherStat
        elif isinstance(otherStat, GladiatorStats):
            other_dict = otherStat.stats

        for k in other_dict.keys():
            try:
                self.stats[k] -= otherStat[k]
                if self.stats[k] < self.min_stat_value:
                    self.stats[k] = self.min_stat_value
            except KeyError:
                self.stats[k] = otherStat[k]

        self.update_secondary_stats()
        return self

    def __repr__(self):
        info = ""
        for k in self.stats.keys():
            info += f"{k} : {self.stats[k]}\n" 
        return info

    def __getitem__(self, key):
        return self.stats[key]

    def __setitem__(self, key, value):
        self.stats[key] = value
        if key != 'Health':
            self.update_secondary_stats()
    
    def update_secondary_stats(self):
        for key, val in self.conversion.items():
            if key == 'Health':
                continue
            
            self.stats[key] = get_secondary_stat(self.stats[val["primary_stat"]], val["limit"], val["scale_limit"], val["divisor"], val["round_to"])