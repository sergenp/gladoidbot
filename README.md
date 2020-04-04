## The Hut Assistant

This README contains how to add the bot to your server, what does it do and how to run the bot if you're a developer.


### How Do I add this bot to my server?

Simply click this following link:

https://discordapp.com/api/oauth2/authorize?client_id=598077927577616384&permissions=117824&scope=bot

to add the bot to your server

### What is this bot? What does it do?

Hut Assistant essentially has been created for a private server called "The Hut". It started as a multi-functional bot
that has some utility functionality, like searching videos on youtube based on given sentence or word. 
It has evolved into a RPG kind-of bot when I started working on a dueling system between players, which basically you challenge a discord member
to a duel, game starts, you have certain kind of moves available to you, you react to the message the bot has send to choose
from one of the moves and with some calculation happening in the background the other player takes damage.

I have recently added a tracking system that tracks the player's duel statistics.(How many won, how many lost, XP, Coins)
With that I have added NPCs to the dueling functionality. You can now, using the exact methods, duel with a computer controlled, player.

In future, I am planning to add more NPCs to the game.

#### Bot Commands

| Corona           |                                                                                                                                                                                                                   |
|------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| setnewschannel   | Sets the current channel as the corona news channel. Bot will send news about corona virus to this channel after using this command                                                                               |
| virus            | Given country, it shows the specific cases inside that country, otherwise it shows general information about the virus. Information about the virus is gotten from the https://www.worldometers.info/coronavirus/ |
    
| General   |                                                                                                    |
|-----------|----------------------------------------------------------------------------------------------------|
| quote     | Gives out a random quote from a random person from history                                         |
| translate | Example usage: h!translate 'I love you' german  h!translate [toTranslate] [toTranslateLanguage=en] |
| ysearch   | Searchs given strings in youtube and writes out the first video it finds                           |

| Gladiator |                                                                                                                                        |
|-----------|----------------------------------------------------------------------------------------------------------------------------------------|
| challenge | Challenges the another discord member to a gladiator match                                                                             |
| gamead    | Shows a buzzwordy ad for the Gladiator game                                                                                            |
| gamerules | Sends a DM containing how the Gladiator game is played                                                                                 |
| hunt      | Spawns a random NPC(%90) or fails(10%). You can fight a Gladiator Game with spawned NPC                                                |
| profile   | Shows your Gladiator Game profile, LVL, XP, Items etc. Or given a tag to another discord Member, shows the same for the discord Member |
| shop      | Given a page, it shows the Items you can buy for your Gladiator. If no argument is given, it shows the available pages instead         |

| Meme     |                                                                                                                    |
|----------|--------------------------------------------------------------------------------------------------------------------|
| blb      | Generates a be like bill image given gender value, which can be F or M for Female or Male  h!blb [user] [gender=M] |
| buzzword | Gives out a random company buzzword                                                                                |
| dadjoke  | Gives out a random dad joke                                                                                        |
| meme     | Gives out a random meme                                                                                            |
| swq      | Gives out a random star wars quote                                                                                 |
| xkcd     | Gives out a random xkcd comic                                                                                      |
| yesno    | Gives out a random yes/no/maybe image  Example:  h!yesno is my life going to be alright?                           |     

| Trivia |                                                                     |
|--------|---------------------------------------------------------------------|
| ask    | Asks a random trivia question to the user who have used the command |        

### I am a developer. I want to add stuff to this bot. What do I need to do?

First of all, thanks! I have worked hard to make this bot work the way it works now and I would appreciate any addition you'd make to the bot. 

#### How to add stuff

##### How to run the bot
You'd first need to clone this project. 
Then you need to create a discord bot of your own to test the functionalities this bot has. 
You can follow this guide on how to create your own discord bot:
https://discordpy.readthedocs.io/en/latest/discord.html

When you have created your own bot, create a bot_token.py file where the bot.py file exists. And write this:
```python
#bot_token.py
def token():
    return "MY_SECRET_TOKEN_THAT_I_COPIED_FROM_DISCORD_DEV_PORTAL"
```

In order to use the Gladiator Profiles, you'd need to actually own a google cloud developer account. 
The bot uses the google cloud storage to store the user profile data. 
You don't need to use this functionality when you are using the bot locally. 
But the google api will still need your credentials. 

In order to use the bot without uploading files to the cloud, you should comment out some code, which are these:

These function is in the GladiatorProfile.py

```python
# Wherever you see an import from Gladiator.UserProfileData.backup_user_data, comment out the line. Currently
# from Gladiator.UserProfileData.backup_user_data import backup_single_profile
```

```python
def save_profile(func):
    def wrapper(self, *args, **kwargs):
        out = func(self, *args, **kwargs)
        filename = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "UserProfileData", f"{self.profile_stats['Id']}.json")
        json.dump(self.profile_stats, open(
            filename, "w"), indent=4, sort_keys=True)
        # comment out backup_single_profile line
        #backup_single_profile(filename)
        return out
    return wrapper
```
And inside bot.py file:

```python
# from Gladiator.UserProfileData.backup_user_data import download_profiles
# .
# .
# .
@bot.event
async def on_ready():
    print(f"Connected!\nName: {bot.user.name}\nId: {bot.user.id}\n")
    corona_update_task.start()
    #download_profiles()
```
Now that you have commented out the functions that requires a credential for u to upload files to the cloud, you can now start your own bot 
For linux, open up a terminal in the directory where bot.py exist and run:
```
python3 bot.py
```
For windows, open the run.bat

##### What now?

You can now try out the commands! Simply type h!help in your server where you have added the bot to, then check out the commands. 
Feel free to change your own local code and try out different things.

##### What would you like me to add?

Unless you are going to make a pull request to this repository, It is your own bot now! You can do whatever you want with it.

If you are going to be making a pull request, I mostly want NPCs and Arts. which is pretty easy for you to add even if you don't know any python.

###### How to add an NPC?
You would just need to create a .json file with these keys for your NPC to appear in h!hunt command: 

```json
{
    "Name": "Necromancer",
    "Stats": {
        "Health": 10,
        "Attack Chance": 62,
        "Attack Min. Damage": 0,
        "Attack Max. Damage": 0,
        "Magic Damage": 8,
        "Magic Armor": 1,
        "Armor": 0,
        "Block Chance": 0,
        "Critical Damage Chance": 35,
        "Critical Damage Boost": 1.1
    },
    "NPC_Level_Range": [
        5,
        25
    ],
    "NPC_Images_Path": [
        "Necromancer.jpg",
        "Necromancer1.jpg"
    ],
    "Attack Ids": [
        3,
        8
    ],
    "Debuff Ids": [
        1
    ]
}
```

The keys of the json file is pretty self explainatory but "Attack Ids" and "Debuff Ids". 
Those 2 keys come from the Gladiator/AttackInformation folder

Attack Ids are from : Gladiator/AttackInformation/GladiatorAttackBuffs.json

Debuff Ids are from : Gladiator/AttackInformation/GladiatorTurnDebuffs.json


"Attack Ids" key makes your NPC to use the attacks that appear in the related json file. 
This list must have at least 1 key, otherwise well, you won't be able to battle your NPC. 

"Debuff Ids" gives your NPC a chance to apply debuff to the player(Which currently is just a damage per turn debuff, may extend to something more in the future) each attack.
This list can be empty like 
```json
    "Debuff Ids": []
```

When you add your custom NPC.json file along with images to that NPC, simply git commit to the master branch and give me a pull request. I will check out your custom NPC and make sure it is balanced(we probably won't want a 1921823 HP dark elf) and add it to our game!
