import discord
import bot_token

class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        if (message.content[0:2] == 'h!'):
            args = message.content[2:].split(' ')
            if (args[0] == 'emojify'):
                del args[0]
                await message.channel.send(emojify(args))

def emojify(text):
    out = ''
    for i in text[0]:
        out += ':regional_indicator_' + i + ': '
    return out

client = MyClient()
client.run(bot_token.token())
