import asyncio
import io
import json
import os
import secrets
from contextlib import asynccontextmanager
from typing import Any, Dict, Optional, Union

import aiohttp
import asyncpg
import discord
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse, ORJSONResponse, PlainTextResponse

import utils
from utils import RedirectEnum


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with (
        aiohttp.ClientSession() as app.state.session,
        asyncpg.create_pool(os.getenv("PSQL_URL"), record_class=utils.CustomRecordClass) as db,
    ):
        app.state.db = db
        app.state.states = {}

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

    redirect_uri = os.environ["redirect_url"]

    if not code or not state:
        return PlainTextResponse("Missing arguments you(need code and state)", status_code=401)

    data = await utils.server.handle_grab_token(app, code, state, redirect_uri)
    # possibly better way to pass app but idk what.

    if isinstance(data, str):
        return PlainTextResponse(data, status_code=401)

    user_id = data["user"]["id"]
    result = await app.state.db.fetchrow("SELECT * FROM OAUTH_TOKENS WHERE user_id = $1", user_id)

    # wait .......
    # I am dumb lol
    # I need to re-do this.

    access_token = data["token"]["access_token"]
    refresh_token = data["token"]["refresh_token"]

    if result:
        await app.state.db.execute(
            "UPDATE OAUTH_TOKENS SET ACCESS_TOKEN = $1 and REFRESH_TOKEN = $2 WHERE user_id = ($3)",
            access_token,
            refresh_token,
            user_id,
        )

    return PlainTextResponse("Grabbing guild data so you can use it in command /data")


@app.get("/full-data")
async def full_data(response: Response, code: Optional[str] = None, state: Optional[str] = None):

    # possibly better way to get app maybe https://fastapi.tiangolo.com/reference/request/#fastapi.Request
    # would this allow me to have my own session with the local broswer to request for nickname data.

    redirect_uri = os.environ["website_redirect_url"]

    if not code or not state:
        return PlainTextResponse("Missing arguments you(need code and state)", status_code=401)

    data = await utils.server.handle_basic_response(app, code, state, redirect_uri)

    if isinstance(data, str):
        return PlainTextResponse(data, status_code=401)

    json_string = json.dumps(data, indent=4)
    json_response = io.StringIO(json_string)

    oauth_db = await utils.make_oauth_database(data)

    """
    key_validation = secrets.token_urlsafe(32)
    user_id = int(data["user"]["id"])
    # validated earlier

    record = await app.state.db.fetchrow("SELECT * FROM VALIDATION_KEYS SELECT user_id = $1", user_id)
    if not record:
        await app.state.db.execute("INSERT INTO VALIDATION_KEYS VAULUES($1, $2)", user_id, key_validation)
        # how do I make this encypted

        response.set_cookie(key="validation_key", value=key_validation)

    # re-use cookie I suppose?

    # will need to be added to database as encypted.
    # prevents people from downloading wrong data.
    """
    # not used code right now

    """
    can also be used for bot stuff and for later if this is moved.
    file support
    find out how to download the json and also to respond with the stats via html

    will be json response in a bit or not idk.

    html responses with download html attribute
    le pain.

    processing takes way too long too.
    """

    html = """
    <pre>
    { "nice": "stats" }
    </pre>
    <a href="download_link.json" download>Download as JSON</a>
    <a href="download_link.sqlite" download>Download as SQLite</a>
    """
    # suggested solution from python.
    # write actual stats there soon

    return HTMLResponse(content=html)
    # does not work appreantly.


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
    client_id: Optional[int] = None,
    user_id: Optional[int] = None,
    redirect_int: Optional[int] = None,
):
    if not client_id or not user_id or not redirect_int:

        data = {"error": "Please provide a valid integer for (client_id, user_id, and redirect_int)"}
        return ORJSONResponse(data, status_code=401)

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
    # unused guild.members.read for now will be using it in a different method (if it comes back).

    return {"url": url}


if not os.getenv("PSQL_URL"):
    load_dotenv()
    # only gunatrees data is loaded properly
    # using systemd is better to load up.


async def main():
    config = uvicorn.Config("server:app", port=3000, log_level="debug")
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    try:
        asyncio.run(main())

    except KeyboardInterrupt as e:
        pass


# may also run in the command line idk yet
