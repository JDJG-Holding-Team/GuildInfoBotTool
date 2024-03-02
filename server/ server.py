from aiohttp import web

routes = web.RouteTableDef()


@routes.get("/code/")
async def code(request):

    code = request.rel_url.query["code"]
    state = request.rel_url.query["state"]

    if not state in states:
        return web.Response(status=401, text="invalid state(please don't fake states or please try again)")
    
    # send request to discord and have a way of having a bot.session to the discord bot that this calls.

    return web.Response(status="200", text="Grabbing guild data so you can use it in command /data")


app = web.Application()
app.add_routes(routes)
web.run_app(app, host="localhost", port=2343)
