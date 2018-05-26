import os
import time
import aiohttp
import asyncio
import socket
import discord
import dbl
import random
from urllib.request import urlopen
from random import randint

startTime = time.time()

class ScriptMessage:
    Actor = ""
    Message = ""

class ImageSearchResult:
    Url = ""
    Name = ""

def GetArgumentsFromCommand(command):
    command = command[len(prefix):]

    try:
        command = command[command.index(argumentChar) + 1: ]
    except:
        return False

    if command.endswith(argumentKillChar) and len(argumentKillChar) > 0:
        command = command[:-1]
    
    commandArray = command.split(argumentSeperator)

    for commandUsed in commandArray:
        if commandUsed.startswith(' '):
            commandUsed = commandUsed[1:]
    
    return commandArray

try:
    with open('token.txt', 'r') as myfile:
        token = myfile.read().replace('\n', '')
except:
    try:
        token = os.environ['PATCHYBOT-TOKEN']
    except:
        print ("CRITICAL ERROR:\n\nNo Bot Token specified in either a 'token.txt' file or 'PATCHYBOT-TOKEN' System Environment Variable.\nBot cannot start.\n")
        
        raise SystemExit(0)

runningCommandsArray = []

prefix = 'k.'

try:
    with open('prefix.txt', 'r') as myfile:
        prefix = myfile.read().replace('\n', '')
except:
    try:
        prefix = os.environ['PATCHYBOT-PREFIX']
    except:
        print("INFO:\n\nNo custom Prefix specified in either a 'prefix.txt' file or 'PATCHYBOT-PREFIX' System Environment Variable.\nUsing default Prefix of '" + prefix + "'.\n")

argumentChar = ' '
argumentKillChar = ''
argumentSeperator = ','

cooldown_message = "Hey, slow down! I can only work so fast on my own you know!"

helpMessage = """```
~Patchouli Knowledge Help~

~~~~~General Commands~~~~~
""" + prefix + """help - You're currently reading this!
""" + prefix + """info - Information about me. Wow. Very interesting.
""" + prefix + """suggest""" + argumentChar + """Idea""" + argumentKillChar + """ - Suggests an 'Idea' to the Bot developers.

~~~~~Image Commands~~~~~
""" + prefix + """image - Gets a Touhou image from Gelbooru.
""" + prefix + """image""" + argumentChar + """Cirno Frog""" + argumentKillChar + """ - Gets an image with 'Cirno' and a 'Frog'.
""" + prefix + """nsfwimage - Gets a NSFW Touhou image. NSFW Channel required.
""" + prefix + """nsfwimage""" + argumentChar + """Reimu Solo""" + argumentKillChar + """ - Gets an NSFW image of just Reimu.

~~~~~Quote Commands~~~~~
""" + prefix + """quote - Gets a quote from a random Touhou game.
""" + prefix + """quote""" + argumentChar + """6""" + argumentKillChar + """ - Gets a quote from Touhou 6.

~~~~~Search Commands~~~~~
""" + prefix + """search""" + argumentChar + """Reimu""" + argumentKillChar + """ - Searches for 'Reimu' pages on touhouwiki.net.
""" + prefix + """portrait""" + argumentChar + """Reimu""" + argumentKillChar + """ - Searches for a 'Reimu' portrait.
""" + prefix + """lookup""" + argumentChar + """Reimu""" + argumentKillChar + """ - Searches for a 'Reimu' page and portrait.

~~~~~Card Commands~~~~~
[BETA] """ + prefix + """card - Gets a Trading Card. (No progress is saved)

```"""

# [BETA] """ + prefix + """daily -  Receive your daily Card. Resets every 24 hours.

aboutMessage = """```
~About Patchouli Knowledge~

- Runs entirely in Python 3, with the use of discord.py %s.
- So far I have stayed up reading for %s minutes.
- I'm currently loaning my books to %s servers.
- I'm open source! https://git.io/vpSEv
- Made by @Epicfisher#6763

```"""

allowLargeQuotes = False
postFullConversations = False

allow_commands = False

client = discord.Client()

closed_access_users = None

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

data_guild = None
data_channel = None

data_guild_id = None
data_channel_id = None

suggestions_guild = None
suggestions_channel = None

suggestions_guild_id = None
suggestions_channel_id = None

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

##################################################AIOHTTP CONNECTOR############################################################

use_ssl = True

async def get_aio_connector():
    conn = aiohttp.TCPConnector(
        family=socket.AF_INET,
        verify_ssl=use_ssl,
    )
    
    return conn

