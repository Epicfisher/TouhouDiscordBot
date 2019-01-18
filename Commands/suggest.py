import commands

###

import bot

async def suggest(message):
    if bot.suggestions_channel == None or bot.suggestions_guild == None:
        await message.channel.send("Our inbox for Suggestions are currently closed. Sorry!")
        return

    arguments = commands.GetArgumentsFromCommand(message.content)

    if arguments == False:
        await message.channel.send("Either I'm perfect, or you forgot to type in a suggestion.")
        return

    await bot.suggestions_channel.send("Suggestion Received from '" + str(message.author) + "':\n'" + arguments[0] + "'")
    await message.channel.send("Thank you! I'll try my best to improve the library's services!")
    return

###

commands.Add("suggest%", suggest)
