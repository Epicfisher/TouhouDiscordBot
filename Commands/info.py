import commands

###

import bot
from datetime import datetime
from time import time
from random import randint
import discord

'''
aboutMessage = """```asciidoc
= About Patchouli Knowledge =

"%s"

> Runs entirely in Python 3, with the use of discord.py %s. ::
> So far I have stayed up reading for %s minutes. ::
> I currently understand %s commands. ::
> I'm currently loaning my books to %s servers. ::
> I'm currently playing music for %s servers. ::

> I'm open source! git.io/vpSEv ::

> Made by @Epicfisher#6763 :: \u200B
```"""
'''

aboutMessage = """```asciidoc
= About Patchouli Knowledge =

"%s"

- Runs entirely in Python 3, with the use of discord.py %s.
- So far I have stayed up reading for %s minutes.
- I currently understand %s commands.
- I'm currently loaning my books to %s servers.
- I'm currently playing music for %s servers.

- I'm open source! git.io/vpSEv
- I have a community server! discord.gg/jnKMSSE

- Made by @Epicfisher#6763
```"""

def GetSpecialQuote():
    # Special Birthday Quotes! Hooray!
    if datetime.now().month == 7 and datetime.now().day == 7:
        return "Happy Marisa Day! I've noticed a few books missing lately..."
    if datetime.now().month == 7 and datetime.now().day == 4:
        return "Happy Flandre Day! Should we let her out this once..?"
    if datetime.now().month == 6 and datetime.now().day == 9:
        return "Happy Patchouli (Me) Day! Mukyu~"
    if datetime.now().month == 5 and datetime.now().day == 15:
        return "Happy Meiling Day! I bought her a couple of books."
    #if datetime.now().month == 9 and datetime.now().day == 9 and datetime.now().hour == 9 and datetime.now().minute == 9:
        #return "Happy ⑨ Day, Hour and Minute! I wonder what Cirno's up to..?"
    if datetime.now().month == 9 and datetime.now().day == 9:
        return "Happy Cirno (Baka) Day! I heard she got a tan."
    if datetime.now().day == 5:
        return "Happy Remilia Day! I hope she doesn't celebrate by drinking."
    if datetime.now().day == 16:
        return "Happy Sakuya Day! She should take the day off."
    if datetime.now().day == 9:
        return "Happy Koakuma Day! Maybe I should let her slack off today."

    # Special Holiday Quotes! Hooray Again!
    if bot.season == "christmas":
        return "Happy Holidays! Get into the spirit with '" + bot.prefix + "image christmas'!"
    if bot.season == "halloween":
        return "Happy Halloween! Get spooked with '" + bot.prefix + "image halloween'!"

    # Generic Patchy Quotes
    random_number = randint(0,6)

    if random_number == 0:
        return "Whatever the weather, it doesn't matter if I stay at home."
    if random_number == 1:
        return "There is no rampaging around in my study."
    if random_number == 2:
        return "Hmm, my eyes have gotten worse lately."
    if random_number == 3:
        return "My asthma isn't bad today, so I'll show you my best magic!"
    if random_number == 4:
        return "Then I absolutely cannot allow you to see the mistress."
    if random_number == 5:
        return "Drizzle that humidifies the air is the book's worst enemy."
    if random_number == 6:
        return "There have been lots of mice in the library recently."

async def info(message):
    await message.channel.send(aboutMessage % (GetSpecialQuote(), str(discord.__version__), round((time() - bot.startTime) / 60, 1), str(len(commands.commands)), str(len(bot.client.guilds)), str(len(bot.radio_players))))
    return

###

commands.Add("info", info)