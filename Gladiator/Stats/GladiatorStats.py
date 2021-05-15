import json
import pathlib

path = pathlib.Path(__file__).parent.absolute()

PRIMARY_STATS = ["Attack", "Defence"]


def get_secondary_stat(
    main_stat_val=1, percentage_limit=10, scale_limit=0.5, divisor=1.25, round_to=1
):
    exp = scale_limit * main_stat_val / divisor
    inner = 1 - (0.01 / (0.01 * percentage_limit))
    return round(percentage_limit * (1 - inner ** exp), round_to)


class GladiatorStats:
    def __init__(self, stats: dict = None, **kwargs):
        self.max_stat_value = 100  # max value of any given stat, should actually be included in the GladiatorGameSettings.json, but too lazy
        self.min_stat_value = 0
        self.stats = stats
        self.stats.update(kwargs)
        self.conversion = json.load(
            open(path / ".." / "Settings" / "GladiatorGameSettings.json", "r")
        )["secondary_stats"]
        health_inf = self.conversion.pop("Health")
        # adding or subtracting stats calls update_secondary_stats(), which in turn would update Health,
        # if we were to add some critical strike chance, we'd end up recalculating Health based on,
        # Defence main stat, so in mid fight, this would make the Gladiator's Health stat reset into it's original
        # i.e. Health should only be calculated once and never again
        self.stats["Health"] = get_secondary_stat(
            self.stats["Defence"],
            health_inf["limit"],
            health_inf["scale_limit"],
            health_inf["divisor"],
            health_inf["round_to"],
        )
        self.update_secondary_stats()

    ## update the GladiatorStats, add/remove stats
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
            # if there is no k in the self.stats, create a self.stats[k]
            # and set it to whatever is added
            # This is used in turn based debuff effects
            except KeyError:
                self.stats[k] = otherStat[k]

        self.update_secondary_stats()
        return self

    # same as add but instead subtracts
    def __sub__(self, otherStat):
        other_dict = {}
        if isinstance(otherStat, dict):
            other_dict = otherStat
        elif isinstance(otherStat, GladiatorStats):
            other_dict = otherStat.stats

        for k in other_dict.keys():
            try:
                # when subtracted, if stat's min value is lesser than allowed, set it to it's min
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

    # mimic the dictionary, so we could use GladiatorPlayer.stats["Attack Damage"]
    # or something similiar
    def __getitem__(self, key):
        return self.stats[key]

    # update secondary stats if only key isn't Health and key is either Attack or Defence
    # that would mean e.g. if an Attack value is set, the secondary stats will updated accordingly
    # if a secondary stat is updated directly, like Critical Chance, secondary stats won't be updated
    # since key isn't Attack or Defence i.e. primary stats
    def __setitem__(self, key, value):
        self.stats[key] = value
        if key != "Health" and key in PRIMARY_STATS:
            self.update_secondary_stats()

    def update_secondary_stats(self):
        for key, val in self.conversion.items():
            # calculate secondary stats
            self.stats[key] = get_secondary_stat(
                self.stats[val["primary_stat"]],
                val["limit"],
                val["scale_limit"],
                val["divisor"],
                val["round_to"],
            )
