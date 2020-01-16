import os

try:
    os.mkdir("matches")
except FileExistsError:
    pass


def addMatch(matchName):
    open(f"matches{os.path.sep}{matchName}.txt", "w")

def addMatchEvent(matchName, event):
    with open(f"matches{os.path.sep}{matchName}.txt", "a") as f:
        f.writelines(event + ";")


addMatchEvent("abc","event")