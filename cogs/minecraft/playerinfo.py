import discord
import requests
import base64
import json

from discord.ext import commands
from discord.ext.commands import *


class playerinfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(aliases=['mcplayer', 'mcuser', "mcusr"])
    async def playerinfo(self, ctx, player):
        url = f"https://api.mojang.com/users/profiles/minecraft/{player}"

        try:
            uuid = requests.get(url).json()["id"]
        except Exception:
            if requests.get(f"https://api.mojang.com/user/profiles/{player}/names"):
                uuid = player
            else:
                await ctx.reply("That username is not taken.")
                return

        url = f"https://api.mojang.com/user/profiles/{uuid}/names"

        pastnames = []

        for name in requests.get(url).json():
            try:
                pastnames.append(f"{name['name']} (<t:{int(int(name['changedToAt'])/1000)}:R>)")
            except Exception:
                try:
                    pastnames.append(f"{name['name']} (original)")
                except Exception:
                    pass

        pastnames.reverse()
        pastnames = ", \n".join(pastnames)

        if len(pastnames) > 1020:
            pastnames = pastnames[:1020] + "..."

        url = f"https://sessionserver.mojang.com/session/minecraft/profile/{uuid}"

        skincape = requests.get(url).json()["properties"][0]["value"]

        skincape = json.loads(base64.b64decode(skincape).decode("utf-8"))

        username = requests.get(url).json()["name"]

        try:
            if skincape["textures"]["SKIN"]["metadata"] == {"model": "slim"}:
                playermodel = "Alex"
            else:
                playermodel = "Steve"
        except KeyError:
            playermodel = "Steve"

        embed_desc = f"**Player name:** {username}\n**UUID:** `{uuid}`\n\n**Player model:** {playermodel}\n"

        try:
            embed_desc += f'**Cape:** [link]({skincape["textures"]["CAPE"]["url"]})'
        except KeyError:
            pass

        embed = discord.Embed(
            title=f'Minecraft user information for player "{username}"',
            description=embed_desc
        )

        try:
            embed.set_thumbnail(url=skincape["textures"]["SKIN"]["url"])
        except KeyError:
            pass

        embed.add_field(name="Name history:", value=pastnames)
        embed.set_footer(text=f"Command executed by: {ctx.author.display_name}", icon_url=ctx.author.avatar)
        await ctx.reply(embed=embed)


def setup(bot):
    bot.add_cog(playerinfo(bot))