##################################################ASYNC HTML DOWNLOADER############################################################
async def get(url):
    retry = True
    
    while retry:
        retry = False
        
        try:
            async with aiohttp.ClientSession(connector=await get_aio_connector()) as session:
                async with session.get(url) as resp:
                    return await resp.text()
        except:
            if use_ssl:
                print("ERROR:\n\nFailed to download HTML with SSL enabled. Disabling SSL...\n")
                use_ssl = False
                retry = True
            else:
                print ("ERROR:\n\nFailed to download HTML with SSL disabled.\n")
                return
            
    return await r.text()

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
            print('Attempting to post server count')
            try:
                await self.dblpy.post_server_count()
                print('Posted server count (' + str(len(self.bot.guilds)) + ")")
            except Exception as e:
                print('Failed to post server count\n{}: {}\n'.format(type(e).__name__, e))
            
            await asyncio.sleep(1800) # Wait 30 minutes in seconds

def setup_discord_bots_org_api(bot):
    #bot.add_cog(DiscordBotsOrgAPI(bot))
    DiscordBotsOrgAPI(bot)
    #pass
    
##################################################IMAGES############################################################
async def PostImage(message, rating, tags, APILink):
    image_seperator_char = ' '
    image_space_char = '_'

    async with message.channel.typing():
        tags = "rating:" + rating + "+" + tags # Format and add the Rating into the total Tags

        bad_sfw_tags = ['nude', 'ass', 'anus', 'no_panties', 'no_bra', 'removing_panties', 'pussy_juice', 'vibrator', 'breasts', 'nipples', 'topless', 'thighs', 'upskirt', 'rape', 'sex', 'masturbation', 'implied_masturbation', 'yuri', 'vore', 'tentacles', 'guro', 'blood']

        arguments = GetArgumentsFromCommand(message.content)

        additional_tags = ""

        if not arguments == False:
            character_names = []
            
            raw_characters_html = await get("http://touhou.wikia.com/wiki/Character_List") # API is too confusing for a simpleton like me so I guess I'll just parse the webpage HTML don't mind me
            raw_characters_html = raw_characters_html[raw_characters_html.index('id="Character_List"'):raw_characters_html.index('id="Unnamed_Characters"')]
            
            parsing = True
            while parsing:
                try:
                    raw_characters_html = raw_characters_html[raw_characters_html.index('title="') + 7:]
                    character_names.append(raw_characters_html[:raw_characters_html.index('"')])
                except:
                    parsing = False

            additional_tags = arguments[0]
            
            tags_array = additional_tags.split(image_seperator_char)
            additional_tags = ""
            i = 0
            for tag in tags_array:
                while tag.startswith(' '):
                    tag = tag[1:]
                while tag.endswith(' '):
                    tag = tag[0:len(tag) - 1]

                character = ''
                if tag.startswith("$") and tag.endswith("$"): # Disable Character Recognition
                    tag = tag[1:-1] # Hide the symbols
                else: # We don't want to disable Character Recognition
                    swap_names_back = False
                    found_character = False
                    for character_name in character_names:
                        if found_character:
                            break
                        character_array = character_name.split(" ")
                        if len(character_array) >= 2:
                            for character_word in character_array:
                                tag_words = tag.lower().split(image_space_char)
                                for tag_word in tag_words:
                                    if tag_word == character_word.lower() and not character_word.lower() == 'no' and not character_word.lower() == 'giant' and not character_word.lower() == 'three' and not character_word.lower() == 'mischievous':
                                        if len(character_array) > 2:
                                            character = character_name.replace(" ", "_")
                                        else:
                                            character = character_array[1] + "_" + character_array[0]
                                            swap_names_back = True

                                        found_character = True
                                        break
                        else:
                            if tag.lower() == character_name.lower():
                                character = character_name
                                
                                found_character = True
                                break

                if len(character) > 0:
                    keep_testing = True
                    try_end_touhou_tag = True
                    got_character = False
                    while keep_testing:
                        keep_testing = False

                        html = await get(APILink + "?page=dapi&s=post&q=index&limit=1&json=1&pid=10&tags=" + tags + "+" + character) # We're going to check if our new name has atleast 10 results
                        if not "file_url" in html: # If it doesn't...
                            #print("Trying " + character)
                            if swap_names_back:
                                if character.startswith(character_array[1]):
                                    character = character_array[0] + "_" + character_array[1] # Swap the names around again back to it's original positions
                                else:
                                    character = character_array[1] + "_" + character_array[0] # Swap the names around again back to it's reversed positions
                                swap_names_back = False
                                keep_testing = True
                                if not try_end_touhou_tag:
                                    character = character + "_(touhou)"
                            if not character.endswith("_(touhou)") and swap_names_back == False and keep_testing == False and try_end_touhou_tag:
                                character = character + "_(touhou)"
                                if len(character_array) == 2:
                                    swap_names_back = True
                                keep_testing = True
                                try_end_touhou_tag = False
                        else: # If we were able to find atleast 10 images of our character tag...
                            #print("Working " + character)
                            keep_testing = False
                            got_character = True
                            tag = character

                    if not got_character:
                        #await message.channel.send("I couldn't find an image of your character '" + tag + "'!\nPro Tip: Don't want me to treat a tag as a character? Simple! Just let me know by putting a '$' symbol at the start and end of your tag!")
                        #return
                        tag = ''

                if len(tag) > 0:
                    raw_tag = tag
                    if tag.startswith('-'):
                        raw_tag = raw_tag[1:]

                    is_good_tag = True

                    if raw_tag.startswith("rating"): # Disallow modification to the Rating tag
                        is_good_tag = False

                    if rating == "safe": # Disallow certain tags if we're supposed to be SFW
                        for bad_tag in bad_sfw_tags: # Cycle through all bad SFW tags
                            if raw_tag == bad_tag: # Check for a match with the current tag
                                is_good_tag = False
                                break

                    if is_good_tag:
                        additional_tags = additional_tags + tag + '+'

                    i = i + 1

        if len(additional_tags) > 0:
            print("Using additional tags: '" + additional_tags[0:-1].replace(image_space_char, '_') + "'")

        if rating == "safe":
            for bad_tag in bad_sfw_tags: # Add a filter for all bad tags if we're SFW so they aren't shown
                additional_tags = additional_tags + '-' + bad_tag + '+'

        if not additional_tags == None:
            tags = tags + '+' + additional_tags.replace(image_space_char, "_")

        while tags.endswith('+'):
            tags = tags[0:-1]  # Cut off the last '+'s

        html = await get(APILink + "?page=dapi&s=post&q=index&limit=1&json=1&pid=1&tags=" + tags)
        if not "file_url" in html:
            await message.channel.send("I couldn't find an image!")
            return

        #print("Using tags: '" + tags + "'")

        page_scope = 20000
        i = 1

        worked = False
        while not worked:
            html = await get(APILink + "?page=dapi&s=post&q=index&limit=1&json=1&pid=" + str(randint(0, page_scope)) + "&tags=" + tags)

            try:
                fileUrl = html[html.index('file_url":"') + 11 : - 3]
                fileUrl = fileUrl.replace("\/", "/")
                fileUrl = fileUrl[0:fileUrl.index('"')]

                source = html[html.index('source":"') + 9:]
                source = source[:source.index('"')]
                source = source.replace("\/", "/")

                print("Posting Image: " + fileUrl)
                if len(source) > 0:
                    print("Image Source: " + source)

                worked = True
            except:
                i = i + 1
                if i <= 2:
                    page_scope = int(page_scope / 2)
                else:
                    page_scope = int(page_scope / 3)

                if page_scope < 1:
                    await message.channel.send("I couldn't find an image!")
                    return
                #else:
                    #print("Dividing our search scope to '" + str(page_scope) + "'... [Attempt " + str(i) + "]") # Mainly for debug purposes

        messageEmbed = discord.Embed()
        messageEmbed.set_image(url=fileUrl)
        messageEmbed.add_field(name="Image URL", value=fileUrl, inline=False)
        if len(source) > 0:
            messageEmbed.add_field(name="Image Source",value=source, inline=False)

        await message.channel.send(embed=messageEmbed)

