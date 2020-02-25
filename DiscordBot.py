import sys, os
import asyncio
from datetime import datetime
from time import time
import contextlib
from youtube_dl import version as youtube_dl # THIS ISN'T ACTUALLY YOUTUBE_DL IT'S THE VERSION OBJECT IDK I ONLY NEED THAT THOUGH SO IT'S FINE
import discord
import dbl

#Bot#
import bot
#Bot#

#Commands#
from commands import commands # Access to commands array

import Commands.ping
import Commands.invite
if not bot.owner_id == -1:
    import Commands.test
import Commands.help
import Commands.info
import Commands.suggest
import Commands.report
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
        bot.log("CRITICAL ERROR", "No Bot Token specified in either a 'token.txt' file or 'PATCHYBOT-TOKEN' System Environment Variable.\nBot cannot start.")

        raise SystemExit(0)

bot.startTime = time()

#if not os.path.exists(os.path.dirname(os.path.realpath(__file__)) + '\\temp_music\\'):
    #os.makedirs(os.path.dirname(os.path.realpath(__file__)) + '\\temp_music\\')

bot.cooldown_message = "Hey, slow down! I can only work so fast on my own you know!"

if datetime.now().month == 12:
    if datetime.now().day <= 25:
        bot.season = "christmas"
    else:
        bot.season = "new year"
if datetime.now().month == 10:
    bot.season = "halloween"

bot.max_threads = 254 # Real max threads for free Heroku plans are 256, minus two since I assume the Bot is running on a Thread of it's own to begin with and one more just to feel safe.

bot.allowLargeQuotes = False
bot.postFullConversations = False

allow_commands = False

bot.client = discord.Client()

closed_access_users = None

bot.use_ssl = True

try:
    with open('closed-access-users.txt', 'r') as myfile:
        closed_access_users = myfile.read().split('\n')
        bot.log("INFO", "Closed Access Users were specified in a 'closed-access-users.txt' file.\nStarted bot in Closed Access Mode...")
except:
    try:
        closed_access_users = [os.environ['PATCHYBOT-CLOSEDACCESSUSER']]
        bot.log("INFO", "A Closed Access User was specified in a 'PATCHYBOT-CLOSEDACCESSUSER' System Environment Variable.\nStarted bot in Closed Access Mode...")
    except:
        bot.log("INFO", "No Closed Access Users specified in either a 'closed-access-users.txt' file or 'PATCHYBOT-CLOSEDACCESSUSER' System Environment Variable.\nOpening Bot to the public...")
        pass

##################################################DISCORD BOTS API############################################################
class DiscordBotsOrgAPI:
    def __init__(self, _bot):
        self.bot = _bot

        try:
            with open('dbl-token.txt', 'r') as myfile:
                dbltoken = myfile.read().replace('\n', '')
        except:
            try:
                dbltoken = os.environ['PATCHYBOT-DBLTOKEN']
            except:
                bot.log("WARNING", "No DBL Token specified in either a 'dbl-token.txt' file or 'PATCHYBOT-DBLTOKEN' System Environment Variable.\nDisabling discordbots.org API support...")

                return
        self.token = dbltoken

        try:
            self.dblpy = dbl.DBLClient(self.bot, self.token)
            self.bot.loop.create_task(self.update_stats())
        except Exception as e:
            print("Failed to Initialise Discord Bots API!\n" + str(e))

    async def update_stats(self):
        while True:
            await asyncio.sleep(1800) # Wait 30 minutes in seconds

            #print('Attempting to post server count')
            try:
                #await self.dblpy.post_server_count()
                await self.dblpy.post_guild_count()
                print('Posted server count (' + str(len(self.bot.guilds)) + ")\n")
            except Exception as e:
                #print('Failed to post server count\n{}: {}\n'.format(type(e).__name__, e))
                print('Failed to post server count{\n' + str(e) + '\n}')

def setup_discord_bots_org_api(bot):
    #bot.add_cog(DiscordBotsOrgAPI(bot))
    print("Starting DiscordBotsOrgAPI...\n")
    DiscordBotsOrgAPI(bot)
    #pass

def setup_opus():
    print("Configuring Opus...\n")
    opus_libs = ['libopus-0.x86.dll', 'libopus-0.x64.dll', 'libopus-0.dll', 'libopus.so.0', 'libopus.so', 'libopus.0.dylib', 'opus', 'opus.exe']

    if not discord.opus.is_loaded():
        for opus_lib in opus_libs:
            try:
                discord.opus.load_opus(opus_lib)
                print("Loaded External Opus Library!\n")
                break
            except OSError:
                pass
    else:
        print("Loaded System Opus Library!\n")

    if not discord.opus.is_loaded():
        bot.log("INFO", "Failed to Load Opus.\nPCM Audio will be used instead.")

def run_discord_bot(token):
    print("Starting Bot...\n")
    bot.client.run(token, reconnect=True)
    #while True:
    	#try:
    		#bot.client.loop.run_until_complete(bot.client.start(token))
    	#except BaseException as e:
            #print("Failed to start! Retrying in 5 seconds...\n" + str(e))
            #time.sleep(5)
            #print("Retrying...\n")

    #while True:
        #try:
            #bot.client.run(token)
            #break
        #except Exception as e:
            #print("Failed to start! Retrying in 10 seconds...\n" + str(e))
            #time.sleep(10)
            #print("Retrying...\n")

##################################################START############################################################
async def set_presence():
    #await bot.client.change_presence(status=discord.Status.online, activity=discord.Game(bot.prefix + "help for Help!"))
    await bot.client.change_presence(status=discord.Status.online, activity=discord.Streaming(name=bot.prefix + "help for Help!", url="https://www.twitch.tv/patchouli_knowledge_bot", type=1))

