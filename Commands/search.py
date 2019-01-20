import commands

###

import bot
import discord

use_old_query = False

async def get_search_results(query, quantity):
    searchResults = []

    if use_old_query:
        json = await bot.get("https://en.touhouwiki.net/api.php?action=query&list=search&srprop=redirecttitle&srwhat=title&format=json&srsearch=" + query + "&utf8=")
        json = json[json.index('"search":'):len(json)]

        while True:
            try:
                json = json[json.index('"title"') + 9:]
                searchResults.append(json[:json.index('"')].replace(" ", "_"))
                #print (json + "\n" + title + "\n")
            except:
                break
    else:
        json = await bot.get("https://en.touhouwiki.net/api.php?action=opensearch&search=" + query + "&limit=" + str(quantity) + "&redirects=resolve&format=json&utf8=")
        json = json[1:]
        for i in range(0, 3):
            json = json[json.index("[") + 1:]

        while True:
            try:
                json = json[1:]
                searchResults.append(json[json.index("/wiki/") + 6:json.index('"')])
                print("Found " + (json[json.index("/wiki/") + 6:json.index('"')]))

                json = json[json.index('"') + 2:]
                if json.startswith("]"):
                    break
            except:
                break

    if len(searchResults) > 1:
        #searchResults.sort(key=len) # Sort total results by length, smallest first. This is tricky, as it could mess stuff up, but all in all it works better for the smaller queries people run,  like 'ZUN', but not really so for more longer and vague queries. Oh well, this is just the kind of sacrifice that has to be made I guess, I don't see any other way around this issue, unless we do something like sort by popularity or 'clicks', which the Wikimedia API doesn't even have support for.
        ''' # Uncomment me if you want results sorted by the first set of numbers included within their titles. I don't think the functionality for this is actually needed. I guess it helps to keep it more literal and logical by not using this, but I've commented it out incase I change my mind in the future, since this is overall more simplistic and 'user-friendly'.

        if not any(char.isdigit() for char in query) and any(char.isdigit() for char in searchResults[0]):
            multiple_number_results_sort = []
            multiple_number_results_sort_numbers = []
            common_length = len(searchResults[0])
            for i in range(0, len(searchResults)):
                if len(searchResults[i]) == common_length:
                    multiple_number_results_sort.append(searchResults[i])
                else:
                    break

            if len(multiple_number_results_sort) > 1:
                searchResults = searchResults[len(multiple_number_results_sort):] # Cut off unsorted results. We're going to do this ourselves.

                for search_result in multiple_number_results_sort:
                    for i in range(0, len(search_result)):
                        if search_result[i].isdigit():
                            multiple_number_results_sort_numbers.append(search_result[i])
                            break

                multiple_number_results_sort = [x for y, x in sorted(zip(multiple_number_results_sort_numbers, multiple_number_results_sort))] # ouch, no idea what this is doing (see: https://stackoverflow.com/questions/6618515/sorting-list-based-on-values-from-another-list)

                searchResults = multiple_number_results_sort + searchResults

        '''

    return searchResults

async def get_search(message, getUrls, getImage):
    arguments = commands.GetArgumentsFromCommand(message.content)

    force_image = True

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
        if len(searchResults) == 1:
            getImage = True
            force_image = False
            searchResults = [searchResults[0]]

        if getUrls and not getImage: # Regular Search
            messageEmbed = discord.Embed(title="Search Results For '" + query + "'", color=bot.hex_color)

            for i in range(0, len(searchResults)):
                try:
                    messageEmbed.add_field(name="Result " + str(i + 1), value="https://en.touhouwiki.net/wiki/" + searchResults[i], inline=False)
                except:
                    print("Skipping Search Result...")
                    pass

        if getImage:
            #searchImages = 1
            #if getUrls == False:
            searchImages = len(searchResults)

            if getUrls: # Lookup
                image_info = await bot.get_image(searchResults, searchImages, force_image, True)
            if not getUrls: # Portrait
                image_info = await bot.get_image(searchResults, searchImages, force_image, False)

            if not image_info == False:
                if getUrls: # Lookup
                    messageEmbed = discord.Embed(title=image_info.Name.replace("_", " "), color=bot.hex_color)

                    messageEmbed.add_field(name="Page URL", value="https://en.touhouwiki.net/wiki/" + searchResults[0], inline=False)
                    if not image_info.Summary == "":
                        messageEmbed.add_field(name="Summary", value=image_info.Summary.replace("_", " "), inline=False)
                else: # Portrait
                    messageEmbed = discord.Embed(title=image_info.Name.replace("_", " ") + "'s Portrait", color=bot.hex_color)
            else:
                if not getUrls:
                    await message.channel.send("I wasn't able to find any photos in my library on '" + query + "'.")
                    return

            if image_info:
                messageEmbed.set_image(url=image_info.Url)

        try:
            await message.channel.send(embed=messageEmbed)
        except:
            await message.channel.send("I couldn't find anything in my library for '" + query + "'.")

async def search(message):
    await get_search(message, True, False)
    return

async def portrait(message):
    await get_search(message, False, True)
    return

async def lookup(message):
    await get_search(message, True, True)
    return

###

commands.Add("search%", search)
commands.Add("portrait%", portrait)
commands.Add("lookup%", lookup)
