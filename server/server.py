import asyncio
import enum
import os
import random
import secrets
from threading import Thread

import discord
from aiohttp import web
import aiohttp

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

    api_endpoint = discord.http.Route.BASE

    client_id = os.environ["client_id"]
    client_secret = os.environ["client_secret"]

    session = request.app["aiohttp_session"]
    # could be done better honestly

    redirect_uri = os.environ["redirect_url"]

    data = {
        "grant_type": "authorization_code",
        "code" : _code,
        "redirect_uri": redirect_uri
    }

    resp = await session.post(f"{api_endpoint}/oauth2/token", data=data, auth=aiohttp.BasicAuth(client_id, client_secret))

    if not resp.ok:
        return web.Response(status="401", text="Grabbing data failed.")
    
    data_response = await resp.json()

    access_token = data_response["access_token"]
    token_type = data_response["token_type"]

    # make sure we all get all data under ("identify", "guilds", "connections", "guilds.members.read", "connections")

    headers = {"authorization" : f"{token_type} {access_token}"}
    # not sure if that's right but it seems to match.

    resp = await session.get(f"{api_endpoint}/users/@me", headers=headers)

    if not resp.ok:
        return web.Response(status="401", text="Grabbing data failed.")

    user_data = await resp.json()

    resp = await session.get(f"{api_endpoint}/oauth2/@me", headers=headers)

    if not resp.ok:
        return web.Response(status="401", text="Grabbing data failed.")

    app_data = await resp.json()

    # https://discord.com/developers/docs/topics/oauth2#get-current-authorization-information

    # indentify?
    # maybe more data below:

    resp = await session.get(f"{api_endpoint}/users/@me/guilds?with_counts=True", headers=headers)

    if not resp.ok:
        return web.Response(status="401", text="Grabbing data failed.")

    guilds = await resp.json()

    # with_counts may be useful, guilds
    # no email is needed right?
    # I don't know if people want email stats.

    # https://discord.com/developers/docs/resources/user#get-current-user-guild-member
    # I did put something in for nickname data, tied to guild.members.read.

    resp = await session.get(f"{api_endpoint}/users/@me/connections", headers=headers)

    if not resp.ok:
        return web.Response(status="401", text="Grabbing data failed.")

    connections = await resp.json()

    # connections
    # are there more things for all the other data?

    complete_data = {}
    complete_data["user"] = user_data
    complete_data["app"] = app_data
    complete_data["guilds"] = guilds
    complete_data["connections"] = connections

    request.app["guild_data"][user_id] = complete_data

    return web.Response(status="200", text="Grabbing guild data so you can use it in command /data")
    # will be json response in a bit or not idk.


class RedirectEnum(enum.IntEnum):
    regular = 0
    website = 1
    stats = 2

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

    data = {"url": url}
    return web.json_response(data, status=200)


app = web.Application()
app.add_routes(routes)
