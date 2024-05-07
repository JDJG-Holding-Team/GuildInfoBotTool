import enum
import tempfile

import asyncpg
import asqlite
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

    # guild count with specific types in the future.


async def make_oauth_database(oauth_data: dict):
    # also add support for the asqlite version in the future too.

    with tempfile.NamedTemporaryFile(mode="w") as f:
        # delete on close may be already used
        # delete is necessary possibly but idk, I just know delete_on_close=True isn't in python 3.11
        # is delete needed?
        # appraently it's also autodeleted
        # https://stackoverflow.com/questions/11043372/how-to-use-tempfile-namedtemporaryfile
        # https://docs.python.org/3/library/tempfile.html#tempfile.NamedTemporaryFile

        # does f even work with it?

        async with asqlite.connect(f.name) as conn:
            async with conn.cursor() as cursor:
                print(conn)
                # could get the names of the colonums and make them their own tables and make json be a text type?

    return f.name
    # all you need appreantly.


class CustomRecordClass(asyncpg.Record):
    def __getattr__(self, name: str) -> Any:
        if name in self.keys():
            return self[name]
        return super().__getattr__(name)
