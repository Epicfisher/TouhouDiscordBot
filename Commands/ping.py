import commands

###

from random import randint

import bot

def get_ping_message():
    if bot.season == "christmas":
        return "Jingle, jingle! Oh, uh, Pong!"
    if bot.season == "halloween":
        return "Who's there?! Oh, it's just you. Pong!"

    return "Pong!"

async def ping(message):
    if randint(0, 99) == 0:
        await message.channel.send("...Wha? Oh, Pong!")
    else:
        await message.channel.send(get_ping_message())
    return

###

commands.Add("ping", ping)