##################################################SEARCH API HANDLERS############################################################
async def get_search_results(query, quantity):
    json = await get("https://en.touhouwiki.net/api.php?action=query&list=search&srprop=redirecttitle&srwhat=title&format=json&srsearch=" + query + "&utf8=")

    json = json[json.index('"search":'):len(json)]

    searchResults = []

    keepParsing = True
    while keepParsing:
        try:
            json = json[json.index('"title"') + 9:]
            searchResults.append(json[:json.index('"')].replace(" ", "_"))
            #print (json + "\n" + title + "\n")
        except:
            keepParsing = False

    searchResults.sort(key=len) # Sort total results by length, smallest first. This is tricky, as it could mess stuff up, but all in all it works better for the smaller queries people run,  like 'ZUN', but not really so for more longer and vague queries. Oh well, this is just the kind of sacrifice that has to be made I guess, I don't see any other way around this issue, unless we do something like sort by popularity or 'clicks', which the Wikimedia API doesn't even have support for.

    return searchResults[:quantity]

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
    
##################################################SEARCH############################################################
async def get_search(message, getUrls, getImage):
    arguments = GetArgumentsFromCommand(message.content)

    if arguments == False:
        await message.channel.send("You're going to have to give me something to look for.")
        return
    else:
        query = arguments[0]

    async with message.channel.typing():
        searchResults = await get_search_results(query, 5)

        if len(searchResults) < 1:
            await message.channel.send("I couldn't find anything in my library for '" + query + "'.")
            return

        if getUrls:
            if getUrls and getImage: # Lookup
                messageEmbed = discord.Embed(title="Lookup Result For '" + query + "'")
                
                messageEmbed.add_field(name="Page URL", value="https://en.touhouwiki.net/wiki/" + searchResults[0], inline=True)
            else: # Regular Search
                messageEmbed = discord.Embed(title="Search Results For '" + query + "'")
                
                for i in range(0, len(searchResults)):
                    try:
                        messageEmbed.add_field(name="Result " + str(i + 1), value="https://en.touhouwiki.net/wiki/" + searchResults[i], inline=True)
                    except:
                        print("Skipping Search Result...")
                        pass
            
        if getImage:
            searchImages = 1
            if getUrls == False:
                searchImages = len(searchResults)

            image_info = await get_image(searchResults, searchImages)

            if getUrls == False:
                if image_info == False:
                    await message.channel.send("I wasn't able to find any photos in my library on '" + query + "'.")
                    return
                    
                messageEmbed = discord.Embed(title=image_info.Name.replace("_", " ") + "'s Portrait")

            if image_info:
                messageEmbed.set_image(url=image_info.Url)

        try:
            await message.channel.send(embed=messageEmbed)
        except:
            await message.channel.send("I couldn't find anything in my library for '" + query + "'.")

