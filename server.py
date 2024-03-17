import asyncio
import os
import random
import secrets
from threading import Thread

import discord
from aiohttp import web
from discord.http import Route

routes = web.RouteTableDef()

states = {}


@routes.get("/")
async def hello(request):
    return web.Response(text="Welcome Please let the bot direct you to the right spots")


@routes.get("/code")
async def code(request):

    _code = request.rel_url.query.get("code")
    state = request.rel_url.query.get("state")

    if not _code or not state:
        return web.Response(status=400, text="Missing arguments you(need code and state)")

    if not state in states:
        return web.Response(
            status=400,
            text="invalid state(please don't fake states or please try again)",
        )

    # send request to discord and have a way of having a bot.session to the discord bot that this calls.
    # also I need to make sure I have the user id.

    user_id = states[state]

    api_endpoint = "https://discord.com/api/v10"
    # maybe grab this from dpy?

    client_id = os.environ["client_id"]
    client_secret = os.environ["client_user"]

    session = request.app["aiohttp_session"]
    # could be done better honestly

    redirect_uri = os.environ["redirect_url"]

    data = {"grant_type": "authorization_code", "code": _code, "redirect_uri": redirect_uri}
    resp = await session.post(f"{api_endpoint}/oauth2/token", data=data, auth=(client_id, client_secret))

    if not resp.ok:
        return web.Response(status="401", text="Grabbing data failed.")

    data_response = await resp.json()

    access_token = data_response["access_token"]

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