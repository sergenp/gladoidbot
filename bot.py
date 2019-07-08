import discord
import bot_token
from discord.ext import commands
from util import send_embed_message

bot = commands.Bot(command_prefix="h!")

@bot.event
async def on_ready():
    print(f"Connected! \n{bot.user.name}\nId: {bot.user.id}\n")

@bot.command()
async def emojify(ctx, *args):
    out = ''
    for i in args:
        for l in i:
            out += ':regional_indicator_' + l.lower() + ': '
        out += '    '
    await ctx.send(out)
    
@bot.command()
async def synonym(ctx, arg):
    for i in [
        {'word': 'krizzle', 'syn': 'Korean gay'},
        {'word': 'inubakkari', 'syn': 'The Lord of Us All'},
        {'word': 'sergenp', 'syn': 'Third World Genius'},
        {'word': 'marquitos', 'syn': 'mosquito'},
        {'word': 'iara', 'syn': 'hmm'}
    ]:
        if i['word'] == arg:
            wrd = i['word']
            syn = i['syn']
    await send_embed_message(ctx, 'Another word for ' + wrd + ' is ' + syn + '.')

bot.run(bot_token.token() or process.env.BOT_TOKEN)