##################################################TRADING CARDS API############################################################
async def get_all_cards():
    html = await get("https://en.touhouwiki.net/api.php?action=parse&prop=wikitext&format=json&page=Touhoudex_2/Touhoudex_2")

    raw_names = []

    keep_parsing = True
    while keep_parsing:
        try:
            html = html[html.index('}}') + 4:]
            html = html[html.index('{{Touhoudex 2/DexEntry') + 22:]
            for i in range(0, 2):
                html = html[html.index('|') + 1:]
            name = html[:html.index('|')]

            if not name == "None":
                raw_names.append(name)
        except:
            keep_parsing = False

    raw_names = raw_names[:-19] # Cut off misc. characters

    # Okay but add a few more back in though because they're pretty cool
    raw_names.append("TensokuG")
    raw_names.append("Kasen")
    raw_names.append("Satsuki")
    raw_names.append("EMarisa")
    raw_names.append("JKSanae")
    raw_names.append("MPSuika")
    raw_names.append("Ayakashi")

    return raw_names

##################################################TRADING CARDS############################################################
async def get_card(message):
    async with message.channel.typing():
        raw_names = await get_all_cards()

        #rarity_to_discover = 0
        #for i in range(0, 10):
            #if random.randint(0, 10) >= i:
                #rarity_to_discover += 1
            #else:
                #break

        worked = False
        while not worked:
            random_card = randint(0, len(raw_names) - 1)
            #random_card = 6                                    # 1 STAR CHARACTER
            #random_card = 2                                    # 2 STAR CHARACTER
            #random_card = 102                               # 5 STAR CHARACTER
            #random_card = 1                                    # 6 STAR CHARACTER
            #random_card = len(raw_names) - 5 # 7 STAR CHARACTER
            #random_card = len(raw_names) - 6 # 8 STAR CHARACTER
            #random_card = len(raw_names) - 2 # 9 STAR CHARACTER
            #random_card = len(raw_names) - 1 # 10 STAR CHARACTER
            character_html = await get("https://en.touhouwiki.net/wiki/Touhoudex_2/" + raw_names[random_card])

            try: # New Template Parser
                character_name = character_html[character_html.index("vcard") + 4:]
                character_html = character_name
                character_name = character_name[character_name.index("<b>") + 3:character_name.index("</b>")]
                if character_name.endswith("</a>"):
                    character_name = character_name[:-4]                

                try:
                    link = character_name[character_name.index("href=") + 6:]
                    link = link[1:link.index('"')]
                    link = link[link.index("/") + 1:]
                except:
                    link = ""

                try:
                    name = character_name[character_name.index("<"):character_name.index(">") + 1]
                    name = character_name.replace(name, "")
                except:
                    name = character_name
                
                character_image = "Touhoudex 2/" + raw_names[random_card]
                character_image = await get_image(character_image, 1)

                power = character_html[character_html.index("Base Stats"):]
                power = power[power.index("</tr>") + 5:power.index("</table>")]
                power = power[power.rfind("<td>") + 5:]
                power = power[:power.index("<") - 1]

                #Lowest: 330
                #Highest: 720

                rarity_remaining = float(power) - 330
                if rarity_remaining >= 390:
                    rarity = 10
                    rarity_symbol = ":white_circle:"
                else:
                    rarity = 0
                    rarity_symbol = ":large_blue_circle:"
                    while rarity_remaining >= 39:
                        rarity_remaining = rarity_remaining - 39
                        rarity = rarity + 1

                    if rarity >= 4:
                        rarity_symbol = ":red_circle:"

                #rarity = rarity - 1
                        
                #if rarity == 10:
                    #if random.randint(0, 1) == 0:
                        #Code below this line just to make the rarest cards even RARER

                rarity_message = ""
                print("Posting a card with a rarity of "+ str(rarity))
                for i in range(0, 10):
                    if i <= rarity:
                        rarity_message = rarity_message + rarity_symbol
                    else:
                        rarity_message = rarity_message + ":black_circle:"

                #price = int((int(power)*int(power)*int(power)*int(power)/2)/100000000) * (rarity + 1)
                #price = int((int(power)*int(power)*int(power)*2)/1000000) * (rarity + 1)
                price = int((int(power)*int(power)*int(power)*2)/1000000)

                if rarity >= 7:
                    price = price * 2
                if rarity >= 8: 
                    price = price * 2
                if rarity >= 9:
                    price = price * 2
                if rarity == 10:
                    price = price * 2
                
                embed = discord.Embed(title="You found [ " + name + " ]")
                embed.set_image(url=character_image.Url)
                embed.add_field(name="Power:", value=rarity_message, inline=False)
                #embed.add_field(name="Power:", value=power, inline=False)
                embed.add_field(name="Price:", value="$" + str(price), inline=False)
                if len(link) > 0:
                    embed.add_field(name="Page URL:", value="https://en.touhouwiki.net/wiki/" + link, inline=False)
                
                await message.channel.send(embed=embed)
                worked = True
            except: # Outdated Template Parser
                try:
                    print("Outdated template parser not yet implemented!")
                except:
                    print("Error parsing character page")

