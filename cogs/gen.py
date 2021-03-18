import discord
from discord.ext import commands
from .util import send_embed_message
from google_trans_new import google_translator
import requests
import ast

TRANSLATOR = google_translator()

    
def insert_returns(body):
    # insert return stmt if the last expression is a expression statement
    if isinstance(body[-1], ast.Expr):
        body[-1] = ast.Return(body[-1].value)
        ast.fix_missing_locations(body[-1])

    # for if statements, we insert returns into the body and the orelse
    if isinstance(body[-1], ast.If):
        insert_returns(body[-1].body)
        insert_returns(body[-1].orelse)

    # for with blocks, again we insert returns into the body
    if isinstance(body[-1], ast.With):
        insert_returns(body[-1].body)

def setup(bot):
    bot.add_cog(General(bot))


class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, description="Translates given text to english\n")
    async def translate(self, ctx, *, to_translate):
        if to_translate == "":
            await send_embed_message(ctx, "Gimme something to translate")
            return 

        detect_language = TRANSLATOR.detect(to_translate)[1]
        translated = TRANSLATOR.translate(to_translate, lang_tgt='en')

        field_list = [{
                "name" : "Original Text",
                "value" : to_translate,
                "inline" : False
            },
            {
                "name" : "Translated",
                "value" : translated,
                "inline" : False
            }
        ]
        await send_embed_message(ctx, title=f"Language detected {detect_language.title()}",
                                 field_list=field_list)

    @commands.command()
    async def quote(self, ctx, amount=1):
        if amount > 10:
            amount = 10

        for _ in range(amount):
            data = requests.get("https://api.quotable.io/random").json()
            await send_embed_message(ctx, author_name=data["author"], content=data["content"])
    
    @commands.command(description="Returns the invite link of the bot")
    async def invite(self, ctx):
        await ctx.send("https://discordapp.com/api/oauth2/authorize?client_id=598077927577616384&permissions=117824&scope=bot")
 
    @commands.command(description="Vote for me uwu")
    async def vote(self, ctx):
        await ctx.send("https://top.gg/bot/598077927577616384/vote")

    @commands.command(description="Shows the avatar of the user or the one mentioned")
    async def avatar(self, ctx, user:discord.Member = None):
        if user:
            await send_embed_message(ctx, title=f"Showing avatar of {user.name}", image_url=user.avatar_url)
        else:
            await send_embed_message(ctx, title=f"Showing avatar of {ctx.message.author.name}", image_url=ctx.message.author.avatar_url)

    @commands.command(name="eval")
    async def eval_fn(self, ctx, *, cmd):
        if ctx.author.id == 314800228480057355 or ctx.author.id == 225347010553839616:
            fn_name = "_eval_expr"
            cmd = cmd.strip("` ")
            # add a layer of indentation
            cmd = "\n".join(f"    {i}" for i in cmd.splitlines())
            # wrap in async def body
            body = f"async def {fn_name}():\n{cmd}"
            parsed = ast.parse(body)
            body = parsed.body[0].body
            insert_returns(body)
            env = {
                'bot': ctx.bot,
                'discord': discord,
                'commands': commands,
                'ctx': ctx,
                '__import__': __import__
            }
            exec(compile(parsed, filename="<ast>", mode="exec"), env)
            result = (await eval(f"{fn_name}()", env))
        else:
            await ctx.send("You aren't my creator, therefore I won't do your bidding.")

