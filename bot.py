import os
from concurrent.futures import ThreadPoolExecutor
import asyncio
import aiohttp
import socket
import html

class ImageSearchResult:
    Url = ""
    Name = ""
    Summary = ""

client = None

startTime = None

prefix = 'k.'

running_threads = 0
max_threads = None

owner_id = -1 # Special ID of the Bot's Owner. This is for special commands, such as temporary debug and test commands. See test.py. Disabled by default

hex_color = 0x593695

cooldown_message = None # For when a user just wont stop spamming the library's poor customer reception. This is actually set in DiscordBot.py

season = None # Used for special messages on Christmas, Halloween etc.

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

reports_guild = None
reports_channel = None
reports_guild_id = None
reports_channel_id = None

argumentChar = ' '
argumentKillChar = ''
argumentSeperator = ','

radio_players = []

use_rarity_check = True

runningCommandsArray = []

use_ssl = None

def log(header, text):
    print(header + ":\n" + text + "\n")

try:
    with open('prefix.txt', 'r') as myfile:
        prefix = myfile.read().replace('\n', '')
except:
    try:
        prefix = os.environ['PATCHYBOT-PREFIX']
    except:
        log("INFO", "No custom Prefix specified in either a 'prefix.txt' file or 'PATCHYBOT-PREFIX' System Environment Variable.\nUsing default Prefix of '" + prefix + "'.")

try:
    with open('owner.txt', 'r') as myfile:
        owner_id = int(myfile.read().replace('\n', ''))
except:
    try:
        owner_id = int(os.environ['PATCHYBOT-OWNER'])
    except:
        log("INFO", "No Owner ID specified in either a 'owner.txt' file or 'PATCHYBOT-OWNER' System Environment Variable.\nDisabling Test Commands...")

try:
    with open('data-guild-id.txt', 'r') as myfile:
        data_guild_id = myfile.read().replace('\n', '')
except:
    try:
        data_guild_id = os.environ['PATCHYBOT-DATAGUILDID']
    except:
        log("WARNING", "No Data Guild ID specified in either a 'data-guild-id.txt' file or 'PATCHYBOT-DATAGUILDID' System Environment Variable.\nDisabling Data Storage Support...")

if not data_guild_id == None:
    try:
        with open('data-channel-id.txt', 'r') as myfile:
            data_channel_id = myfile.read().replace('\n', '')
    except:
        try:
            data_channel_id = os.environ['PATCHYBOT-DATACHANNELID']
        except:
            log("WARNING", "No Data Channel ID specified in either a 'data-channel-id.txt' file or 'PATCHYBOT-DATACHANNELID' System Environment Variable.\nDisabling Data Storage Support...")

try:
    with open('suggestions-guild-id.txt', 'r') as myfile:
        suggestions_guild_id = myfile.read().replace('\n', '')
except:
    try:
        suggestions_guild_id = os.environ['PATCHYBOT-SUGGESTIONSGUILDID']
    except:
        log("WARNING", "No Suggestions Guild ID specified in either a 'suggestions-guild-id.txt' file or 'PATCHYBOT-SUGGESTIONSGUILDID' System Environment Variable.\nDisabling Suggestions...")

if not suggestions_guild_id == None:
    try:
        with open('suggestions-channel-id.txt', 'r') as myfile:
            suggestions_channel_id = myfile.read().replace('\n', '')
    except:
        try:
            suggestions_channel_id = os.environ['PATCHYBOT-SUGGESTIONSCHANNELID']
        except:
            log("WARNING", "No Suggestions Channel ID specified in either a 'suggestions-channel-id.txt' file or 'PATCHYBOT-SUGGESTIONSCHANNELID' System Environment Variable.\nDisabling Suggestions...")

try:
    with open('reports-guild-id.txt', 'r') as myfile:
        reports_guild_id = myfile.read().replace('\n', '')
except:
    try:
        reports_guild_id = os.environ['PATCHYBOT-REPORTSGUILDID']
    except:
        log("WARNING", "No Reports Guild ID specified in either a 'reports-guild-id.txt' file or 'PATCHYBOT-REPORTSGUILDID' System Environment Variable.\nDisabling Reports...")

if not reports_guild_id == None:
    try:
        with open('reports-channel-id.txt', 'r') as myfile:
            reports_channel_id = myfile.read().replace('\n', '')
    except:
        try:
            reports_channel_id = os.environ['PATCHYBOT-REPORTSCHANNELID']
        except:
            log("WARNING", "No Reports Channel ID specified in either a 'reports-channel-id.txt' file or 'PATCHYBOT-REPORTSCHANNELID' System Environment Variable.\nDisabling Reports...")

async def run_in_threadpool(function):
    global running_threads

    while running_threads >= max_threads:
        await asyncio.sleep(1)

    with ThreadPoolExecutor(max_workers=1) as thread_pool:
        running_threads = running_threads + 1

        loop = asyncio.get_event_loop()
        result = loop.run_in_executor(thread_pool, function)
        try:
            result = await result
        except Exception as e:
            raise e
        finally:
            running_threads = running_threads - 1
            thread_pool.shutdown(wait=True)

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
        except aiohttp.ClientError as e:
            if use_ssl:
                log("ERROR", "Failed to download HTML with SSL enabled.\nDisabling SSL...")
                use_ssl = False
                retry = True
            else:
                log("ERROR", "Failed to download HTML with SSL disabled.")
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

async def get_image(search_results, quantity, image_required, get_summary):
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
        except:
            print("No Photo for '" + search_results[i] + "'. Moving on...")

        if get_summary:
            json = await get("https://en.touhouwiki.net/api.php?action=parse&page=" + search_results[i] + "&prop=properties&format=json")

            try:
                summary = json[json.index('"description"') + 14:]
                summary = summary[summary.index(":") + 2:]
                summary = summary[:summary.index('"')]

                results.Summary = html.unescape(summary.encode().decode("unicode-escape"))
            except:
                print("No Summary for " + search_results[i] + ". Moving on...")
                results.Summary = ""

        if i  >= quantity:
            return False

        if not image_required or not results.Url == "":
            return results

    return False