## Get 'Types' value(s) from character_page ( tokens required(?) )

## Pricing Formula (Rounded Up):
## (total stats * total stats) / 10,000 (?)
## Divided across all tokens needed (?)

##################################################QUOTES############################################################
async def get_quote(message, quotesToGet):
    
    arguments = GetArgumentsFromCommand(message.content)

    gameNumberToUse = ""

    if arguments == False:
        gameNumberToUse = str(randint(6, 16))
    else:
        if int(arguments[0]) < 6 or int(arguments[0]) > 16:
            await message.channel.send("Sorry, I don't think my library has any quotes from that incident!\nPlease give me a game number from 6 to 16.")
            return
        
        gameNumberToUse = arguments[0]
        
    if len(gameNumberToUse) == 1:
        gameNumberToUse = "0" + gameNumberToUse

    if quotesToGet == 0:
        quotesToGet = random.randint(1, 3)

    async with message.channel.typing():

        print("Quote requested from game: " + gameNumberToUse)

        html = await get("https://www.thpatch.net/wiki/Th" + gameNumberToUse)
        try:
            html = html[html.index('<h3><span class="mw-headline" id="Main_Story"'):html.index('id="Spell_cards"')]
        except:
            html = html[html.index('<h3><span class="mw-headline" id="Main_Story"'):html.index('id="Music"')]
        
        gamesStillExist = True
        scenarioLinks = []
        while gamesStillExist:
            try:
                currentGame = html[html.index("<li>"):html.index("</li>")]
                currentGame = currentGame[currentGame.index("href=") + 6:]
                currentGame = currentGame[0:currentGame.index('"')]
                currentGame = currentGame[currentGame.rindex('/') + 1:]
                #print(currentGame)
                scenarioLinks.append(currentGame)
                html = html[html.index("</li>") + 5:]
            except:
                gamesStillExist = False

        quoteWorked = False
        while quoteWorked == False:
            pageWorked = False
            
            while pageWorked == False:
                try:
                    scenarioToUse = scenarioLinks[randint(0, len(scenarioLinks) - 1)]

                    sectionCount = await get("https://www.thpatch.net/w/api.php?action=parse&format=json&prop=sections&page=Th" + gameNumberToUse + "/" + scenarioToUse + "/en")
                    sectionCount = sectionCount[sectionCount.rindex('index') + 8:]
                    sectionCount = int(sectionCount[0:sectionCount.index('"')])

                    htmlUrl = "https://www.thpatch.net/w/api.php?action=parse&format=json&section=" + str(randint(1, sectionCount)) + "&prop=wikitext&page=Th" + gameNumberToUse + "/" + scenarioToUse + "/en"
                    
                    html = await get(htmlUrl)
                    #html = html.encode('unicode_escape').decode('unicode_escape')
                    html = bytes(html, 'ascii').decode('unicode-escape')
                    
                    html = html.replace("\n", " ")
                    html = html[html.index('*') + 4:]

                    pageWorked = True
                except:
                    print("Something went wrong while trying to substring the HTML sections.")
                    pass

            messageList = []

            keepParsingConversation = True
            while keepParsingConversation:
                try:
                    currentMessage = ScriptMessage()
                    html = html[html.index('char=') + 5:]
                    #print(html)
                    currentMessage.Actor = html[0:html.index('|')]
                    
                    html = html[html.index('tl=') + 3:]
                    #print(html)
                    currentMessage.Message = html[0:html.index('}}')]

                    # Convert all misc. renamed action blocks into one unified ACTIONQUOTE block
                    if currentMessage.Actor == "Danmaku.":
                        currentMessage.Actor = "ACTIONQUOTE"
                        currentMessage.Message = ""
                    
                    if (len(currentMessage.Actor) > 0 and len(currentMessage.Message) > 0) or currentMessage.Actor == "ACTIONQUOTE": # Make sure Actor and Message is valid. Or, with an exception of it being an action block
                        messageList.append(currentMessage)
                        #print (currentMessage.Actor)
                        #print(currentMessage.Message)
                        #print("##########")
                    else:
                        print("Could not add '" + currentMessage.Actor + ": " + currentMessage.Message + "'")
                except:
                    keepParsingConversation = False

            fullQuote = ""

            if postFullConversations == True:
                for messageItem in messageList:
                    fullQuote = fullQuote + messageItem.Actor + ": " + messageItem.Message + "\n"
            else:
                randomQuote = -1
                
                while messageList[randomQuote].Actor == "ACTIONQUOTE" or randomQuote == -1: # Did we land on an action block while looking for a starting block? If so, find another starting block
                    if messageList[randomQuote].Actor == "ACTIONQUOTE":
                        print("Randomly landed on an Action Block while trying to find a starting point. Finding another starting point...")
                    randomQuote = random.randint(0, len(messageList) - 1)
                
                i = 0
                while i < quotesToGet:
                    try:
                        if messageList[randomQuote + i].Actor == "ACTIONQUOTE": # If we detect an action block, then the conversation is over
                            print("Landed on an Action Block while creating Message. Ending conversation...")
                            i = quotesToGet + 1
                            break

                        if messageList[randomQuote + i].Message.endswith("...") and i >= quotesToGet - 1: # If the message ends with "..." and we're at the last Quote...
                            quotesToGet = quotesToGet + 1 # Greedily shove one more line in there. You need to resolve the tension, r-right?
                        if messageList[randomQuote + i].Message.endswith(",") and i >= quotesToGet - 1: # If the message ends with "," and we're at the last Quote...
                            quotesToGet = quotesToGet + 1 # Greedily shove one more line in there. You need to resolve the tension, r-right?
                        if messageList[randomQuote + i].Message.endswith("?") and i >= quotesToGet - 1: # If the message ends with "?", and we're at the last Quote...
                            quotesToGet = quotesToGet + 1 # Greedily shove one more line in there. You need to resolve the tension, r-right?
                        
                        messageList[randomQuote + i] = await fix_quote(messageList[randomQuote + i]) # Fix the quote

                        if not i == 0:
                            fullQuote = fullQuote + "\n" # If this isn't the first quote line, post a new line seperator to continue from the last quote line, so this next one will be on a new line.

                        fullQuote = fullQuote + messageList[randomQuote + i].Actor + ": " + messageList[randomQuote + i].Message # Build the quote as 'Actor: Message'
                    except:
                        pass

                    i += 1
                if fullQuote.endswith(" "): # If it ends with a space...
                    fullQuote = fullQuote[0:-1] # What? Why? Get that space out of my sight
                fullQuote = "*" + fullQuote + "*" # Make the message all italic. Ooh, shiny.

            print("Posting from URL: " + htmlUrl) # Print the quote API HTML page we parsed in order to get the conversation. This is mainly for debug purposes so we can check afterwards if need be.

            if allowLargeQuotes == False:
                if len(fullQuote) > 1999:
                    quoteWorked = False
                    
                    print("Quote is long! Trying another one?")
                else:
                    quoteWorked = True
                    
                    await message.channel.send(fullQuote)
                    return
            else:
                quoteWorked = True
                
                remainderQuote = ""

                if len(fullQuote) > 3999:
                    await mesasge.channel.send("Uwaa, onii-chan! T-That quote is too b-big to fit inside m-my m-messagebox~!!")
                    return
                    
                if len(fullQuote) > 1999:
                    remainderQuote = ".. " + fullQuote[1997:]
                    fullQuote = fullQuote[0:1997]
                    fullQuote = fullQuote + " .."

                await message.channel.send(fullQuote)

                if len(remainderQuote) > 1:
                    await message.channel.send(remainderQuote)

