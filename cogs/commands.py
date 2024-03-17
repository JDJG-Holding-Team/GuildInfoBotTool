from __future__ import annotations

import io
import random
import json
from typing import TYPE_CHECKING

import asqlite
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
        url = URL("http://localhost:3000/generate-url")
        full_url = url.with_query(params)

        resp = await self.bot.session.get(full_url)
        
        data = await resp.json()

        redirect_url = data["url"]

        view = discord.ui.View()

        view.add_item(discord.ui.Button(label=f"Setup", url=redirect_url, style=discord.ButtonStyle.link))

        await interaction.response.send_message("Please Click on the button url to authorize oauth", view=view)

    @app_commands.command(description="Sends guild data empherally", name="data")
    async def data(self, interaction: discord.Interaction):

        if not self.bot.guild_data.get(interaction.user.id):
            return await interaction.response.send_message("You have no data stored with this right now")

        data = self.bot.guild_data[interaction.user.id]
        oauth_user = data["user"]

        user = self.bot.get_user(int(oauth_user["id"]))

        if user != interaction.user:

            info = await self.bot.application_info()
            owner_id = info.team.owner_id if info.team else info.owner.id
            owner = self.bot.get_user(owner_id)

            await owner.send(f"Hey boss {interaction.user} had wrong data you should check this")
            # make a webhook to send this in the info with a ping and also link to the line in the source code ie jdbot source may be helpful for this.

            return await interaction.response.send_message("Someone you got the incorrect data assigned to the wrong person")
        
        json_string = json.dumps(data, indent=4)
        json_response = io.StringIO(json_string)
        file = discord.File(json_response, filename="user_data.json")

        with tempfile.NamedTemporaryFile(mode="w", delete_on_close=True) as f:
            # delete on close may be already used
            # is delete needed?
            # appraently it's also autodeleted
            # https://stackoverflow.com/questions/11043372/how-to-use-tempfile-namedtemporaryfile
            # https://docs.python.org/3/library/tempfile.html#tempfile.NamedTemporaryFile

            # does f even work with it?

            async with asqlite.connect(f) as conn:
                async with conn.cursor() as cursor:
                    print(conn)

                # I am unsure about what tables in execute right now.

        await interaction.response.send_message("Here's your data(stats will be around in the future)", files=[file, sqlite_file], ephemeral=True)

    @app_commands.command(description="Clears data", name="clear-data")
    async def clear_data(self, interaction: discord.Interaction):
        if not self.bot.guild_data.get(interaction.user.id):
            return await interaction.response.send_message("You have no data stored with this right now")
        
        del self.bot.guild_data[interaction.user.id]
        # add some validation will not sync in till case.


async def setup(bot: GuildInfoTool):
    await bot.add_cog(Commands(bot))
