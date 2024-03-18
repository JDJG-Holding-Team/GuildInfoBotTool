import asyncio
import enum
import io
import json
import os
import random
import secrets
from threading import Thread

import aiohttp
import discord
from aiohttp import web

import utils
from utils import RedirectEnum

routes = web.RouteTableDef()

states = {}


@routes.get("/")
async def hello(request):
    return web.Response(text="Welcome Please let the bot direct you to the right spots")


@routes.get("/code")
async def code(request):

    redirect_uri = os.environ["redirect_url"]
    data = await utils.server.handle_basic_response(request, states, redirect_uri)

    if isinstance(data, web.Response):
        return data

    user_id = int(data["user"]["id"])
    # this should work ok.

    request.app["guild_data"][user_id] = data

    return web.Response(status=200, text="Grabbing guild data so you can use it in command /data")
    # will be json response in a bit or not idk.


@routes.get("/full-data")
async def full_data(request):

    redirect_uri = os.environ["website_redirect_url"]
    data = await utils.server.handle_basic_response(request, states, redirect_uri)

    if isinstance(data, web.Response):
        return data

    json_string = json.dumps(data, indent=4)
    json_response = io.StringIO(json_string)

    # also add support for the asqlite version in the future too.

    # web.FileResponse(path=json_response, status=200, )
    return web.Response(status=200, text="Stats in the future")

    # find out how to download the json and also to respond with the stats via html

    # will be json response in a bit or not idk.


@routes.get("/stats")
async def stats(request):

    redirect_uri = os.environ["stats_redirect_url"]
    data = await utils.server.handle_basic_response(request, states, redirect_uri)

    if isinstance(data, web.Response):
        return data

    # complete_collections info is all in the server.py file so, may be better if I had an object to handle everything.

    # run stat calculations on different stuff and reply with a file version within json or txt too.

    return web.Response(status=200, text="Stats in the future")


@routes.get("/generate-url")
async def generate_url(response):

    redirect_int = response.rel_url.query.get("redirect_int")
    client_id = response.rel_url.query.get("client_id")
    user_id = response.rel_url.query.get("user_id")

    if not client_id or not user_id:
        data = {"error": "Missing arguments you(need client_id and user_id)"}
        return web.json_response(data, status=400)

    state = secrets.token_urlsafe(32)

    if not redirect_int.isdigit():
        data = {"error": "Invalid integer for redirect_int"}
        return web.json_response(data, status=401)

    if not client_id.isdigit():
        data = {"error": "Invalid integer for client_id"}
        return web.json_response(data, status=401)

    if not user_id.isdigit():
        data = {"error": "Invalid integer for user_id"}
        return web.json_response(data, status=401)

    user_id = int(user_id)
    client_id = int(client_id)
    redirect_int = int(redirect_int)

    states[state] = user_id

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

    # these scopes should be the only ones I need.

    data = {"url": url}
    return web.json_response(data, status=200)


app = web.Application()
app.add_routes(routes)
