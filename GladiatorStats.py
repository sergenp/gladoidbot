class GladiatorStats:
    def __init__(self, stats={}):
        if len(stats.items()) > 0:
            self.stats = stats
        else:
            self.stats = {
                "Health": 20,
                "Attack Chance": 90,
                "Attack Min. Damage": 3,
                "Attack Max. Damage": 7,
                "Armor": 2,
                "Block Chance": 5,
                "Critical Damage Chance": 5,
                "Critical Damage Boost": 1.5,
            }

    def __add__(self, otherStat):
        for k in otherStat.stats.keys():
            try:
                self.stats[k] += otherStat.stats[k]
            except KeyError:
                self.stats[k] = otherStat.stats[k]

        return GladiatorStats(self.stats)

    def __sub__(self, otherStat):
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