##################################################FIX QUOTES############################################################
async def fix_quote(givenMessage):
    if givenMessage.Message.startswith('"') and givenMessage.Message.endswith('"'):
        givenMessage.Message = givenMessage.Message[1:-1]
    if not givenMessage.Message.count('"') % 2 == 0: # If there is an odd number of quotes, as in, one of them was opened and never closed...
        givenMessage.Message = givenMessage.Message.replace('"', '') # Take no chances. Nuke the whole thing, get rid of every quote. I could probably do this better (somehow) and only remove the latest unfinished troublemaking quotation mark, but alas, too much processing time for something that the end-user might not even appreciate, or care about.

    givenMessage.Actor = givenMessage.Actor.replace("TH16", "") # Touhou 16 has quote Actor references that say "TH16Mai", probably to avoid confusion between the other Mai from Touhou 5. Oh well, this is just a pain for us anyway, so let's get rid of "TH16" so it only says "Mai" and displays properly.

    #givenMessage.Message = givenMessage.Message.replace("*", "\*") # lol I tried to escape the asterisks that already existed in the quote here because I thought discord was well-written and would handle it hahahaha what was I thinking
    givenMessage.Message = givenMessage.Message.replace("*", "") # Since we're going to be using italics in our Discord message, having any other asterisks in our quote would break the message. Unfortunately, as a result, we're going to have to get rid of every other asterisk.

    return givenMessage

