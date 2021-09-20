import discord
from discord.ext import commands
from discord import FFmpegPCMAudio
from youtube_dl import YoutubeDL


class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.original_queue = []
        self.queue = []
        self.playing = False
        self.voice_client = None

    @commands.command()
    async def join(self, ctx):
        channel = ctx.author.voice.channel
        await channel.connect()

    @commands.command()
    async def leave(self, ctx):
        await ctx.voice_client.disconnect()

    async def play_next(self, error):
        self.playing = False
        if self.voice_client:
            if self.voice_client.is_playing:
                self.voice_client.stop()
            await self.play_current_song_in_queue()

    @commands.command()
    async def next(self, ctx):
        await self.play_next(None)

    @commands.command()
    async def stop(self, ctx):
        self.playing = False
        self.voice_client = None
        ctx.voice_client.stop()

    @commands.command()
    async def play(self, ctx, *, url: str):
        try:
            voice = ctx.author.voice.channel
            await voice.connect()
        except discord.ClientException:
            pass

        self.queue.append(url)
        self.original_queue.append(url)
        await ctx.send(f"Added `{url}` to the queue")
        queue_str = "Current queue:\n"
        for index, link in enumerate(self.original_queue):
            queue_str += f"`{index}<<<--->>>{link}`\n"

        await ctx.send(queue_str)

        if not self.playing:
            if self.voice_client is None:
                self.voice_client = ctx.voice_client
            await self.play_current_song_in_queue()

    async def play_current_song_in_queue(self):
        if len(self.queue) > 0:
            YDL_OPTIONS = {
                "format": "bestaudio",
                "noplaylist": "True",
                "default_search": "auto",
            }
            FFMPEG_OPTIONS = {
                "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
                "options": "-vn",
            }
            now_playing = self.queue.pop()
            with YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(now_playing, download=False)

            try:
                URL = info["entries"][0]["formats"][0]["url"]
            except KeyError:
                URL = info["formats"][0]["url"]
            self.voice_client.play(
                FFmpegPCMAudio(URL, **FFMPEG_OPTIONS), after=self.play_next
            )
            self.playing = True


def setup(bot):
    bot.add_cog(Music(bot))
