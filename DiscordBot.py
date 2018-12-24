# Old global imports before MODULATION
'''
import sys, os
from concurrent.futures import ThreadPoolExecutor
from time import time
from datetime import datetime
import aiohttp, asyncio
import socket
import contextlib
import discord
import dbl
from youtube_dl import YoutubeDL
import urllib.parse, urllib.request
import html
from random import randint
import math
#from urllib.request import urlopen
'''

import sys, os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from time import time
import contextlib
from youtube_dl import version as youtube_dl # THIS ISN'T ACTUALLY YOUTUBE_DL IT'S THE VERSION OBJECT IDK I ONLY NEED THAT THOUGH SO IT'S FINE
import discord

#Bot#
import bot
#Bot#

#Commands#
from commands import commands # Access to commands array

import Commands.ping
import Commands.invite
#import(Commands.test
import Commands.help
import Commands.info
import Commands.suggest
import Commands.image
import Commands.quote
import Commands.search
import Commands.cards
import Commands.music
#Commands#

try:
    with open('token.txt', 'r') as myfile:
        token = myfile.read().replace('\n', '')
except:
    try:
        token = os.environ['PATCHYBOT-TOKEN']
    except:
        print ("CRITICAL ERROR:\n\nNo Bot Token specified in either a 'token.txt' file or 'PATCHYBOT-TOKEN' System Environment Variable.\nBot cannot start.\n")

        raise SystemExit(0)

bot.startTime = time()

#if not os.path.exists(os.path.dirname(os.path.realpath(__file__)) + '\\temp_music\\'):
    #os.makedirs(os.path.dirname(os.path.realpath(__file__)) + '\\temp_music\\')

bot.cooldown_message = "Hey, slow down! I can only work so fast on my own you know!"

if datetime.now().month == 12:
    bot.season = "christmas"
if datetime.now().month == 10:
    bot.season = "halloween"

bot.max_threads = 254 # Real max threads for free Heroku plans are 256, minus two since I assume the Bot is running on a Thread of it's own to begin with and one more just to feel safe.

bot.thread_pool = ThreadPoolExecutor(max_workers=bot.max_threads)

bot.allowLargeQuotes = False
bot.postFullConversations = False

allow_commands = False

bot.client = discord.Client()

closed_access_users = None

bot.use_ssl = True

try:
    with open('closed-access-users.txt', 'r') as myfile:
        closed_access_users = myfile.read().split('\n')
        print("INFO:\n\nClosed Access Users were specified in a 'closed-access-users.txt' file.\nStarted bot in Closed Access Mode...\n")
except:
    try:
        closed_access_users = [os.environ['PATCHYBOT-CLOSEDACCESSUSER']]
        print("INFO:\n\nA Closed Access User was specified in a 'PATCHYBOT-CLOSEDACCESSUSER' System Environment Variable.\nStarted bot in Closed Access Mode...\n")
    except:
        print("INFO:\n\nNo Closed Access Users specified in either a 'closed-access-users.txt' file or 'PATCHYBOT-CLOSEDACCESSUSER' System Environment Variable.\nOpening Bot to the public...\n")
        pass

##################################################DISCORD BOTS API############################################################
class DiscordBotsOrgAPI:
    def __init__(self, bot):
        self.bot = bot

        try:
            with open('dbl-token.txt', 'r') as myfile:
                dbltoken = myfile.read().replace('\n', '')
        except:
            try:
                dbltoken = os.environ['PATCHYBOT-DBLTOKEN']
            except:
                print ("WARNING:\n\nNo DBL Token specified in either a 'dbl-token.txt' file or 'PATCHYBOT-DBLTOKEN' System Environment Variable.\nDisabling discordbots.org API support...\n")

                return
        self.token = dbltoken

        self.dblpy = dbl.Client(self.bot, self.token)
        self.bot.loop.create_task(self.update_stats())

    async def update_stats(self):
        while True:
            #print('Attempting to post server count')
            try:
                await self.dblpy.post_server_count()
                print('Posted server count (' + str(len(self.bot.guilds)) + ")")
            except Exception as e:
                #print('Failed to post server count\n{}: {}\n'.format(type(e).__name__, e))
                print('Failed to post server count{\n' + e + '\n}')

            await asyncio.sleep(1800) # Wait 30 minutes in seconds

def setup_discord_bots_org_api(bot):
    #bot.add_cog(DiscordBotsOrgAPI(bot))
    print("Starting DiscordBotsOrgAPI...\n")
    DiscordBotsOrgAPI(bot)
    #pass

def run_discord_bot(token):
    OPUS_LIBS = ['libopus-0.x86.dll', 'libopus-0.x64.dll', 'libopus-0.dll', 'libopus.so.0', 'libopus.0.dylib', 'opus']

    if not discord.opus.is_loaded():
        for opus_lib in opus_libs:
            try:
                discord.opus.load_opus(opus_lib)
                print("Loaded Opus Lib!")
                break
            except OSError:
                pass
    else:
        print("Loaded Opus!")

    if not discord.opus.is_loaded():
        print("Failed to Load Opus!")

    print("Starting Bot...\n")
    bot.client.run(token)

