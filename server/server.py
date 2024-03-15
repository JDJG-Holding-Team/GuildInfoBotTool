import os
import random
import secrets
from threading import Thread

import discord
from aiohttp import web
import asyncio
import asyncio

routes = web.RouteTableDef()

states = {}

@routes.get("/")
async def hello(request):
    return web.Response(text="Welcome Please let the bot direct you to the right spots")

@routes.get("/code")
async def code(request):

    _code = request.rel_url.query.get("code")
    state = request.rel_url.query.get("state")

    print(request.rel_url.query)

    if not _code or state:
        return web.Response(status=400, text="Missing arguments you(need code and state)")

    if not state in states:
        return web.Response(
            status=400,
            text="invalid state(please don't fake states or please try again)",
        )

    # send request to discord and have a way of having a bot.session to the discord bot that this calls.
    # also I need to make sure I have the user id.

    user_id = states[state]

    # request.app["guild_data"][user_id] = data

    return web.Response(status="200", text="Grabbing guild data so you can use it in command /data")
    # will be json response in a bit or not idk.


@routes.get("/generate-url")
async def generate_url(response):

    redirect_url = os.environ["redirect_url"]
    client_id = response.rel_url.query.get("client_id")
    user_id = response.rel_url.query.get("user_id")

    if not client_id or not user_id:
        data = {"error": "Missing arguments you(need client_id and user_id)"}
        return web.json_response(data, status=400)

    state = secrets.token_urlsafe(32)

    if not client_id.isdigit():
        data = {"error": "Invalid integer for client_id"}
        return web.json_response(data, status=401)
    
    if not user_id.isdigit():
        data = {"error": "Invalid integer for user_id"}
        return web.json_response(data, status=401)
    
    user_id = int(user_id)
    client_id = int(client_id)

    states[state] = user_id

    url = discord.utils.oauth_url(
        client_id,
        redirect_uri=redirect_url,
        scopes=("identify", "guilds", "connections", "guilds.members.read", "connections"),
        state=state,
    )

    data = {"url": url}
    return web.json_response(data, status=200)


app = web.Application()
app.add_routes(routes)
