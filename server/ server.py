import secrets
import random

from aiohttp import web

routes = web.RouteTableDef()

states = {}

@routes.get("/code/")
async def code(request):

    code = request.rel_url.query["code"]
    state = request.rel_url.query["state"]

    if not state in states:
        return web.Response(status=401, text="invalid state(please don't fake states or please try again)")
    
    # send request to discord and have a way of having a bot.session to the discord bot that this calls.

    return web.Response(status="200", text="Grabbing guild data so you can use it in command /data")

@routes.get("/generate-url/")
async def generate_url(response):
    # N = random.randint(0, 1000000)

    # N could be handled better.

    redirect_url = os.environ["redirect_url"]
    client_id = request.rel_url.query["client_id"]
    user_id = request.rel_url.query["user_id"]

    state = secrets.token_urlsafe(N)

    states[state, user_id]

    url = discord.utils.oauth_url(
    client_id,
    redirect_uri=redirect_url,
    scopes=("identify", "guilds", "connections", "guild.members.read"),
    state=state,
    )

    return web.Response(status="200", text=f"{url}")


app = web.Application()
app.add_routes(routes)
web.run_app(app, host="localhost", port=2343)