async def initialise():
    global allow_commands

    if not bot.data_guild_id == None:
        bot.data_guild = bot.client.get_guild(int(bot.data_guild_id))
    if not bot.data_channel_id == None:
        bot.data_channel = bot.data_guild.get_channel(int(bot.data_channel_id))

    if not bot.suggestions_guild_id == None:
        bot.suggestions_guild = bot.client.get_guild(int(bot.suggestions_guild_id))
    if not bot.suggestions_channel_id == None:
        bot.suggestions_channel = bot.suggestions_guild.get_channel(int(bot.suggestions_channel_id))

    if not bot.reports_guild_id == None:
        bot.reports_guild = bot.client.get_guild(int(bot.reports_guild_id))
    if not bot.reports_channel_id == None:
        bot.reports_channel = bot.reports_guild.get_channel(int(bot.reports_channel_id))

    print("Caching Character Database...\n")
    await Commands.image.ParseCharacters(Commands.image.character_names, Commands.image.character_links)

    allow_commands = True # Now we're truly ready to begin taking commands

@bot.client.event
async def on_ready():
    await initialise()

    await set_presence()

    print('Logged in as')
    print(bot.client.user.name)
    print(bot.client.user.id)
    print('------')

@bot.client.event
async def on_resumed():
    await set_presence()

    print('Reconnected as')
    print(bot.client.user.name)
    print(bot.client.user.id)
    print('------')

##################################################VOICE CHANNEL UPDATE DETECTION############################################################
async def check_voice_channel(channel, i):
    valid_members = 0
    for member in channel.members:
        if not member.bot:
            valid_members = valid_members + 1

    if valid_members < 1:
        if bot.radio_players[i].voice_channel.id == channel.id:
            #Commands.music.radio_player = None
            Commands.music.radio_player = bot.radio_players[i]

            if Commands.music.radio_player == None:
                return False

            await Commands.music.radio_player.Stop()
            return False
    return True

@bot.client.event
async def on_voice_state_update(member, before, after):
    if 'Commands.music' in sys.modules: # Handle disconnect if last person in Voice Channel left
        #print("Handle state")
        #if after.channel == None:
        try:
            for channel in member.guild.voice_channels:
                if channel.id == before.channel.id:
                    for i in range(0, len(bot.radio_players)):
                        if bot.radio_players[i].voice_channel.guild.id == channel.guild.id:
                            if not await check_voice_channel(channel, i):
                                print("Last User in VC '" + str(before.channel) + "' ('" + str(channel) + "') Left. Killed VC of Radio " + str(i) + ".")
                                return

                            if not after.channel.id == bot.radio_players[i].voice_channel.id and member.id == bot.client.user.id: # Have we been moved into a new Voice Channel?
                                print("Updating Channel for Radio VC " + str(i) + " to '" + str(after.channel) + "'.")
                                bot.radio_players[i].voice_channel = after.channel
                                if not await check_voice_channel(after.channel, i):
                                    return
        except:
            return

##################################################JOINING AND LEAVING LOGS############################################################
@bot.client.event
async def on_guild_join(guild):
    print("I have been Invited to a Server!\n")
    return

@bot.client.event
async def on_guild_remove(guild):
    print("I have been Removed from a Server!\n")
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

    if lowercaseMessage.endswith('::'):
        lowercaseMessage = lowercaseMessage[:-2]
        message.content = message.content[:-2]

    if lowercaseMessage.endswith(' '):
        lowercaseMessage = lowercaseMessage[:-1]
        message.content = message.content[:-1]

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
            if await handle_command(message, lowercaseMessage):
                bot.runningCommandsArray.remove(message.author.id)
            print("Handled Command '" + message.content + "' Sent By '" + str(message.author) + "'\n")

async def handle_command(message, lowercaseMessage):
    print("Handling Command '" + message.content + "' Sent By '" + str(message.author) + "'")

    try:
        for i in range(0, len(commands)):
            if commands[i].name.endswith('%'):
                if lowercaseMessage.startswith(commands[i].name[:-1]):
                    await commands[i].command(message)
                    return True
            else:
                if lowercaseMessage == commands[i].name:
                    await commands[i].command(message)
                    return True

        #await message.channel.send("Sorry, but I'm not quite sure what you're asking me to do.")
        return True
    except Exception as e:
        try:
            bot.runningCommandsArray.remove(message.author.id)
        except:
            if message.author.id in bot.runningCommandsArray:
                print("FAILED TO REMOVE RUNNING COMMAND INSTANCE FOR '" + str(message.author) + "'. THIS IS VERY VERY BIG BAD")
            else:
                print("User '" + str(message.author) + "' has no Running Command Instance. Please advise. Is this bad? Or ok?")
            pass

        try:
            print("USER HAD AN ERROR! BIG BAD<\n'" + str(message.content) + "'\n" +  str(e) + "\n>")
            if "Missing Permissions" in str(e): # lol this probably isn't the best but it works and I don't really care
                await message.channel.send("Whoops! I'm missing a Permission to send that message!")
            else:
                await message.channel.send("Whoops! Something went wrong in my head while trying to figure that one out... Sorry!")
        except:
            pass
        return False

print("""Now starting with:
- Python Version: """ + sys.version[:sys.version.index('(') - 1] + """
- discord.py Version: """ + str(discord.__version__) + """
- youtube-dl Version: """ + str(youtube_dl.__version__) + """
""")

setup_discord_bots_org_api(bot.client) # Setup Discord Bots Org API
setup_opus() # Setup Opus Audio Codec
run_discord_bot(token) # Start the bot with the Token
