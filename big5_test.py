import asyncio
from discord import Embed
from discord.ext import commands
from Big5Test.Test import Big5Test
from util import send_embed_message
from MongoDB.Connector import Connector

tests = {}
MongoDB = Connector()
reactions_map = {"1️⃣" : 1,  "2️⃣" : 2,  "3️⃣" : 3,  "4️⃣" : 4, "5️⃣" : 5}

class Big5TestCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.command(pass_context=True,aliases=["big5test", "ptest"], description="A Big 5 Personality test")
    async def b5test(self, ctx):
        tests[ctx.author.id] = Big5Test(ctx.author.id)
        await ctx.send("Successfully created a Big5 test for you, please answer the questions accordingly, note that your Big5 will be saved at the end of the test.")
        return await self.test_loop(ctx, ctx.author.id)

    @commands.command(pass_context=True, aliases=["b5result"], description="A Big 5 Personality test")
    async def myb5(self, ctx):
        res = MongoDB.get_big5_results(ctx.author.id)
        if res:
            res.pop("_id")
            content = ""
            for k,v in res.items():
                content += f"{k} : {v}\n"
            await send_embed_message(ctx, content=content, title=f"{ctx.author.name}'s Big5 Score")
        else:
            await ctx.send("Couldn't find any big5 results for you, be sure to take the test first!")

    async def test_loop(self, ctx, test_id, msg=None):
        test = tests[test_id]
        curr_q = test.get_current_question()        
        em = Embed(description=curr_q.body, title=f"Question #{curr_q.Id} for {ctx.author.name}")
        em.set_footer(text=f"1=Disagree, 3=Neutral and 5=Agree. Currently at {curr_q.Id}/50. You have a minute to answer each question.\n\nNote that if you add any other reaction, your answer will be registered as 1")

        if not msg:
            msg = await ctx.send(embed=em)
            for reaction in reactions_map.keys():
                await msg.add_reaction(reaction)
        else:
            await msg.edit(embed=em)
        
        def check(reaction, user):
            return user == ctx.message.author and reaction.message.id == msg.id

        try:
            reaction, _ = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
            test.answer_question(reactions_map.get(reaction.emoji, 1))
        
        except asyncio.TimeoutError:
            await ctx.send("You haven't answered the question in time, deleting the test")
            del tests[ctx.author.id]
            await msg.delete()

        next_q = test.get_next_question()
        if next_q:
            return await self.test_loop(ctx, test_id, msg)
        else:
            score_dict = test.end_test()
            content = ""
            for k,v in score_dict.items():
                content += f"{k} : {v}\n"
            await send_embed_message(ctx, content=content, title=f"{ctx.author.name}'s Big5 Score")
            score_dict["_id"] = ctx.author.id
            MongoDB.save_big5_results(score_dict)
            del tests[ctx.author.id]
        
def setup(bot):
    bot.add_cog(Big5TestCog(bot))
