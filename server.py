import asyncio
import io
import json
import os
import secrets
import tempfile
from contextlib import asynccontextmanager
from typing import Dict, Optional, Union

import aiohttp
import asqlite
import discord
import zmq
import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse, PlainTextResponse

import utils
from utils import RedirectEnum


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with aiohttp.ClientSession() as app.state.session:
        app.state.states = {}
        guild_data: Dict[int, dict] = {}
        app.state.guild_data = guild_data
        # just easier to create the stats does not need to be awaited.
        yield  # probaly closes when it is done.
        print("clean aiohttp session")


app = FastAPI(lifespan=lifespan)
# will need to be ran properly through awaitable method or ipc.


@app.get("/", response_class=PlainTextResponse)
async def main():
    return "Welcome Please let the bot direct you to the right spots"


@app.get("/code", response_class=PlainTextResponse)
async def _code(code: Optional[str] = None, state: Optional[str] = None):
    print(code, state)

    redirect_uri = os.environ["redirect_url"]

    if not code or not state:
        return PlainTextResponse("Missing arguments you(need code and state)", status_code=401)

    data = await utils.server.handle_basic_response(app, code, state, redirect_uri)
    # possibly better way to pass app but idk what.

    if isinstance(data, str):
        return PlainTextResponse(data, status_code=401)

    user_id = int(data["user"]["id"])
    # this should work ok.

    app.state.guild_data[user_id] = data

    return PlainTextResponse("Grabbing guild data so you can use it in command /data")


@app.get("/full-data")
async def full_data(code: Optional[str] = None, state: Optional[str] = None):
    print(code, state)

    redirect_uri = os.environ["website_redirect_url"]

    if not code or not state:
        return PlainTextResponse("Missing arguments you(need code and state)", status_code=401)

    data = await utils.server.handle_basic_response(app, code, state, redirect_uri)

    if isinstance(data, str):
        return PlainTextResponse(data, status_code=401)

    json_string = json.dumps(data, indent=4)
    json_response = io.StringIO(json_string)

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

        # unsure how to handle the json response right now will ask dpy for help for that.

    # file support

    # find out how to download the json and also to respond with the stats via html

    # will be json response in a bit or not idk.

    return PlainTextResponse("Stats in the future")
    # html responses with download html attribute
    # le pain.

    """
    <pre>
    { "nice": "stats" }
    </pre>
    <a href="download_link.json" download>Download as JSON</a>
    <a href="download_link.sqlite" download>Download as SQLite</a>
    """
    # suggested solution from python.


@app.get("/stats")
async def stats(code: Optional[str] = None, state: Optional[str] = None):

    redirect_uri = os.environ["stats_redirect_url"]

    if not code or not state:
        return PlainTextResponse("Missing arguments you(need code and state)", status_code=401)

    data = await utils.server.handle_basic_response(app, code, state, redirect_uri)

    if isinstance(data, str):
        return PlainTextResponse(data, status_code=401)

    return PlainTextResponse("Stats in the future")

    # complete_collections info is all in the server.py file so, may be better if I had an object to handle everything.

    # run stat calculations on different stuff and reply with a file version within json or txt too.
    # although stats should report name information I do not remeber what this file says.


@app.get("/generate-url", response_class=ORJSONResponse)
async def generate_url(
    client_id: int,
    user_id: int,
    redirect_int: int,
):

    state = secrets.token_urlsafe(32)
    app.state.states[state] = user_id

    redirect_enum = RedirectEnum(redirect_int)

    match redirect_enum:
        case RedirectEnum.regular:
            redirect_url = os.environ["redirect_url"]

        case RedirectEnum.website:
            redirect_url = os.environ["website_redirect_url"]

        case RedirectEnum.stats:
            redirect_url = os.environ["stats_redirect_url"]

    # this looks kind of funky ngl

    url = discord.utils.oauth_url(
        client_id,
        redirect_uri=redirect_url,
        scopes=("identify", "connections", "guilds", "guilds.members.read"),
        state=state,
    )

    return {"url": url}


async def main():
    config = uvicorn.Config("server:app", port=3000, log_level="debug")
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    try:
        asyncio.run(main())

    except KeyboardInterrupt as e:
        print("Closed the program thank you for using it:)")
        

# may also run in the command line idk yet
