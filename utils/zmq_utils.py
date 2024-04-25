import asyncio
import json

import zmq
from zmq.asyncio import Context, Poller

# server methods for zmq bot
# server should use port (localhost:5554)
# remove comment from the server file once you start coding this here

# bot methods under this
# pyzmq localhost bot: 5555(remove the port comment from main.py when done.)

server_url = "tcp://127.0.0.1:5554"
bot_url = "tcp://127.0.0.1:5555"


# needs a new file name and name change in utils(ie import change) when done
# this may work okay?

ctx = Context.instance()


async def ping() -> None:
    """print dots to indicate idleness"""
    while True:
        await asyncio.sleep(0.5)
        print("....")
        # does it need to always print dots?


async def bot_receiver():
    """receive messages with polling"""
    pull = ctx.socket(zmq.PULL)
    pull.connect(bot_url)
    poller = Poller()
    poller.register(pull, zmq.POLLIN)
    while True:
        events = await poller.poll()
        if pull in dict(events):
            print("recving", events)
            msg = await pull.recv_multipart()
            print("recvd", msg)


async def bot_sender(user_id: int) -> None:
    "sends messages from the bot"
    push = ctx.socket(zmq.PUSH)
    push.bind(server_url)

    data_request = json.dumps({"user_id": user_id})
    await push.send_multipart(data_request)
    # or does push.send_string work better?


async def server_receiver():
    """receive messages with polling"""
    pull = ctx.socket(zmq.PULL)
    pull.connect(server_url)
    poller = Poller()
    poller.register(pull, zmq.POLLIN)
    while True:
        events = await poller.poll()
        if pull in dict(events):
            print("recving", events)
            msg = await pull.recv_multipart()
            print("recvd", msg)


async def server_sender(user_id: int) -> None:
    "sends messages from the server"
    push = ctx.socket(zmq.PUSH)
    push.bind(bot_url)

    data_request = json.dumps({"data": data, "user_id": user_id})
    await push.send_multipart(data_request)
    # or does push.send_string work better?


# check this: https://github.com/JDJG-Holding-Team/GuildInfoBotTool/commit/4e29e602251f463276b3df9ef3f98bd9536a432e#commitcomment-141348897
