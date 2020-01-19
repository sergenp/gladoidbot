from discord import Embed
import subprocess


async def send_embed_message(ctx, content="", title="", colour=0x0080c0, link="", name="", ikon_link=""):
    em = Embed(title=title, description=content, colour=colour)
    em.set_thumbnail(url=link)
    em.set_author(name=name, icon_url=ikon_link)
    return await ctx.message.channel.send(embed=em)


def search_youtube(searchStr):
    command = f"youtube-dl -e --get-id \"ytsearch1:{searchStr}\""
    a = subprocess.check_output(
        command, shell=True).decode("utf-8").split("\n")
    try:
        return f"https://www.youtube.com/watch?v={a[1]}"
    except IndexError:
        return None
