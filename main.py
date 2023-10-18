import os

import aiohttp
import discord

from discord.ext import commands


from dotenv import load_dotenv

class GuildInfoTool(commands.Bot):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

bot = GuildInfoTool(command_prefix=commands.when_mentioned_or("g$"), intents=discord.Intents.all(), strip_after_prefix=True)

@bot.event
async def on_ready():
    print(bot.user)
    print(bot.user.id)

load_dotenv()
bot.run(os.environ["TOKEN"])