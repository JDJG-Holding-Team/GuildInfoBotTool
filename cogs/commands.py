from __future__ import annotations

import random
from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands
from yarl import URL

if TYPE_CHECKING:
    from main import GuildInfoTool


class Commands(commands.Cog):
    "Commands for the Bot (temp name for now)"

    def __init__(self, bot: GuildInfoTool):
        self.bot: GuildInfoTool = bot

    async def cog_load(self):
        print("cog loaded")

    async def cog_unload(self):
        print("cog unloaded")

    @app_commands.command(description="Setups up oauth", name="setup")
    async def _setup(self, interaction: discord.Interaction):

        params = {"client_id": self.bot.user.id, "user_id": interaction.user.id}
        url = URL("http://localhost:2343/generate-url/")
        full_url = url.with_query(params)

        resp = await self.bot.session.get(full_url)
        data = await resp.json()

        redirect_url = data["url"]

        view = discord.ui.View()

        view.add_item(discord.ui.Button(label=f"Setup", url=redirect_url, style=discord.ButtonStyle.link))

        await interaction.response.send_message("Please Click on the button url to authorize oauth", view=view)

    @app_commands.command(description="Sends guild data empherally", name="data")
    async def data(self, interaction: discord.Interaction):

        await interaction.response.send_message("Wip right now", ephemeral=True)


async def setup(bot: GuildInfoTool):
    await bot.add_cog(Commands(bot))
