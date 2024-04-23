import asyncio
import os

import aiohttp
import discord
from aiohttp import web
from fastapi import FastAPI


async def grab_nickname_data(guild, session: aiohttp.ClientSession, api_endpoint: str, headers: dict):
    # object type for guild may make this easier, to make guild_id to guild.id
    # guild.id may be better.
    guild_id = guild["id"]
    resp = await session.get(f"{api_endpoint}/users/@me/guilds/{guild_id}/member", headers=headers)

    guild_info = await resp.json()

    retry_seconds = 0.0
    if not resp.ok:
        retry_seconds = guild_info.get("retry_after")

        if not retry_seconds:
            return "Retry after doesn't exist."

        return retry_seconds

    return guild_info


async def handle_basic_response(app: FastAPI, code: str, state: str, redirect_uri: str):

    states = app.state.states
    if not state in states:
        return "Invalid state(please don't fake states or please try again)"
        # make sure to check what was returned on the other end.

    # prevents fake sessions abusing our calls

    user_id = states[state]
    api_endpoint = discord.http.Route.BASE
    client_id = os.environ["client_id"]
    client_secret = os.environ["client_secret"]
    session = app.state.session

    # this is basically the same way as long

    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
    }
    # needs cleaning up

    resp = await session.post(
        f"{api_endpoint}/oauth2/token",
        data=data,
        auth=aiohttp.BasicAuth(client_id, client_secret),
    )

    if not resp.ok:
        return "Grabbing data failed."

    data_response = await resp.json()
    access_token = data_response["access_token"]
    token_type = data_response["token_type"]

    # make sure we all get all data under ("identify", "guilds", "connections", "guilds.members.read", "connections")

    headers = {"authorization": f"{token_type} {access_token}"}
    # not sure if that's right but it seems to match.
    resp = await session.get(f"{api_endpoint}/users/@me", headers=headers)

    if not resp.ok:
        return "Grabbing data failed."

    user_data = await resp.json()
    user_data_id = int(user_data.get("id"))
    # I hate grabbing the data like this.

    if user_data_id != user_id:
        return "Mismatched user_id data. Something fishy is going on here."
        # could I possibly put a warning in here and then update the state data, idk?

    resp = await session.get(f"{api_endpoint}/oauth2/@me", headers=headers)

    if not resp.ok:
        return "Grabbing data failed."

    app_data = await resp.json()

    # https://discord.com/developers/docs/topics/oauth2#get-current-authorization-information

    # indentify?
    # maybe more data below:

    resp = await session.get(f"{api_endpoint}/users/@me/guilds?with_counts=True", headers=headers)

    if not resp.ok:
        return "Grabbing data failed."

    guilds = await resp.json()

    nicknames = {}
    # this loop is a terrible way to grab it(It may be better to remove it)
    for guild in guilds:

        guild_id = guild["id"]
        guild_info = await grab_nickname_data(guild, session, api_endpoint, headers)

        if isinstance(guild_info, web.Response):
            return guild_info

        if not isinstance(guild_info, float) and not isinstance(guild_info, dict):
            return "Something went wrong with retrying fetching."

        if isinstance(guild_info, float):
            retry_seconds = guild_info

            if retry_seconds:
                if retry_seconds > 10:
                    guild_info = {
                        "error": f"fetching data with {guild_id}",
                        "fetch_time": retry_seconds,
                    }

                else:
                    await asyncio.sleep(retry_seconds)
                    # I should break out of it

                    if retry_seconds > 30:
                        break  # break out of loop

                    guild_info = await grab_nickname_data(guild, session, api_endpoint, headers)
            # should run only when more than 0 seconds.
            # I should probaly not use this rn and find a way to be able to grab all without having the server timeout.

        nicknames[guild_id] = guild_info

    # https://discord.com/developers/docs/resources/user#get-current-user-guild-member
    # I did put something in for nickname data, tied to guild.members.read.

    resp = await session.get(f"{api_endpoint}/users/@me/connections", headers=headers)

    if not resp.ok:
        return "Grabbing data failed."

    connections = await resp.json()

    # connections
    # are there more things for all the other data?

    complete_data = {
        "user": user_data,
        "app": app_data,
        "guilds": guilds,
        "connections": connections,
        "nicknames": nicknames,
    }

    """
    complete_data = {}
    complete_data["user"] = user_data
    complete_data["app"] = app_data
    complete_data["guilds"] = guilds
    complete_data["connections"] = connections
    complete_data["nicknames"] = nicknames
    """
    # old code the new one is better.

    return complete_data