##################################################STORED DATA HANDLERS############################################################
async def write_data_unsafe(key, data):
    try:
        await data_channel.send("[k]" + key + "[d]" + data)
        return True
    except:
        return False

async def get_data():    
    try:
        return await data_channel.history().flatten()
    except:
        return False

async def search_data(key):
    data = await get_data()
    for data_piece in data:
        if data_piece.content.startswith("[k]" + key + "[d]"):
            return data_piece.content[data_piece.content.index("[d]") + 3:]

    return False

async def write_data(key, data):
    all_data = await get_data()
    for data_piece in all_data:
        if data_piece.content.startswith("[k]" + key + "[d]"):
            print("Data key already exists!")
            return False

    await write_data_unsafe(key, data)
    return True

async def edit_data(key, data):
    all_data = await get_data()
    for data_piece in all_data:
        if data_piece.content.startswith("[k]" + key + "[d]"):
            await data_piece.edit(content="[k]" + key + "[d]" + data)
            return True

    print("Could not find data to edit!")
    return False

async def overwrite_data(key, data):
    all_data = await get_data()
    for data_piece in all_data:
        if data_piece.content.startswith("[k]" + key + "[d]"):
            await data_piece.edit(content="[k]" + key + "[d]" + data)
            return True

    await write_data_unsafe(key, data)
    return False

async def delete_data(key):
    all_data = await get_data()
    for data_piece in all_data:
        if data_piece.content.startswith("[k]" + key + "[d]"):
            await data_piece.delete()
            return True

    print("Could not find data to delete!")
    return False

