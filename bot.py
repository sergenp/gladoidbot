import discord
try:
    import bot_token
except ModuleNotFoundError:
    import os 
from discord.ext import commands
from util import send_embed_message, search_youtube
from googletrans import Translator

TRANSLATOR = Translator()
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

@bot.command()
async def ysearch(ctx, *searchStr):
    searchStr = ' '.join(map(str, searchStr))
    await ctx.send(f"Searching  \'{searchStr}\' on youtube...")
    video_link = search_youtube(searchStr)
    if video_link != None:
        await ctx.send(f"Found : {video_link}")
    else:
        await ctx.send("I couldn't find anything")

@bot.command(pass_context=True, description="Example usage:\n h!translate \'I love you\' german")
async def translate(ctx, toTranslate: str = "", toTranslateLanguage: str = "turkish"):
        if toTranslate == "":
            await send_embed_message(ctx, "Gimme something to translate")
        try:
            detect_language = TRANSLATOR.detect(toTranslate).lang
            print(f"Language detected from {toTranslate}, {detect_language}")
            translated = TRANSLATOR.translate(toTranslate, src=detect_language, dest=toTranslateLanguage).text
            await send_embed_message(ctx, f"Word : {toTranslate.upper()} means {translated.upper()} "
                                          f"in {toTranslateLanguage.upper()} ")
        except ValueError:
            await send_embed_message(ctx, "Error, type h!help translate")
try:
    bot.run(bot_token.token())
except NameError:
    bot.run(os.environ['BOT_TOKEN'])

