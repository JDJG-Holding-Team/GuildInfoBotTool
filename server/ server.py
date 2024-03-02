from aiohttp import web

routes = web.RouteTableDef()

@routes.get('/code/')
async def code(request):

    code = request.rel_url.query["code"]

    return web.Response(text="Grabbing guild data so you can use it in command /data")

app = web.Application()
app.add_routes(routes)
web.run_app(app, host="localhost", port=2343)