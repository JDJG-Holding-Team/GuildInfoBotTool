import enum

import discord


class RedirectEnum(enum.IntEnum):
    regular = 0
    website = 1
    stats = 2


def stats_builder(data: dict):

    user = data["user"]
    app_data = data["app"]
    # unsure if I will need app_data for this.

    guilds = data["guilds"]
    # this I can make stats like this without having to rely on their work:
    # to replace https://discordtools.io/guildcount
    # https://dinfo.fumple.pl/
    # https://discordlookup.com/guildlist
    # https://discordlookup.com/experiments

    connections = data["connections"]
    # unknown for connection stats.
    nicknames = data["nicknames"]
