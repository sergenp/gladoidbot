from discord import Embed, DMChannel
import subprocess


async def send_embed_message(ctx, content="", title="", colour=0x0080c0, thumbnail_link="", name="", author_icon_link="", field_list=[], title_url="", image_url = ""):
    em = Embed(title=title, description=content, colour=colour, url=title_url)
    if image_url:
        em.set_image(url=image_url)
    em.set_thumbnail(url=thumbnail_link)
    em.set_author(name=name, icon_url=author_icon_link)
    if field_list:
        for k in field_list:
            em.add_field(name=k["name"], value=k["value"], inline=k["inline"])
    if isinstance(ctx, DMChannel):
        return await ctx.send(embed=em)
    else:
        return await ctx.message.channel.send(embed=em)


def search_youtube(searchStr):
    command = f"youtube-dl -e --get-id \"ytsearch1:{searchStr}\""
    a = subprocess.check_output(
        command, shell=True).decode("utf-8").split("\n")
    try:
        return f"https://www.youtube.com/watch?v={a[1]}"
    except IndexError:
        return None
