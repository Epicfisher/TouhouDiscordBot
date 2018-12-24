import os
from concurrent.futures import ThreadPoolExecutor
import asyncio
import aiohttp
import socket

class ImageSearchResult:
    Url = ""
    Name = ""

client = None

startTime = None

prefix = 'k.'

max_threads = None

thread_pool = None

hex_color = 0x593695

running_threads = 0

cooldown_message = None

season = None

allowLargeQuotes = None
postFullConversations = None

moderatorOnlyMusic = False
music_cooldowntime = 10 # Cooldown between new music retrievals. Value is in seconds

data_guild = None
data_channel = None

data_guild_id = None
data_channel_id = None

suggestions_guild = None
suggestions_channel = None

suggestions_guild_id = None
suggestions_channel_id = None

argumentChar = ' '
argumentKillChar = ''
argumentSeperator = ','

radio_players = []

use_rarity_check = True

runningCommandsArray = []

use_ssl = None

try:
    with open('prefix.txt', 'r') as myfile:
        prefix = myfile.read().replace('\n', '')
except:
    try:
        prefix = os.environ['PATCHYBOT-PREFIX']
    except:
        print("INFO:\n\nNo custom Prefix specified in either a 'prefix.txt' file or 'PATCHYBOT-PREFIX' System Environment Variable.\nUsing default Prefix of '" + prefix + "'.\n")

try:
    with open('data-guild-id.txt', 'r') as myfile:
        data_guild_id = myfile.read().replace('\n', '')
except:
    try:
        data_guild_id = os.environ['PATCHYBOT-DATAGUILDID']
    except:
        print ("WARNING:\n\nNo Data Guild ID specified in either a 'data-guild-id.txt' file or 'PATCHYBOT-DATAGUILDID' System Environment Variable.\nDisabling Data Storage Support...\n")

if not data_guild_id == None:
    try:
        with open('data-channel-id.txt', 'r') as myfile:
            data_channel_id = myfile.read().replace('\n', '')
    except:
        try:
            data_channel_id = os.environ['PATCHYBOT-DATACHANNELID']
        except:
            print ("WARNING:\n\nNo Data Channel ID specified in either a 'data-channel-id.txt' file or 'PATCHYBOT-DATACHANNELID' System Environment Variable.\nDisabling Data Storage Support...\n")

try:
    with open('suggestions-guild-id.txt', 'r') as myfile:
        suggestions_guild_id = myfile.read().replace('\n', '')
except:
    try:
        suggestions_guild_id = os.environ['PATCHYBOT-SUGGESTIONSGUILDID']
    except:
        print ("WARNING:\n\nNo Suggestions Guild ID specified in either a 'suggestions-guild-id.txt' file or 'PATCHYBOT-SUGGESTIONSGUILDID' System Environment Variable.\nDisabling Suggestions...\n")

if not suggestions_guild_id == None:
    try:
        with open('suggestions-channel-id.txt', 'r') as myfile:
            suggestions_channel_id = myfile.read().replace('\n', '')
    except:
        try:
            suggestions_channel_id = os.environ['PATCHYBOT-SUGGESTIONSCHANNELID']
        except:
            print ("WARNING:\n\nNo Suggestions Channel ID specified in either a 'suggestions-channel-id.txt' file or 'PATCHYBOT-SUGGESTIONSCHANNELID' System Environment Variable.\nDisabling Suggestions...\n")

async def run_in_threadpool(function):
    global running_threads

    while running_threads >= max_threads:
        await asyncio.sleep(1)

    running_threads = running_threads + 1

    loop = asyncio.get_event_loop()
    try:
        result = await loop.run_in_executor(thread_pool, function)
    except e:
        running_threads = running_threads - 1
        return e

    running_threads = running_threads - 1
    return result

async def get_aio_connector():
    conn = aiohttp.TCPConnector(
        family=socket.AF_INET,
        verify_ssl=use_ssl,
    )

    return conn

async def get(url):
    global use_ssl

    retry = True

    while retry:
        retry = False

        try:
            async with aiohttp.ClientSession(connector=await get_aio_connector()) as session:
                async with session.get(url) as resp:
                    return await resp.text()
        except Exception as e:
            if use_ssl:
                print("ERROR:\n\nFailed to download HTML with SSL enabled. Disabling SSL...\n")
                use_ssl = False
                retry = True
            else:
                print ("ERROR:\n\nFailed to download HTML with SSL disabled.\n")
                print(e)
                return

    return await r.text()

async def get_raw(url):
    async with aiohttp.ClientSession(connector=await get_aio_connector()) as session:
        async with session.get(url) as resp:
            return await resp.read()

def write_to_file(filename, content):
    f = open(filename, 'wb')
    f.write(content)
    f.close()

async def get_file(url, filename):
    content = await get_raw(url)
    write_to_file(filename, content)

async def get_image(search_results, quantity):
    if not isinstance(search_results, list):
        search_results = [search_results]
        quantity = 1

    results = ImageSearchResult() # Create Image Result class

    for i in range(0, quantity):
        json = await get("https://en.touhouwiki.net/wiki/" + search_results[i])

        try:
            json = json[json.index('infobox'):]
            json = json[json.index('<a href="/wiki/File:') + 9:]
            json = json[:json.index("</a>")]
            file = json[json.index('File:'):json.index('"')]

            json = await get("https://en.touhouwiki.net/api.php?action=query&titles=" + file + "&prop=imageinfo&iiprop=url&format=json")

            json = json[json.index('"url":"') + 7:]
            file = json[:json.index('"')]

            results.Url = file
            results.Name = search_results[i]
            return results # At this point, we should have our working image. Quit out of the for loop.
        except:
            if i >= quantity:
                return False
            else:
                print("No Photo for '" + search_results[i].replace("_", " ") + "'. Moving on...")

    return False
