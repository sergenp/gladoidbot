class GladiatorStats:
    def __init__(self, stats={}):
        if len(stats.items()) > 0:
            self.stats = stats
        else:
            self.stats = {
                "attack_chance": 90,
                "attack_damage": 5,
                "armor": 2,
                "block_chance": 3,
                "crit_chance": 5,
                "crit_damage_boost": 1.5,
            }

    def __add__(self, otherStat):
        for k, j in otherStat.stats.items():
            try:
                self.stats[k] += otherStat.stats[k]
            except KeyError:
                self.stats[k] = otherStat.stats[k]

        return GladiatorStats(self.stats)

    def __repr__(self):
        return str(self.stats)

    def __getitem__(self, key):
        return self.stats[key]


class GladiatorArmor:
    def __init__(self, stats={}):
        if len(stats.items()) == 0:
            self.stats = GladiatorStats({"armor": 1})
        else:
            self.stats = GladiatorStats(stats)


class GladiatorSword:
    def __init__(self, stats={}):
        if len(stats.items()) == 0:
            self.stats = GladiatorStats({"attack_damage": 1})
        else:
            self.stats = GladiatorStats(stats)
