import os
import sys
import traceback
from typing import Any, Dict, Optional

import aiohttp
import discord
from discord.ext import commands
from dotenv import load_dotenv

import server
from cogs import EXTENSIONS


class GuildInfoTool(commands.Bot):
    def __init__(self, *args: Any, **kwargs: Any) -> None:

        self.guild_data: Dict[int, dict] = {}

        super().__init__(*args, **kwargs)

    async def setup_hook(self) -> None:
        for cog in EXTENSIONS:
            try:
                await self.load_extension(f"{cog}")
            except commands.errors.ExtensionError:
                traceback.print_exc()

        self.session = aiohttp.ClientSession()

        await server.runner.setup()
        await server.site.start()

    async def close(self) -> None:
        await self.session.close()

        await server.runner.cleanup()
        await server.site.close()

        await super().close()

    async def on_error(self, event, *args: Any, **kwargs: Any) -> None:
        more_information = sys.exc_info()
        error_wanted = traceback.format_exc()
        traceback.print_exc()

        # print(event)
        # print(more_information[0])
        # print(args)
        # print(kwargs)
        # check about on_error with other repos of mine as well to update this.


if not os.getenv("TOKEN"):
    load_dotenv()

bot = GuildInfoTool(
    command_prefix=commands.when_mentioned_or("g$"),
    intents=discord.Intents.all(),
    strip_after_prefix=True,
)


@bot.event
async def on_ready():
    print(bot.user)
    print(bot.user.id)

server.app["guild_data"] = bot.guild_data
bot.run(os.environ["TOKEN"])
