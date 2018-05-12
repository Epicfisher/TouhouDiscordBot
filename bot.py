import os
import time
import discord
import aiohttp
import asyncio
import random
import socket
from urllib.request import urlopen
from random import randint

class ScriptMessage:
    Actor = ""
    Message = ""

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

startTime = time.time()

try:
    with open('token.txt', 'r') as myfile:
        token = myfile.read().replace('\n', '')
except:
    try:
        token = os.environ['TOKEN']
    except:
        print ("APPLICATION HALTED DUE TO CRITICAL ERROR:\n\nNo Bot Token specified in either a 'token.txt' file or 'TOKEN' System Environment Variable.")
        
        while True:
            pass

prefix = 'k.'

argumentChar = ' '
argumentKillChar = ''
argumentSeperator = ','

helpMessage = """```
~Patchouli Knowledge Help~

~~~General Commands~~~
""" + prefix + """help - You're currently reading this!
""" + prefix + """about - Information about me. Wow. Very interesting.
""" + prefix + """ping - Test command. Responds "Pong!"

~~~Image Commands~~~
""" + prefix + """image - Gets a Touhou image from Gelbooru.
""" + prefix + """nsfwimage - Gets a NSFW Touhou image. NSFW Channel required.

~~~Quote Commands~~~
""" + prefix + """quote - Gets a quote from a random Touhou game.
""" + prefix + """quote""" + argumentChar + """6""" + argumentKillChar + """ - Gets a quote from Touhou 6.

~~~Search Commands~~~
""" + prefix + """search""" + argumentChar + """Reimu""" + argumentKillChar + """ - Searches for 'Reimu' pages on touhouwiki.net.
""" + prefix + """portrait""" + argumentChar + """Reimu""" + argumentKillChar + """ - Searches for a 'Reimu' portrait.
""" + prefix + """lookup""" + argumentChar + """Reimu""" + argumentKillChar + """ - Searches for a 'Reimu' page and portrait.

```"""

aboutMessage = """```
~About Patchouli Knowledge~

- Runs entirely in Python 3, with the use of discord.py.
- So far I have stayed up reading for %s minutes.
- I'm currently loaning my books to %s servers.
- Made by @Epicfisher#6763.

```"""

allowLargeQuotes = False
postFullConversations = False

client = discord.Client()

conn = aiohttp.TCPConnector( # Initialise async web downloading connector
    family=socket.AF_INET,
    verify_ssl=False,
)

#async def oldget(url):    
    #async with aiohttp.ClientSession() as session:
        #async with session.get(url) as resp:
            #return await resp.text()

    #return await r.text()

#html = urlopen(APILink + "?page=dapi&s=post&q=index&limit=1&json=1&pid=" + str(randint(0, 20000)) + "&tags=" + tags).read().decode('utf-8')

async def get(url): # Asyncronously download a web-page's HTML.
    conn = aiohttp.TCPConnector( # Reset our connector incase of shutdown
        family=socket.AF_INET,
        verify_ssl=False,
    )
    
    async with aiohttp.ClientSession(connector=conn) as session:
        async with session.get(url) as resp:
            return await resp.text()

    return await r.text()

##################################################IMAGES############################################################
async def PostImage(postChannel, tags, APILink):
    html = await get(APILink + "?page=dapi&s=post&q=index&limit=1&json=1&pid=" + str(randint(0, 20000)) + "&tags=" + tags)

    client.send_typing(postChannel)
    await asyncio.sleep(10)

    try:
        fileUrl = html[html.index('file_url":"') + 11 : - 3]
        fileUrl = fileUrl.replace("\/", "/")
        fileUrl = fileUrl[0:fileUrl.index('"')]
        
        source = html[html.index('source":"') + 9:]
        source = source[:source.index('"')]
        source = source.replace("\/", "/")
        
        print("Posting Image: " + fileUrl)
        print("Image Source: " + source)
    except:
        await client.send_message(postChannel, "I couldn't find an image!")

        return
    
    messageEmbed = discord.Embed()
    messageEmbed.set_image(url=fileUrl)
    messageEmbed.add_field(name="Image URL", value=fileUrl, inline=False)
    if len(source) > 0:
        messageEmbed.add_field(name="Image Source",value=source, inline=False)
    #else:
        #messageEmbed.add_file(name="Image Source",value="None", inline=False)
        #pass
    
    await client.send_message(postChannel, embed=messageEmbed)

