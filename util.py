from discord import Embed

async def send_embed_message(ctx, content = "", title = "", colour = 0x0080c0, link = "", name = "", ikon_link = ""):
        em = Embed(title=title, description=content, colour=colour)
        em.set_thumbnail(url=link)
        em.set_author(name=name, icon_url=ikon_link)
        await ctx.message.channel.send(embed=em)

