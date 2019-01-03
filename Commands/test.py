import commands

###

import bot
import sys, os
from youtube_dl import version as youtube_dl
import asyncio
import discord
import psutil

diagMessage = """```asciidoc
= Patchouli Knowledge Diagnosis Screen =

===== Versions =====
- Discord Version: """ + sys.version[:sys.version.index('(') - 1] + """
- discord.py Version: """ + str(discord.__version__) + """
- youtube-dl Version: """ + str(youtube_dl.__version__) + """

===== Memory =====
- Memory (B): %s
- Memory (KB): %s
- Memory (MB): %s
- Memory Usage (Out of 512MB): %s%%

===== Command Subsystem =====
- Running %s other commands.
```"""

def tester_check(message):
    if message.author.id == bot.owner_id: # haha only I can test because I am a developer >:)
        return True
    return False

async def diagnostics(message):
    if not tester_check(message):
        return

    process = psutil.Process(os.getpid())

    await message.channel.send(diagMessage % (process.memory_info().rss, process.memory_info().rss / 1000, process.memory_info().rss / 1000000, ((process.memory_info().rss / 1000000) / 512) * 100, len(bot.runningCommandsArray) - 1))

async def radio(message):
    if not tester_check(message):
        return

    if len(bot.radio_players) < 1:
        print("No Radios")
        return

    for i in range(0, len(bot.radio_players)):
        player = bot.radio_players[i]
        print("Player " + str(i) + ":\n---")

        print(" vc: " + str(player.vc))
        print(" Voice Channel: " + str(player.voice_channel))
        print(" Initialised: " + str(player.initialised))
        print(" Play Message: " + str(player.play_message))
        print(" Stop After: " + str(player.stop_after))
        print(" Get: " + str(player.get))
        print(" Queue Size: " + str(len(player.queue)))
        print(" Use Queue: " + str(player.use_queue))
        print(" Automatic Queue Disable: " + str(player.automatic_queue_disable))
        print(" Preparing Queue: " + str(player.preparing_queue))
        print(" Song: " + str(player.song))
        print(" Next Song: " + str(player.next_song))
        print(" Vote Skippers Size: " + str(len(player.vote_skippers)))
        print(" Skip Cooldown: " + str(player.skip_cooldown))
        print(" Saved Query: " + str(player.saved_query))
        print(" Playing Loop: " + str(player.playing_loop))
        print(" Volume: " + str(player.volume))
        print(" Sleep: " + str(player.sleep))

        print()

        print(" Is Playing: " + str(player.vc.is_playing()))
        print(" Is Paused: " + str(player.vc.is_paused()))

        print("---")

async def exception(message):
    if not tester_check(message):
        return

    raise ValueError('Manual test exception thrown.')
    return

async def sleep(message):
    if not tester_check(message):
        return

    await asyncio.sleep(5)
    await message.channel.send('Done sleeping')

async def cardraritytest(message):
    if not tester_check(message):
        return

    raw_names = await get_all_cards()

    card_options = GetCardOptions()
    card_options.get_rarity = True

    while True:
        try:
            random_card = randint(0, len(raw_names) - 1)
            card = await get_card_object(raw_names[random_card], card_options, True, False)
            print(card.rarity)
        except:
            pass

async def deadlythread(message):
    if not tester_check(message):
        return

    loop = asyncio.get_event_loop()
    await loop.run_in_executor(thread_pool, lambda: time.sleep(5000))
    print("Deadly Thread is Deadly No More\n")
    return

###

commands.Add("test.diag", diagnostics, count=False)
commands.Add("test.radio", radio, count=False)
commands.Add("test.exception", exception, count=False)
commands.Add("test.sleep", sleep, count=False)
commands.Add("test.raritytest", cardraritytest, count=False)
commands.Add("test.deadlythread", deadlythread, count=False)
