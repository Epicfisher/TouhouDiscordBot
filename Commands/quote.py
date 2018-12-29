import commands

###

import bot
from random import randint

class ScriptMessage:
    Actor = ""
    Message = ""

async def get_quote(message, quotesToGet):
    arguments = commands.GetArgumentsFromCommand(message.content)

    gameNumberToUse = ""

    invalid_argument = False

    if arguments == False:
        gameNumberToUse = str(randint(6, 16))
    else:
        try:
            if int(arguments[0]) < 6 or int(arguments[0]) > 16:
                invalid_argument = True
                pass
        except:
            invalid_argument = True
            pass

        if invalid_argument:
            await message.channel.send("Sorry, I don't think my library has any quotes from that incident!\nPlease give me a game number from 6 to 16.")
            return

        gameNumberToUse = arguments[0]

    if len(gameNumberToUse) == 1:
        gameNumberToUse = "0" + gameNumberToUse

    if quotesToGet == 0:
        quotesToGet = randint(1, 3)

    async with message.channel.typing():

        print("Quote requested from game: " + gameNumberToUse)

        html = await bot.get("https://www.thpatch.net/wiki/Th" + gameNumberToUse)
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

                    sectionCount = await bot.get("https://www.thpatch.net/w/api.php?action=parse&format=json&prop=sections&page=Th" + gameNumberToUse + "/" + scenarioToUse + "/en")
                    sectionCount = sectionCount[sectionCount.rindex('index') + 8:]
                    sectionCount = int(sectionCount[0:sectionCount.index('"')])

                    htmlUrl = "https://www.thpatch.net/w/api.php?action=parse&format=json&section=" + str(randint(1, sectionCount)) + "&prop=wikitext&page=Th" + gameNumberToUse + "/" + scenarioToUse + "/en"

                    html = await bot.get(htmlUrl)
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

            if bot.postFullConversations == True:
                for messageItem in messageList:
                    fullQuote = fullQuote + messageItem.Actor + ": " + messageItem.Message + "\n"
            else:
                randomQuote = -1

                while messageList[randomQuote].Actor == "ACTIONQUOTE" or randomQuote == -1: # Did we land on an action block while looking for a starting block? If so, find another starting block
                    if messageList[randomQuote].Actor == "ACTIONQUOTE":
                        print("Randomly landed on an Action Block while trying to find a starting point. Finding another starting point...")
                    randomQuote = randint(0, len(messageList) - 1)

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

            if bot.allowLargeQuotes == False:
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

async def fix_quote(givenMessage):
    if givenMessage.Message.startswith('"') and givenMessage.Message.endswith('"'):
        givenMessage.Message = givenMessage.Message[1:-1]
    if not givenMessage.Message.count('"') % 2 == 0: # If there is an odd number of quotes, as in, one of them was opened and never closed...
        givenMessage.Message = givenMessage.Message.replace('"', '') # Take no chances. Nuke the whole thing, get rid of every quote. I could probably do this better (somehow) and only remove the latest unfinished troublemaking quotation mark, but alas, too much processing time for something that the end-user might not even appreciate, or care about.

    givenMessage.Actor = givenMessage.Actor.replace("TH16", "") # Touhou 16 has quote Actor references that say "TH16Mai", probably to avoid confusion between the other Mai from Touhou 5. Oh well, this is just a pain for us anyway, so let's get rid of "TH16" so it only says "Mai" and displays properly.

    #givenMessage.Message = givenMessage.Message.replace("*", "\*") # lol I tried to escape the asterisks that already existed in the quote here because I thought discord was well-written and would handle it hahahaha what was I thinking
    givenMessage.Message = givenMessage.Message.replace("*", "") # Since we're going to be using italics in our Discord message, having any other asterisks in our quote would break the message. Unfortunately, as a result, we're going to have to get rid of every other asterisk.

    if '|' in givenMessage.Message: # Some quotes on the site like to have comments or other additional notes included within their Quote Messages. We don't really *want* those, so we're going to remove them.
        givenMessage.Message = givenMessage.Message[:givenMessage.Message.index('|')] # Remove them.

    return givenMessage

async def quote(message):
    await get_quote(message, 0)
    return

###

commands.Add("quote%", quote)