##################################################START############################################################
@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.online, activity=discord.Game(prefix + "help for Help!"))

    global allow_commands

    global data_guild
    global data_channel

    global suggestions_guild
    global suggestions_channel

    data_guild = client.get_guild(int(data_guild_id))
    data_channel = data_guild.get_channel(int(data_channel_id))

    suggestions_guild = client.get_guild(int(suggestions_guild_id))
    suggestions_channel = suggestions_guild.get_channel(int(suggestions_channel_id))
                
    allow_commands = True # Now we're truly ready to begin taking commands
    
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_message(message):
    if not allow_commands:
        return
    
    if message.author.bot:
        return

    if not closed_access_users == None:
        if not str(message.author.id) in closed_access_users:
            print("Blocked access from non closed-access user")
            return
    
    lowercaseMessage = message.content.lower()

    if lowercaseMessage.startswith(prefix):
        if len(lowercaseMessage) > len(prefix):
            if lowercaseMessage[len(prefix)] != " ":
                if runningCommandsArray.count(message.author.id) > 1:
                    await message.channel.send(cooldown_message)
                    return
                else:
                    runningCommandsArray.append(message.author.id)
                    await handle_command(message, lowercaseMessage)
                    runningCommandsArray.remove(message.author.id)
                    print("Handled Command '" + message.content + "' Sent By '" + str(message.author) + "'\n")

async def handle_command(message, lowercaseMessage):
    print("Handling Command '" + message.content + "' Sent By '" + str(message.author) + "'")
    
    try:
        #if lowercaseMessage == prefix + 'ping':
            #await message.channel.send("Pong!")
            #return
        #if lowercaseMessage == prefix + 'exception':
            #raise ValueError('Manual test exception thrown.')
            #return
        #if message.content == prefix + 'test':
            #counter = 0
            #tmp = await client.send_message(message.channel, 'Calculating messages...')
            #async for log in client.logs_from(message.channel, limit=100):
                #if log.author == message.author:
                    #counter += 1

            #await client.edit_message(tmp, 'You have {} messages.'.format(counter))
        #if message.content == prefix + 'sleep':
            #await asyncio.sleep(5)
            #await client.send_message(message.channel, 'Done sleeping')
        if lowercaseMessage == prefix + 'help':
            await message.channel.send(helpMessage)
            return
        if lowercaseMessage == prefix + 'info':
            await message.channel.send(aboutMessage % (str(discord.__version__), round((time.time() - startTime) / 60, 1), str(len(client.guilds))))
            return
        if lowercaseMessage.startswith(prefix + 'suggest'):
            arguments = GetArgumentsFromCommand(message.content)

            if arguments == False:
                await message.channel.send("Either I'm perfect, or you forgot to type in a suggestion.")
                return

            await suggestions_channel.send("Suggestion Received from '" + str(message.author) + "':\n'" + arguments[0] + "'")
            await message.channel.send("Thank you! I'll try my best to improve the library's services!")
            return
        if lowercaseMessage.startswith(prefix + 'image'):
            await PostImage(message, "safe", "touhou", "https://gelbooru.com/index.php")
            return
        if lowercaseMessage.startswith(prefix + 'nsfwimage'):
            isok = True

            try:
                if not message.channel.is_nsfw(): # If it isn't an NSFW channel, don't allow it
                    isok = False
            except:
                pass

            if isok:
                await PostImage(message, "explicit", "touhou", "https://gelbooru.com/index.php")
                return
            else:
                if random.randint(0,1) == 0:
                    await message.channel.send("I-I don't think this is the kind of channel for THAT.")
                    return
                else:
                    await message.channel.send("S-Shouldn't we do that kind of l-lewd stuff s-somewhere else?")
                    return
        if lowercaseMessage.startswith(prefix + 'quote'):
            await get_quote(message, 0)
            return
        if lowercaseMessage.startswith(prefix + 'search'):
            await get_search(message, True, False)
            return
        if lowercaseMessage.startswith(prefix + 'portrait'):
            await get_search(message, False, True)
            return
        if lowercaseMessage.startswith(prefix + 'lookup'):
            await get_search(message, True, True)
            return
        if lowercaseMessage == prefix + 'card':
            i = 0
            for command in runningCommandsArray:
                if message.author.id == command:
                    i = i + 1
                if i >= 2:
                    await message.channel.send(cooldown_message)
                    return

            #if await write_data("daily_pack_cooldown-" + str(message.author.id), str(time.time())) == False:
                #if (((time.time() - float(await search_data("daily_pack_cooldown-" + str(message.author.id)))) / 60) / 60) >= 24:
                    #await edit_data("daily_pack_cooldown-" + str(message.author.id), str(time.time()))
                #else:
                    #await message.channel.send("You've already received your daily card!")
                    #return

            await get_card(message)
            return
        
        #await message.channel.send("Sorry, but I'm not quite sure what you're asking me to do.")
    except Exception as e:
        print(e)
        await message.channel.send("Whoops! Something went wrong in my head while trying to figure that one out...")

print("Now starting with discord.py Version: '" + str(discord.__version__) + "'\n")

setup_discord_bots_org_api(client) # Setup Discord Bots Org API
client.run(token) # Start the bot with the Token
