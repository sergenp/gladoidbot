from discord import Embed, DMChannel, File
import subprocess
import os


async def send_embed_message(ctx, content="", title="", colour=0x0080c0, thumbnail_link="", author_name="", author_icon_link="", field_list=[], title_url="", image_url = "", image_local_file=False):
    em = Embed(title=title, description=content, colour=colour, url=title_url)
    f = None
    if image_url and not image_local_file:
        em.set_image(url=image_url)
    elif image_url and image_local_file:
        f = File(image_url, filename=os.path.basename(image_url))
        em.set_image(url=f"attachment://{os.path.basename(image_url)}")
    
    em.set_thumbnail(url=thumbnail_link)
    em.set_author(name=author_name, icon_url=author_icon_link)
    if field_list:
        for k in field_list:
            em.add_field(name=k["name"], value=k["value"], inline=k["inline"])
    if isinstance(ctx, DMChannel):
        return await ctx.send(embed=em, file=f)
    
    return await ctx.message.channel.send(embed=em, file=f)