##################################################SEARCH############################################################
async def get_search(message, getUrls, getImage):
    arguments = GetArgumentsFromCommand(message.content)

    if arguments == False:
        await client.send_message(message.channel, "You're going to have to give me something for me to look for...")

        return
    else:
        query = arguments[0]

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

    searchResults.sort(key=len) # Sort results by length, smallest first. This is going to be tricky, as it could mess stuff up, but all in all it works better for the smaller queries people run,  like 'ZUN', maybe not so much for longer or more complicated vague queries. Oh well, this is just the kind of sacrifice tthat must be made though, I don't see any other way around this issue.

    if len(searchResults) < 1:
            await client.send_message(message.channel, "I couldn't find anything in my library for '" + query + "'.")
        
            return
    if getUrls:
        if getUrls and getImage:
            messageEmbed = discord.Embed(title="Lookup Result For '" + query + "'")
            
            messageEmbed.add_field(name="Page URL", value="https://en.touhouwiki.net/wiki/" + searchResults[0], inline=True)
        else:
            messageEmbed = discord.Embed(title="Search Results For '" + query + "'")
            
            for i in range(0, 5):
                try:
                    messageEmbed.add_field(name="Result " + str(i + 1), value="https://en.touhouwiki.net/wiki/" + searchResults[i], inline=True)
                except:
                    print("Skipping Search Result...")
                    pass
        
    if getImage:
        searchImages = 1
        if getImage and getUrls == False:
            searchImages = len(searchResults)
        
        for i in range(0, searchImages):
            json = await get("https://en.touhouwiki.net/wiki/" + searchResults[i])

            try:
                json = json[json.index('infobox'):]
                json = json[json.index('<a href="/wiki/File:') + 9:]
                json = json[:json.index("</a>")]
                file = json[json.index('File:'):json.index('"')]

                json = await get("https://en.touhouwiki.net/api.php?action=query&titles=" + file + "&prop=imageinfo&iiprop=url&format=json")

                json = json[json.index('"url":"') + 7:]
                file = json[:json.index('"')]

                if getUrls == False and getImage:
                    messageEmbed = discord.Embed(title=searchResults[i].replace("_", " ") + "'s Portrait")

                messageEmbed.set_image(url=file)

                break #At this point, we should have our working image. Ensure the for loop is killed.
            except:
                if getImage and getUrls == False:
                    if i >= searchImages:
                        await client.send_message(message.channel, "I wasn't able to find any photos in my library on '" + query + "'.")
                        
                        return
                    else:
                        print("No Photo for '" + searchResults[i].replace("_", " ") + "'. Moving on...")

    try:
        await client.send_message(message.channel, embed=messageEmbed)
    except:
        await client.send_message(message.channel, "I couldn't find anything in my library for '" + query + "'")

