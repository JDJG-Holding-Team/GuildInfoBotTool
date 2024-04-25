import asyncio
import enum
import tempfile

import asqlite
import discord
import zmq


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

# server methods for zmq bot
# server should use port (localhost:5554)
# remove comment from the server file once you start coding this here

# bot methods under this
# pyzmq localhost server: 5555(remove the port comment from main.py when done.)

# this may work okay?