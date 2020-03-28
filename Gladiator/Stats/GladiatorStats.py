import json
import os


class GladiatorStats:
    def __init__(self, stats={}):
        self.max_stat_value = 100
        self.min_stat_value = 0
        self.stats = stats
            
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

        return self

    def __repr__(self):
        info = ""
        for k in self.stats.keys():
            info += f"{k} : {self.stats[k]} " 
        return info

    def __getitem__(self, key):
        return self.stats[key]

    def __setitem__(self, key, value):
        self.stats[key] = value