##################################################QUOTES############################################################
async def get_quote(message, quotesToGet):
    arguments = GetArgumentsFromCommand(message.content)

    gameNumberToUse = ""

    if arguments == False:
        gameNumberToUse = str(randint(6, 16))
    else:
        if int(arguments[0]) < 6 or int(arguments[0]) > 16:
            await client.send_message(message.channel, "Sorry, I don't think my library has any quotes from that incident!\nPlease enter a game number from 6 to 16!")
            return
        
        gameNumberToUse = arguments[0]
        
    if len(gameNumberToUse) == 1:
        gameNumberToUse = "0" + gameNumberToUse

    if quotesToGet == 0:
        quotesToGet = random.randint(1, 3)

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

                #if currentMessage.Message.startswith('"'):
                    #currentMessage.Message = currentMessage.Message[1:]
                    #pass
                #if currentMessage.Message.endswith('"'):
                    #currentMessage.Message = currentMessage.Message[:-1]
                    #pass
                #if currentMessage.Message.startswith('"') and currentMessage.Message.endswith('"'):
                    #currentMessage.Message = currentMessage.Message[1:-1]
                
                if (len(currentMessage.Actor) > 0 and len(currentMessage.Message) > 0) or currentMessage.Actor == "Danmaku.":
                    messageList.append(currentMessage)
                    #print (currentMessage.Actor)
                    #print(currentMessage.Message)
                    #print("##########")
            except:
                keepParsingConversation = False

        fullQuote = ""

        if postFullConversations == True:
            for messageItem in messageList:
                fullQuote = fullQuote + messageItem.Actor + ": " + messageItem.Message + "\n"
        else:
            randomQuote = 0
            
            while messageList[randomQuote].Actor == "Danmaku.":
                randomQuote = random.randint(0, len(messageList) - 1)

            messageList[randomQuote] = await fix_quote(messageList[randomQuote])                
            fullQuote = fullQuote + messageList[randomQuote].Actor + ": " + messageList[randomQuote].Message
            
            if quotesToGet > 1:
                for i in range(0, quotesToGet - 1): 
                    try:
                        if messageList[randomQuote + 1 + i].Actor == "Danmaku.": # If we detect a Danmaku block, then the conversation is over, as thery're obviously fighting
                            i = quotesToGet + 1
                        
                        if messageList[randomQuote + 1 + i].Message.endswith("...") and i >= quotesToGet - 1:
                            pass
                        elif messageList[randomQuote + 1 + i].Message.endswith("...") and i < quotesToGet - 1 and i >= quotesToGet - 2:
                            quotesToGet = quotesToGet + 1
                        elif messageList[randomQuote + 1 + i].Message.endswith(",") and i>= quotesToGet - 1:
                            quotesToGet = quotesToGet + 1
                        else: # It's all good
                            messageList[randomQuote + 1 + i] = await fix_quote(messageList[randomQuote + 1 + i])
                
                            fullQuote = fullQuote + "\n" + messageList[randomQuote + 1 + i].Actor + ": " + messageList[randomQuote + 1 + i].Message
                    except:
                        pass
            if fullQuote.endswith(" "):
                fullQuote = fullQuote[0:-1]
            fullQuote = "*" + fullQuote + "*"

        print("Posting from URL: " + htmlUrl)

        if allowLargeQuotes == False:
            if len(fullQuote) > 1999:
                quoteWorked = False
                
                print("Quote is long! Trying another one?")
            else:
                quoteWorked = True
                
                await client.send_message(message.channel, fullQuote)
                return
        else:
            quoteWorked = True
            
            remainderQuote = ""

            if len(fullQuote) > 3999:
                await client.send_message(message.channel, "Uwaa, onii-chan! T-That quote is too b-big to fit inside m-my m-messagebox~!!")
                return
                
            if len(fullQuote) > 1999:
                remainderQuote = ".. " + fullQuote[1997:]
                fullQuote = fullQuote[0:1997]
                fullQuote = fullQuote + " .."

            await client.send_message(message.channel, fullQuote)

            if len(remainderQuote) > 1:
                await client.send_message(message.channel, remainderQuote)

##################################################FIX QUOTES############################################################
async def fix_quote(givenMessage):
    if givenMessage.Message.startswith('"') and givenMessage.Message.endswith('"'):
        givenMessage.Message = givenMessage.Message[1:-1]
    if not givenMessage.Message.count('"') % 2 == 0:
        givenMessage.Message = givenMessage.Message.replace('"', '')

    givenMessage.Actor = givenMessage.Actor.replace("TH16", "")

    return givenMessage

##################################################START############################################################
@client.event
async def on_ready():
    await client.change_status(game=discord.Game(name = prefix + "help for Help!"))
    
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_message(message):
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
    if message.author.id == client.user.id:
        return
    
    lowercaseMessage = message.content.lower()

    print("Received Message '" + message.content + "'")
    
    if lowercaseMessage == prefix + 'help':
        await client.send_message(message.author, helpMessage)
    if lowercaseMessage == prefix + 'about':
        await client.send_message(message.author, aboutMessage % (round((time.time() - startTime) / 60, 1), str(len(client.servers))))
        #(round(round(time.time() - startTime, 1) / 60, 1))))        
    if lowercaseMessage == prefix + 'ping':
        await client.send_message(message.channel, "Pong!")
    if lowercaseMessage.startswith(prefix + 'image'):
        await PostImage(message.channel, "rating:safe%20touhou", "https://gelbooru.com/index.php")
    if lowercaseMessage == prefix + 'nsfwimage':
        if message.channel.is_private:
            await PostImage(message.channel, "rating:explicit%20touhou", "https://gelbooru.com/index.php")
        elif message.channel.is_nsfw:
            await PostImage(message.channel, "rating:explicit%20touhou", "https://gelbooru.com/index.php")
        else:
            if random.randint(0,1) == 0:
                await client.send_message(message.channel, "I-I don't think this is the kind of channel for THAT.")
            else:
                await client.send_message(message.channel, "S-Shouldn't we do that kind of l-lewd stuff s-somewhere else?")
    if lowercaseMessage.startswith(prefix + 'quote'):
        await get_quote(message, 0)
    if lowercaseMessage.startswith(prefix + 'search'):
        await get_search(message, True, False)
    if lowercaseMessage.startswith(prefix + 'portrait'):
        await get_search(message, False, True)
    if lowercaseMessage.startswith(prefix + 'lookup'):
        await get_search(message, True, True)
    
client.run(token) # Start the bot with the Token