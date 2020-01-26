import json
import os


class GladiatorStats:
    def __init__(self, stats={}):
        if len(stats.items()) > 0:
            self.stats = stats
        else:
            with open(os.path.join("Gladiator", "Settings", "GladiatorGameSettings.json")) as f:
                self.stats = json.load(f)["Gladiator_initial_stats"]

    def __add__(self, otherStat):
        if isinstance(otherStat, dict):
            for k in otherStat.keys():
                try:
                    self.stats[k] += otherStat[k]
                except KeyError:
                    self.stats[k] = otherStat[k]

        elif isinstance(otherStat, GladiatorStats):
            for k in otherStat.stats.keys():
                try:
                    self.stats[k] += otherStat.stats[k]
                except KeyError:
                    self.stats[k] = otherStat.stats[k]

        return GladiatorStats(self.stats)

    def __sub__(self, otherStat):
        if isinstance(otherStat, dict):
            for k in otherStat.keys():
                try:
                    self.stats[k] -= otherStat[k]
                except KeyError:
                    self.stats[k] = otherStat[k]

        elif isinstance(otherStat, GladiatorStats):
            for k in otherStat.stats.keys():
                try:
                    self.stats[k] -= otherStat.stats[k]
                except KeyError:
                    self.stats[k] = otherStat.stats[k]

        return GladiatorStats(self.stats)

    def __repr__(self):
        representation = ""
        for k in self.stats.keys():
            info = f"{k} : {self.stats[k]} "
            representation += info
        return representation

    def __getitem__(self, key):
        return self.stats[key]

    def __setitem__(self, key, value):
        self.stats[key] = value


class GladiatorArmor(GladiatorStats):
    def __init__(self, stats={}):
        if len(stats.items()) == 0:
            self.stats = {"armor": 1}
        else:
            self.stats = stats


class GladiatorSword(GladiatorStats):
    def __init__(self, stats={}):
        if len(stats.items()) == 0:
            self.stats = {"attack_damage": 1}
        else:
            self.stats = stats


class GladiatorBuff(GladiatorStats):
    def __init__(self, stats={}):
        if len(stats.items()) == 0:
            self.stats = {"crit_chance": 2}
        else:
            self.stats = stats
