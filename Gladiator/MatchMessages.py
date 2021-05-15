import sys

sys.path.append("..")

from MongoDB.Connector import Connector

MongoDatabase = Connector()


class MatchMessages:
    def __init__(self, players, match_date):
        self.Date = match_date
        self.Players = [str(player) for player in players]
        self.Messages = []

    def add_msg(self, msg):
        if isinstance(msg, str):
            self.Messages.append(msg)
        elif isinstance(msg, list):
            for m in msg:
                self.Messages.append(m)

    def save(self):
        MongoDatabase.save_messages(self.__dict__)
