from aiohttp import web

async def handle_basic_response(request : web.Request, ):
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

    