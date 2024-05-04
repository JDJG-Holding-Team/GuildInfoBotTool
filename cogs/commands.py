from __future__ import annotations

import io
import json
from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands
from yarl import URL

import utils

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

        params = {
            "client_id": self.bot.user.id,
            "user_id": interaction.user.id,
            "redirect_int": 0,
        }
        url = URL("http://localhost:3000/generate-url")
        full_url = url.with_query(params)

        resp = await self.bot.session.get(full_url)

        data = await resp.json()

        if not resp.ok:
            return await interaction.response.send_message(
                "An error Occured you'll need to run this again later. Dm the owner in the owner command to let them know.",
                ephemeral=True,
            )

        redirect_url = data["url"]

        view = discord.ui.View()

        view.add_item(discord.ui.Button(label="Setup", url=redirect_url, style=discord.ButtonStyle.link))

        await interaction.response.send_message(
            "Please Click on the button url to authorize oauth",
            view=view,
            ephemeral=True,
        )

    @app_commands.command(description="Sends guild data empherally", name="data")
    async def _data(self, interaction: discord.Interaction):

        if not self.bot.oauth_data.get(interaction.user.id):
            # would check to make sure rpc did not have the data if not then it would ignore it.

            return await interaction.response.send_message(
                "You have no data stored with this right now", ephemeral=True
            )

        data = self.bot.oauth_data[interaction.user.id]
        oauth_user = data["user"]

        user = self.bot.get_user(int(oauth_user["id"]))

        if user != interaction.user:

            info = await self.bot.application_info()
            owner_id = info.team.owner_id if info.team else info.owner.id
            owner = self.bot.get_user(owner_id)

            await owner.send(f"Hey boss {interaction.user} had wrong data you should check this")
            # make a webhook to send this in the info with a ping and also link to the line in the source code ie jdbot source may be helpful for this.

            return await interaction.response.send_message(
                "Someone you got the incorrect data assigned to the wrong person",
                ephemeral=True,
            )

        json_string = json.dumps(data, indent=4)
        json_response = io.StringIO(json_string)
        file = discord.File(json_response, filename="user_data.json")

        oauth_db = await utils.make_oauth_database(data)

        sqlite_file = discord.File(oauth_db, filename="data.db")
        # needs to use f.name for the location of the file.

        files = [file, sqlite_file]

        await interaction.response.send_message(
            "Here's your data(stats will be around in the future)",
            files=files,
            ephemeral=True,
        )

    @app_commands.command(description="Clears data", name="clear-data")
    async def clear_data(self, interaction: discord.Interaction):
        if not self.bot.oauth_data.get(interaction.user.id):
            return await interaction.response.send_message(
                "You have no data stored with this right now", ephemeral=True
            )

        # check db instead.

        # del self.bot.Oauth_data[interaction.user.id]
        # add some validation will not sync in till case.

        # delete db data instead.

    @app_commands.command(description="Setups up oauth but sends data only to the site", name="site-setup")
    async def site_setup(self, interaction: discord.Interaction):

        params = {
            "client_id": self.bot.user.id,
            "user_id": interaction.user.id,
            "redirect_int": 1,
        }
        url = URL("http://localhost:3000/generate-url")
        full_url = url.with_query(params)

        resp = await self.bot.session.get(full_url)

        data = await resp.json()

        if not resp.ok:
            return await interaction.response.send_message(
                "An error Occured you'll need to run this again later. Dm the owner in the owner command to let them know.",
                ephemeral=True,
            )

        redirect_url = data["url"]

        view = discord.ui.View()

        view.add_item(discord.ui.Button(label="Setup", url=redirect_url, style=discord.ButtonStyle.link))

        await interaction.response.send_message(
            "Please Click on the button url to authorize oauth",
            view=view,
            ephemeral=True,
        )

    @app_commands.command(
        description="Setups up oauth but sends stats to the site only",
        name="stats-setup",
    )
    async def stats_setup(self, interaction: discord.Interaction):

        params = {
            "client_id": self.bot.user.id,
            "user_id": interaction.user.id,
            "redirect_int": 2,
        }
        url = URL("http://localhost:3000/generate-url")
        full_url = url.with_query(params)

        resp = await self.bot.session.get(full_url)

        data = await resp.json()

        if not resp.ok:
            return await interaction.response.send_message(
                "An error Occured you'll need to run this again later. Dm the owner in the owner command to let them know.",
                ephemeral=True,
            )

        redirect_url = data["url"]

        view = discord.ui.View()

        view.add_item(discord.ui.Button(label="Setup", url=redirect_url, style=discord.ButtonStyle.link))

        await interaction.response.send_message(
            "Please Click on the button url to authorize oauth",
            view=view,
            ephemeral=True,
        )

    @app_commands.command(description="sends link to bot's source code", name="source")
    async def source(self, interaction: discord.Interaction):

        view = discord.ui.View()
        view.add_item(
            discord.ui.Button(
                label="Source",
                url="https://github.com/JDJG-Holding-Team/GuildInfoBotTool",
                style=discord.ButtonStyle.link,
            )
        )
        await interaction.response.send_message(
            "Source: https://github.com/JDJG-Holding-Team/GuildInfoBotTool", view=view
        )

    @app_commands.command(description="Gives the owner's discord information", name="owner")
    async def _owner(self, interaction: discord.Interaction):

        info = await self.bot.application_info()
        owner_id = info.team.owner_id if info.team else info.owner.id
        owner = self.bot.get_user(owner_id)

        if not owner:
            try:
                owner = await self.bot.fetch_user(user_id)

            except discord.errors.NotFound:
                return await interaction.response.send_message("Owner not found", ephemeral=True)

        await interaction.response.send_message(f"Let {owner} know that there is a problem", ephemeral=True)


async def setup(bot: GuildInfoTool):
    await bot.add_cog(Commands(bot))
