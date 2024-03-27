import typing

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse


app = FastAPI()

# will need to be ran properly through awaitable method or ipc.

@app.get("/", response_class=PlainTextResponse)
async def main():
    return "Welcome Please let the bot direct you to the right spots"


@app.get("/code")
async def _code(code: typing.Optional[str] = None, state: typing.Optional[str] = None):
    print(code, state)

    # look to see if this works.



