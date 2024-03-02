import os
import traceback

import aiohttp
import discord

from discord.ext import commands
from dotenv import load_dotenv

class GuildInfoTool(commands.Bot):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

async def setup_hook(self) -> None:
    for cog in EXTENSIONS:
        try:
            await self.load_extension(f"{cog}")
        except commands.errors.ExtensionError:
            traceback.print_exc()


load_dotenv()

bot = GuildInfoTool(command_prefix=commands.when_mentioned_or("g$"), intents=discord.Intents.all(), strip_after_prefix=True)

@bot.event
async def on_ready():
    print(bot.user)
    print(bot.user.id)


bot.run(os.environ["TOKEN"])