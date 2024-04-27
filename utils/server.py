import asyncio
import os

import aiohttp
import discord
from aiohttp import web
from fastapi import FastAPI


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
    # guild.members.read will come back if nickname is runnable on the broswer.

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
        # wouldn't code be weird though ?

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
    }

    """
    complete_data = {}
    complete_data["user"] = user_data
    complete_data["app"] = app_data
    complete_data["guilds"] = guilds
    complete_data["connections"] = connections
    """
    # old code the new one is better.
    # re-add nicknames if we get a new method.

    return complete_data


async def handle_grab_token(app: FastAPI, code: str, state: str, redirect_uri: str):

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

    resp = await session.post(
        f"{api_endpoint}/oauth2/token",
        data=data,
        auth=aiohttp.BasicAuth(client_id, client_secret),
    )

    if not resp.ok:
        return "Grabbing data failed."

    token_data = await resp.json()

    headers = {"authorization": f"{token_type} {access_token}"}
    # not sure if that's right but it seems to match.
    resp = await session.get(f"{api_endpoint}/users/@me", headers=headers)

    if not resp.ok:
        return "Grabbing data failed."

    user_data = await resp.json()

    if not user_data.get("id"):
        return "How do you not have an user id?"

    complete_data = {
        "token": token_data,
        "user": user_data,
    }

    return complete_data
