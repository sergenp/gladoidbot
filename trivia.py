from discord.ext import commands
import requests
import random
from util import send_embed_message
import html

from Gladiator.Profile import Profile

ANSWER_EMOJIS = [u"\U0001F1E6", u"\U0001F1E7",
                 u"\U0001F1E8", u"\U0001F1E9"]


class Trivia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channels = set()

    @commands.command()
    async def ask(self, ctx):
        if ctx.channel.id in self.channels:
            await ctx.send(
                "Waiting for the other question to get answered. Try the command in other channels or wait a bit")
            return
        
        self.channels.add(ctx.channel.id)
        question_data = requests.get(
            "https://opentdb.com/api.php?amount=1").json()["results"][0]
        question = html.unescape(question_data["question"])
        question_data["incorrect_answers"].append(
            question_data["correct_answer"])
        random.shuffle(question_data["incorrect_answers"])
        answers = question_data["incorrect_answers"]
        for k, _ in enumerate(answers):
            answers[k] = html.unescape(answers[k])

        answers = dict(zip(ANSWER_EMOJIS, answers))

        field_list = []
        for k in answers.keys():
            field_list.append({"name": answers[k], "value": k, "inline": True})

        msg = await send_embed_message(
            ctx, content="You have 30 seconds to answer\n\n" + question, field_list=field_list, footer_text=f"Difficulty : {question_data['difficulty']}")

        if question_data["type"] == "boolean":
            for i in ANSWER_EMOJIS[:2]:
                await msg.add_reaction(i)
        else:
            for i in ANSWER_EMOJIS:
                await msg.add_reaction(i)

        def check(reaction, user):
            return user == ctx.message.author and reaction.message.id == msg.id

        try:
            reaction, _ = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
            correct_answer_emoji = ""
            for i in answers.keys():
                if answers[i] == question_data["correct_answer"]:
                    correct_answer_emoji = i
                    break

            if reaction.emoji == correct_answer_emoji:
                await ctx.send("CORRECT! " + ctx.message.author.mention)
                user_profile = Profile(ctx.message.author)
                await ctx.send(user_profile.event_bonus("HutCoins", 10))
            else:
                await ctx.send(
                    f"WRONG! Correct answer is {question_data['correct_answer']}")
            self.channels.remove(ctx.channel.id)
        except:
            try:
                self.channels.remove(ctx.channel.id)
            except KeyError:
                pass

def setup(bot):
    bot.add_cog(Trivia(bot))
