import aiohttp
import discord


async def grab_oauth_data(
    session: aiohttp.ClientSession,
    access_token: str,
    refresh_token: str,
    user_id: str,
):

    api_endpoint = discord.http.Route.BASE
    client_id = os.environ["client_id"]
    client_secret = os.environ["client_secret"]
    token_type = "Bearer"
    # should be enough

    headers = {"authorization": f"{token_type} {access_token}"}
    # not sure if that's right but it seems to match.
    resp = await session.get(f"{api_endpoint}/users/@me", headers=headers)

    if not resp.ok:

        # https://discord.com/developers/docs/topics/oauth2#authorization-code-grant-refresh-token-exchange-example

        # Refreshs token

        data = {"grant_type": "refresh_token", "refresh_token": refresh_token}
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        resp = await session.post(
            f"{api_endpoint}/oauth2/token",
            data=data,
            auth=aiohttp.BasicAuth(client_id, client_secret),
        )

        if not resp.ok:
            return "Refresh Token Failed you will need to redo the oauth."

        data_response = await resp.json()
        access_token = data_response["access_token"]
        token_type = data_response["token_type"]

    headers = {"authorization": f"{token_type} {access_token}"}
    # not sure if that's right but it seems to match.
    resp = await session.get(f"{api_endpoint}/users/@me", headers=headers)

    if not resp.ok:
        return "Grabbing user data failed"

    user_data = await resp.json()
    user_data_id = int(user_data.get("id"))
    # I hate grabbing the data like this.

    if user_data_id != user_id:
        return "Mismatched user_id data. Something fishy is going on here."
        # could I possibly put a warning in here and then update the state data, idk?
        # wouldn't code be weird though ?

    resp = await session.get(f"{api_endpoint}/oauth2/@me", headers=headers)

    if not resp.ok:
        return "Grabbing data failed with getting oauth app data."

    app_data = await resp.json()

    resp = await session.get(f"{api_endpoint}/users/@me/guilds?with_counts=True", headers=headers)

    if not resp.ok:
        return "Grabbing data failed with guilds."

    guilds = await resp.json()

    resp = await session.get(f"{api_endpoint}/users/@me/connections", headers=headers)

    if not resp.ok:
        return "Grabbing data failed with connections."

    connections = await resp.json()

    complete_data = {
        "user": user_data,
        "app": app_data,
        "guilds": guilds,
        "connections": connections,
    }

    return complete_data
    # might be worth making this be ran onto an object(typedDict)
