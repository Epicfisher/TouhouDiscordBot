import commands

###

import bot
from time import time
from random import randint

def get_ping_message():
    if randint(0, 99) == 0:
        return "...Wha? Oh, Pong!"

    if int(24 - (((time() - bot.startTime) / 60) / 60)) <= 2:
        return "Yaawn... Oh! Pong!"

    if bot.season == "christmas":
        return "Jingle, jingle! Oh, uh, Pong!"
    if bot.season == "halloween":
        return "Who's there?! Oh, it's just you. Pong!"
    if bot.season == "new year":
        return "Pong, pong! Happy new year!"

    return "Pong!"

async def ping(message):
    await message.channel.send(get_ping_message())
    return

###

commands.Add("ping", ping)
