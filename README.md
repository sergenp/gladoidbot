## Gladoid

This README contains how to add the bot to your server and what does it do. Feel free to email me if you want to help me develop this bot.


### How Do I add this bot to my server?

Simply click this following link:

https://discordapp.com/api/oauth2/authorize?client_id=598077927577616384&permissions=117824&scope=bot

to add the bot to your server

### What is this bot? What does it do?

Gladoid essentially has been created for a private server called "The Hut". It started as a multi-functional bot
that has some utility functionality, like searching videos on youtube based on given sentence or word. 
It has evolved into a RPG kind-of bot when I started working on a dueling system between players, which basically you challenge a discord member
to a duel, game starts, you have certain kind of moves available to you, you react to the message the bot has send to choose
from one of the moves and with some calculation happening in the background the other player takes damage.

I have recently added a tracking system that tracks the player's duel statistics.(How many won, how many lost, XP, Coins)
With that I have added NPCs to the dueling functionality. You can now, using the exact methods, duel with a computer controlled, player.

In future, I am planning to add more NPCs to the game.

#### Bot Commands

Brackets indicate aliases, e.g. h!b5test and h!ptest would invoke the same command

| Corona           |                                                                                                                                                                                                                   |
|------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| setnewschannel   | Sets the current channel as the corona news channel. Bot will send news about corona virus to this channel after using this command                                                                               |
| virus            | Given country, it shows the specific cases inside that country, otherwise it shows general information about the virus. |
    
| General   |                                                                                                    |
|-----------|----------------------------------------------------------------------------------------------------|
| quote     | Gives out a random quote from a random person from history                                         |
| avatar    | Gives out an embed containing the mentioned user's avatar h!avatar @sergenp | 
| invite    | Gives out the invite link of the bot |
| translate | Translates given arguments to english |
| invite | Gives out the Bot's invite link |
| vote | Gives out a link to vote for my bot |


| Gladiator |                                                                                                                                        |
|-----------|----------------------------------------------------------------------------------------------------------------------------------------|
| challenge | Challenges the another discord member to a gladiator match                                                                             |
| gamead    | Shows a buzzwordy ad for the Gladiator game                                                                                            |
| gamerules | Sends a DM containing how the Gladiator game is played                                                                                 |
| hunt      | Spawns a random NPC you can fight a Gladiator Game with                                                 |
| profile   | Shows your Gladiator Game profile, LVL, XP, Items etc. Or given a tag to another discord Member, shows the same for the discord Member |
| shop      | Given a page (an integer, e.g. h!shop 1), it shows the Items you can buy for your Gladiator. If no argument is given, it shows the available pages instead         |

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


| Interaction |                                                                     |
|--------|---------------------------------------------------------------------|
| hug    | Gives out a random hugging gif from Tenor e.g. h!hug @sergenp |    
| stab   | Gives out a random stabbing gif from Tenor e.g. h!stab @sergenp|
| puke   | Gives out a random puking gif from Tenor e.g. h!puke @sergenp |
| pat   | Gives out a random patting gif from Tenor e.g. h!pat @sergenp |


| Big5Test |                                                                     |
|--------|---------------------------------------------------------------------|
| [ b5test, big5test, ptest ]    | Creates a Big5Test for you to solve. Bot will DM you the results you get |    
| [ b5result, myb5]    | Gets the results of the Big5Test you have solved |


| No Category           |                                                                                                                                                                                                                   |
|------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| changeprefix   | Changes the prefix of the bot from default "h!" |
| help | Shows the default help message, h!help command_name for specific information about the command_name |


### Gladiator Game

`h!hunt`

An example of NPC spawning using this command


![](https://raw.githubusercontent.com/sergenp/the_hut_bot/master/Images/Hunt.png)


An example fight

![](https://github.com/sergenp/the_hut_bot/blob/master/Images/Hunt1.png?raw=true)

![](https://github.com/sergenp/the_hut_bot/blob/master/Images/Hunt2.png?raw=true)

![](https://github.com/sergenp/the_hut_bot/blob/master/Images/Hunt3.png?raw=true)

![](https://github.com/sergenp/the_hut_bot/blob/master/Images/Hunt4.png?raw=true)



### Development

Before launching the bot, make sure the environmental variables are set correctly. You need 3 variables. I suggest creating a `bot_token.py` where the bot.py is at, and define a configurate method like so:

```py
import os

def configurate():
    os.environ["BOT_TOKEN"] = "" # Your discord bot token here
    os.environ["MongoDB_CONNECTION_STRING"] = "" # your mongodb connection string, 
    #required for downloading the Gladiator game information (or uploading), 
    # Keeping track of the Profiles and Game messages.
    # the bad thing about it is that it doesn't save/upload the NPCs, Events, Attack Informations, Settings
    # (I guess I was too lazy, I just uploaded the json files directly into specific collections)
    os.environ["TENOR_API_KEY"] = "" # can be nothing, tenor doesn't seem to care about the API key, 
    # but must be in the environ to make bot work properly.
```

if this file is created and configurated like so, there should be only one problem you would need to fix.

#### MongoDB Downloading Problem

When the bot is first launched, it tries to download all the collections inside MongoDB to their respective folders. This is to make sure everything is updated according to database. If you don't have the NPCs, Events, Attack Informations, Equipments, Settings collections, this will just throw some errors. In order to launch the bot first time, I suggest removing line 16 from bot.py which reads `MongoDatabase.download_gladiator_files_to_local()`.

Bad thing about removing the line is you won't be in sync with your cloud/local mongodb database if you lose the json files inside Gladiator folder. 

##### Why ?

Why did I made it work like this, Why didn't I just connected to the MongoDB database, get what I needed from it realtime?

To be honest, that also would work. But at the beginning of my coding, I wasn't using MondoDB, just was some json files for persistent data, like the collections I have stated above. Later on I added Profiles and Guild specific settings, so to save them to a database made the most sense. With that I also added those said collections to the database. Maybe in the future I will overhaul the system. But I kinda like the I/O system rather than connecting to a cloud database and fetching data from it. It is faster and works better for heroku. If you don't serve it on heroku or you're using a local MongoDB server in it, I would suggest converting e.g. :
```py
def find_equipment(self, equipment_name: str = "") -> dict or None:
    for equipment in self.equipments:
        if equipment["name"] == equipment_name:
            return equipment
    return None
```
to
```py
def find_equipment(self, equipment_name: str="") -> dict or None:
    return self.connector.DatabaseName.Equipments.find_one({"name" : equipment_name})
```

this isn't necessary of course.

#### Now what?

I assume you have created your bot_token.py and deleted the 16th line from bot.py. Now, all you need to do is install the requirements. 
`pip install -r requirements.txt`

Then run the bot:
`python bot.py`

You now have access to every functionality bot offers. Bot should update your profile based on your Discord user id in your MongoDB database. Be sure to check it out after you have done something that updates your profile. MongoDB.Connector.Connector will create a new database called "HutAssistant" in your MongoDB, so there will be no conflict with other collections you have.
