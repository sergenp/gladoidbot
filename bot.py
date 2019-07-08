import discord
import bot_token
from discord.ext import commands

bot = commands.Bot(command_prefix="h!")

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
    
    await ctx.send('Another word for ' + wrd + ' is ' + syn + '.')

bot.run(bot_token.token() or process.env.BOT_TOKEN)
