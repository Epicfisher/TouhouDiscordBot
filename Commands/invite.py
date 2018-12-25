import commands

###

import bot

async def invite(message):
    await message.channel.send("Invite me to your server to use my library's services wherever you'd like!\n<https://discordapp.com/oauth2/authorize?client_id=" + str(bot.client.user.id) + "&scope=bot>")
    return

###

commands.Add("invite", invite)
