import io
import json
import os
import secrets
import typing
from typing import Dict
from contextlib import asynccontextmanager

import aiohttp
import asqlite
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
async def _code(code: typing.Optional[str] = None, state: typing.Optional[str] = None):
    print(code, state)

    redirect_uri = os.environ["redirect_url"]

    if not code or not state:
        return PlainTextResponse(text="Missing arguments you(need code and state)", status_code=401)

    data = await utils.server.handle_basic_response(app, code, state, redirect_uri)
    # possibly better way to pass app but idk what.

    if isinstance(data, str):
        return PlainTextResponse(text=data, status_code=401)

    user_id = int(data["user"]["id"])
    # this should work ok.

    app.state.guild_data[user_id] = data

    return PlainTextResponse(status=200, text="Grabbing guild data so you can use it in command /data")


@app.get("/full-data")
async def full_data(code: typing.Optional[str] = None, state: typing.Optional[str] = None):
    print(code, state)

    redirect_uri = os.environ["website_redirect_url"]

    if not code or not state:
        return PlainTextResponse(text="Missing arguments you(need code and state)", status_code=401)

    data = await utils.server.handle_basic_response(app, code, state, redirect_uri)

    if isinstance(data, str):
        return PlainTextResponse(text=data, status_code=401)

    json_string = json.dumps(data, indent=4)
    json_response = io.StringIO(json_string)

    # also add support for the asqlite version in the future too.

    # web.FileResponse(path=json_response, status=200, )

    # find out how to download the json and also to respond with the stats via html

    # will be json response in a bit or not idk.

    return PlainTextResponse(status=200, text="Stats in the future")


@app.get("/stats")
async def stats():

    redirect_uri = os.environ["stats_redirect_url"]

    if not code or not state:
        return PlainTextResponse(text="Missing arguments you(need code and state)", status_code=401)

    data = await utils.server.handle_basic_response(app, code, state, redirect_uri)

    if isinstance(data, str):
        return PlainTextResponse(text=data, status_code=401)

    return PlainTextResponse(status=200, text="Stats in the future")

    # complete_collections info is all in the server.py file so, may be better if I had an object to handle everything.

    # run stat calculations on different stuff and reply with a file version within json or txt too.
    # although stats should report name information I do not remeber what this file says.


@app.get("/generate-url", response_class=ORJSONResponse)
async def generate_url(
    client_id: typing.Optional[typing.Union[int, str]] = None,
    user_id: typing.Optional[typing.Union[int, str]] = None,
    redirect_int: typing.Optional[typing.Union[int, str]] = None,
):
    
    print(type(client_id), type(user_id))
    if not client_id or not user_id:
        return ORJSONResponse({"error": "Missing arguments(client_id or user_id)"}, status_code=401)

    if isinstance(client_id, str) or isinstance(user_id, str) or isinstance(user_id, str):
        return ORJSONResponse({"error": "Non int variables being used."}, status_code=401)

    # should all be pythonic
    # should already be int

    # pass something to the .stats variable somehow.

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