##################################################START############################################################
@bot.client.event
async def on_ready():
    #await bot.client.change_presence(status=discord.Status.online, activity=discord.Game(bot.prefix + "help for Help!"))
    await bot.client.change_presence(status =discord.Status.online, activity=discord.Streaming(name=bot.prefix + "help for Help!", url="https://www.twitch.tv/patchouli_knowledge_bot", type=1))

    global allow_commands

    global data_guild
    global data_channel

    global suggestions_guild
    global suggestions_channel

    if not bot.data_guild_id == None:
        bot.data_guild = bot.client.get_guild(int(bot.data_guild_id))
    if not bot.data_channel_id == None:
        bot.data_channel = bot.data_guild.get_channel(int(bot.data_channel_id))

    if not bot.suggestions_guild_id == None:
        bot.suggestions_guild = bot.client.get_guild(int(bot.suggestions_guild_id))
    if not bot.suggestions_channel_id == None:
        bot.suggestions_channel = bot.suggestions_guild.get_channel(int(bot.suggestions_channel_id))

    allow_commands = True # Now we're truly ready to begin taking commands

    print('Logged in as')
    print(bot.client.user.name)
    print(bot.client.user.id)
    print('------')

##################################################VOICE CHANNEL UPDATE DETECTION############################################################
@bot.client.event
async def on_voice_state_update(member, before, after):
    if 'Commands.music' in sys.modules: # Handle disconnect if last person in Voice Channel left
        #print("Handle state")
        #if after.channel == None:
        try:
            for channel in member.guild.voice_channels:
                if channel.id == before.channel.id:
                    if len(channel.members) < 2:
                        Commands.music.radio_player = None

                        for i in range(0, len(bot.radio_players)):
                            if bot.radio_players[i].vc.guild.id == member.guild.id:
                                Commands.music.radio_player = bot.radio_players[i]

                                if Commands.music.radio_player == None:
                                    return

                                await Commands.music.radio_player.Stop()
                                return
        except:
            return

##################################################JOINING AND LEAVING LOGS############################################################
@bot.client.event
async def on_guild_join(guild):
    print("I have been Invited to a Server!")
    return

@bot.client.event
async def on_guild_remove(guild):
    print("I have been Removed from a Server!")
    return

##################################################COMMAND HANDLER############################################################
@bot.client.event
async def on_message(message):
    if not allow_commands:
        return

    if message.author.bot: # Don't allow bots to trigger commands because this is a good bot
        return

    lowercaseMessage = message.content.lower()
    is_command = False
    was_mention = False

    if lowercaseMessage.startswith(bot.prefix):
        lowercaseMessage = lowercaseMessage[len(bot.prefix):]
        is_command = True
    if lowercaseMessage.startswith('<@' + str(bot.client.user.id) + '>'):
        lowercaseMessage = lowercaseMessage[len('<@' + str(bot.client.user.id) + '>'):]
        is_command = True
        was_mention = True

    if is_command:
        if not closed_access_users == None:
            if not str(message.author.id) in closed_access_users:
                print("Blocked access from non closed-access user")
                return

        if len(lowercaseMessage) > 0:
            if was_mention:
                while lowercaseMessage[0] == ' ':
                    lowercaseMessage = lowercaseMessage[1:]
            if lowercaseMessage[0] == " ":
                return
        else:
            if was_mention:
                lowercaseMessage = "help"
                message.content = bot.prefix + "help" # This is a BIT messy but I can't really think of any other way to do this in a cleaner way since every command is passed "message"

        if bot.runningCommandsArray.count(message.author.id) > 1:
            print("Blocked spamming user's new command '" + message.content + "'")
            await message.channel.send(bot.cooldown_message)
            return
        else:
            bot.runningCommandsArray.append(message.author.id)
            await handle_command(message, lowercaseMessage)
            bot.runningCommandsArray.remove(message.author.id)
            print("Handled Command '" + message.content + "' Sent By '" + str(message.author) + "'\n")

async def handle_command(message, lowercaseMessage):
    print("Handling Command '" + message.content + "' Sent By '" + str(message.author) + "'")

    try:
        for i in range(0, len(commands)):
            if commands[i].name.endswith('%'):
                if lowercaseMessage.startswith(commands[i].name[:-1]):
                    await commands[i].command(message)
                    return
            else:
                if lowercaseMessage == commands[i].name:
                    await commands[i].command(message)
                    return

        #await message.channel.send("Sorry, but I'm not quite sure what you're asking me to do.")
    except Exception as e:
        print("USER HAD AN ERROR! BIG BAD<\n'" + str(message.content) + "'\n" +  str(e) + "\n>")
        await message.channel.send("Whoops! Something went wrong in my head while trying to figure that one out... Sorry!")

print("""Now starting with:
- discord.py Version: """ + str(discord.__version__) + """
- youtube-dl Version: """ + str(youtube_dl.__version__) + """
""")

setup_discord_bots_org_api(bot.client) # Setup Discord Bots Org API
run_discord_bot(token) # Start the bot with the Token
