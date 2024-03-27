import io
import json
import os
import secrets


from fastapi import FastAPI
from fastapi.responses import PlainTextResponse, ORJSONResponse


app = FastAPI()
app.state.states = {}
# will need to be ran properly through awaitable method or ipc.


@app.get("/", response_class=PlainTextResponse)
async def main():
    return "Welcome Please let the bot direct you to the right spots"


@app.get("/code", response_class=PlainTextResponse)
async def _code(code: typing.Optional[str] = None, state: typing.Optional[str] = None):
    print(code, state)

    redirect_uri = os.environ["redirect_url"]

    if not code or state:
        return PlainTextResponse("Missing arguments you(need code and state)", status_code=401)

    # should be utiling it soon with server_rewrite once all is cleaned up server.py will be deleted and will use the new one.


@routes.get("/full-data")
async def full_data(code: typing.Optional[str] = None, state: typing.Optional[str] = None):
    print(code, state)

    redirect_uri = os.environ["website_redirect_url"]

    if not code or state:
        return PlainTextResponse("Missing arguments you(need code and state)", status_code=401)

    # should be utiling it soon with server_rewrite once all is cleaned up server.py will be deleted and will use the new one.


@routes.get("/stats")
async def stats(request):

    redirect_uri = os.environ["stats_redirect_url"]

    if not code or state:
        return PlainTextResponse("Missing arguments you(need code and state)", status_code=401)

    # should be utiling it soon with server_rewrite once all is cleaned up server.py will be deleted and will use the new one.


@routes.get("/generate-url", response_class=ORJSONResponse)
async def generate_url(
    client_id: typing.Optional[typing.Union[int, str]] = None,
    user_id: typing.Optional[typing.Union[int, str]] = None,
    redirect_int: typing.Optional[typing.Union[int, str]] = None,
):

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
