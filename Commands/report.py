import commands

###

import bot

async def report(message):
    if bot.reports_channel == None or bot.reports_guild == None:
        await message.channel.send("Our inbox for Reports are currently closed. Sorry!")
        return

    arguments = commands.GetArgumentsFromCommand(message.content)

    if arguments == False:
        await message.channel.send("Either I'm perfect, or you forgot to type in a bug report.")
        return

    report = ""
    for i in range(0, len(arguments)):
        report = report + arguments[i]
        if i < len(arguments) - 1:
            report = report + bot.argumentSeperator

    await bot.reports_channel.send(":warning: Report Received from '" + str(message.author) + "':\n'" + report + "'")
    await message.channel.send("Thank you! I'll try my best to improve the library's services!")
    return

###

commands.Add("report%", report)
