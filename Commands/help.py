import commands

###

import bot
from discord import DMChannel

horizontal = 67

def createHelpHeader(name):
    return "===== " + name + " ====="

    # Currently unused to the courtesy of mobile users. Creates help headers which are exactly long enough to fit all text within
    '''
    dashes = horizontal - len(name)
    dashes_str1 = ""
    dashes_str2 = ""
    for i in range(0, int(dashes / 2)):
        dashes_str1 += '~'
    dashes_str2 = dashes_str1
    while len(dashes_str1) + len(name) + len(dashes_str2) >= horizontal:
        dashes_str2 = dashes_str2[:-1]

    return dashes_str1 + name + dashes_str2
    '''

'''
betaHelpMessage = """```
~Patchouli Knowledge Beta Help~

[ Feedback, suggestions and detailed bug-reports for these
  commands are all more than welcome, and I will try my best
  to read and consider every one I get. You can send me your
  thoughts and feedback through the '""" + bot.prefix + """suggest' Command,
  should you have any, and any bug reports through the
  '""" + bot.prefix + """report' Command. Thanks! ]

Beta commands goes here
```"""
'''

musicHelpMessage = """```asciidoc
= Patchouli Knowledge Music Help =

PLEASE NOTE MUSIC PLAYBACK IS NOT 24/7 AND COULD RESTART

(Please report any bugs found using
the '""" + bot.prefix + """report' command. Thanks!)

""" + createHelpHeader("Music Operator Commands ('Manage Channels' Required)") + """
""" + bot.prefix + """forceskip :: Forcefully Skips the currently playing Song.
""" + bot.prefix + """togglequeue :: Enables or disables the Song Queue.
""" + bot.prefix + """volume""" + bot.argumentChar + """0.5""" + bot.argumentKillChar + """ :: Changes Volume to 0.5, out of a maximum of 1.0.

""" + createHelpHeader("Music Playback Commands") + """
""" + bot.prefix + """play :: Plays Random Touhou 6+ Music and Arranges.
""" + bot.prefix + """play""" + bot.argumentChar + """6""" + bot.argumentKillChar + """ :: Autoplays Random Touhou 6 Music + Arranges.
""" + bot.prefix + """play""" + bot.argumentChar + """pc98""" + bot.argumentKillChar + """ :: Autoplays Random Touhou 1-5 Music + Arranges.
""" + bot.prefix + """play""" + bot.argumentChar + """all""" + bot.argumentKillChar + """ :: Autoplays All Random Touhou Music + Arranges.

""" + bot.prefix + """play""" + bot.argumentChar + """arrange""" + bot.argumentKillChar + """ :: Autoplays Random Touhou 6+ Arranges.
""" + bot.prefix + """play""" + bot.argumentChar + """arrange/6""" + bot.argumentKillChar + """ :: Autoplays Random Touhou 6 Arranges.
""" + bot.prefix + """play""" + bot.argumentChar + """arrange/pc98""" + bot.argumentKillChar + """ :: Autoplays Random Touhou 1-5 Arranges.
""" + bot.prefix + """play""" + bot.argumentChar + """arrange/all""" + bot.argumentKillChar + """ :: Autoplays All Random Touhou Arranges.

""" + bot.prefix + """play""" + bot.argumentChar + """ost""" + bot.argumentKillChar + """ :: Autoplays Random Touhou 6+ Music.
""" + bot.prefix + """play""" + bot.argumentChar + """ost/6""" + bot.argumentKillChar + """ :: Autoplays Random Touhou 6 Music.
""" + bot.prefix + """play""" + bot.argumentChar + """ost/pc98""" + bot.argumentKillChar + """ :: Autoplays Random Touhou 1-5 Music.
""" + bot.prefix + """play""" + bot.argumentChar + """ost/all""" + bot.argumentKillChar + """ :: Autoplays All Random Touhou Music.

""" + createHelpHeader("Music Info Commands") + """
""" + bot.prefix + """playing :: View the currently playing Song.

""" + createHelpHeader("Music Control Commands") + """
""" + bot.prefix + """stop :: Stops playing Music and leaves the Voice Channel.
""" + bot.prefix + """stopafter :: Stops Music after finishing current Song.
""" + bot.prefix + """skip :: Votes to Skip the currently playing Song.
""" + bot.prefix + """pause :: Pauses or unpauses the currently playing Song.

""" + createHelpHeader("Music Queue Commands") + """
""" + bot.prefix + """queue :: View the current Song Queue.

""" + bot.prefix + """queue""" + bot.argumentChar + """arrange""" + bot.argumentKillChar + """ :: Queues a Random Touhou 6+ Arrange.
""" + bot.prefix + """queue""" + bot.argumentChar + """arrange/pc98""" + bot.argumentKillChar + """ :: Queues a Random Touhou 1-5 Arrange.
""" + bot.prefix + """queue""" + bot.argumentChar + """arrange/6""" + bot.argumentKillChar + """ :: Queues a Random Touhou 6 Arrange.
""" + bot.prefix + """queue""" + bot.argumentChar + """arrange/all""" + bot.argumentKillChar + """ :: Queues a Random Touhou Arrange.

""" + bot.prefix + """queue""" + bot.argumentChar + """ost""" + bot.argumentKillChar + """ :: Queues a Random Touhou 6+ Song.
""" + bot.prefix + """queue""" + bot.argumentChar + """ost/pc98""" + bot.argumentKillChar + """ :: Queues a Random Touhou 1-5 Song.
""" + bot.prefix + """queue""" + bot.argumentChar + """ost/6""" + bot.argumentKillChar + """ :: Queues a Random Touhou 6 Song.
""" + bot.prefix + """queue""" + bot.argumentChar + """ost/all""" + bot.argumentKillChar + """ :: Queues a Random Touhou Song.
```"""

imageHelpMessage = """```asciidoc
= Patchouli Knowledge Image Help =

""" + createHelpHeader("Image Commands") + """
""" + bot.prefix + """image :: Gets a random Touhou image from Gelbooru.
""" + bot.prefix + """image""" + bot.argumentChar + """Cirno Frog""" + bot.argumentKillChar + """ :: Gets an image of 'Cirno' and a 'Frog'.
""" + bot.prefix + """imagewith""" + bot.argumentChar + """Patchouli""" + bot.argumentKillChar + """ :: Gets an image with 'Patchouli'.

""" + bot.prefix + """lewd :: Gets a Lewd Touhou image. NSFW Channel required.
""" + bot.prefix + """lewd""" + bot.argumentChar + """Sakuya""" + bot.argumentKillChar + """ :: Gets a Lewd image of 'Sakuya'.
""" + bot.prefix + """lewdwith""" + bot.argumentChar + """Alice""" + bot.argumentKillChar + """ :: Gets a Lewd image with 'Alice'.

""" + bot.prefix + """nsfw :: Gets a NSFW Touhou image. NSFW Channel required.
""" + bot.prefix + """nsfw""" + bot.argumentChar + """Reimu""" + bot.argumentKillChar + """ :: Gets an NSFW image of 'Reimu'.
""" + bot.prefix + """nsfwwith""" + bot.argumentChar + """Marisa""" + bot.argumentKillChar + """ :: Gets an NSFW image with 'Marisa'.
```"""

'''
""" + bot.prefix + """betahelp - Try out beta features and provide suggestions!
~Patchouli Knowledge Help~
~~~~~General Commands~~~~~
'''

helpMessage = """```asciidoc
= Patchouli Knowledge Help =

""" + createHelpHeader("General Commands") + """
""" + bot.prefix + """help :: You're currently reading this!
""" + bot.prefix + """info :: Information about me. Wow. Very interesting.
""" + bot.prefix + """ping :: Responds 'Pong!' Can be used to check if I'm awake.

""" + bot.prefix + """suggest""" + bot.argumentChar + """Idea""" + bot.argumentKillChar + """ :: Suggests an 'Idea' to my developers.
""" + bot.prefix + """report""" + bot.argumentChar + """Bug""" + bot.argumentKillChar + """ :: Reports a 'Bug'. Please be VERY detailed!
""" + bot.prefix + """invite :: Bring my knowledge with you using my Invite link!

""" + createHelpHeader("Music Commands") + """
[BETA] """ + bot.prefix + """help""" + bot.argumentChar + """music""" + bot.argumentKillChar + """ :: View Music-specific commands.

""" + createHelpHeader("Image Commands") + """
""" + bot.prefix + """help""" + bot.argumentChar + """image""" + bot.argumentKillChar + """ :: View Image-specific commands.

""" + createHelpHeader("Quote Commands") + """
""" + bot.prefix + """quote :: Gets a quote from a random Touhou game.
""" + bot.prefix + """quote""" + bot.argumentChar + """6""" + bot.argumentKillChar + """ :: Gets a quote from Touhou 6.

""" + createHelpHeader("Wiki Commands") + """
""" + bot.prefix + """search""" + bot.argumentChar + """Reimu""" + bot.argumentKillChar + """ :: Searches for 'Reimu' pages on touhouwiki.net.
""" + bot.prefix + """portrait""" + bot.argumentChar + """Cirno""" + bot.argumentKillChar + """ :: Searches for an official 'Cirno' portrait.
""" + bot.prefix + """lookup""" + bot.argumentChar + """Flandre""" + bot.argumentKillChar + """ :: Searches and highlights a 'Flandre' page.

""" + createHelpHeader("Card Commands") + """
[BETA] """ + bot.prefix + """card :: Gets a Trading Card. (No progress is saved)
```"""

# shhh just close your eyes for the following section

# """ + bot.prefix + """daily - Receive your daily Card. Resets every 24 hours.
# """ + bot.prefix + """cardsof""" + argumentChar + """UserID""" + argumentKillChar + """ - View another User's Card collection.

#~~~~~Card Commands~~~~~
#[BETA] """ + bot.prefix + """daily - Gets your daily Card. Resets every 24 hours.
#[BETA] """ + bot.prefix + """cards - View all Cards you currently own.
#[BETA] """ + bot.prefix + """cards""" + bot.argumentChar + """1""" + bot.argumentSeperator + """UserID""" + bot.argumentKillChar + """ - View another User's Card collection.
#[BETA] """ + bot.prefix + """view""" + bot.argumentChar + """1""" + bot.argumentKillChar + """ - View your first Card in detail.
#[BETA] """ + bot.prefix + """view""" + bot.argumentChar + """1""" + bot.argumentSeperator + """UserID""" + bot.argumentKillChar + """ - View another User's Card in detail.

# ok you can open your eyes again

async def help(message):
    arguments = commands.GetArgumentsFromCommand(message.content)

    if arguments == False:
        await message.channel.send(helpMessage)
    else:
        if arguments[0] == 'music':
            await message.author.send(musicHelpMessage)
            if not isinstance(message.channel, DMChannel): # Are we not in a DM Channel?
                await message.channel.send(message.author.name + ": There are a LOT of commands! Check your DMs!") # Tell the User to check them.
        if arguments[0] == 'image' or arguments[0] == 'images':
            await message.channel.send(imageHelpMessage)
    return

'''
async def betahelp(message):
    await message.channel.send(betaHelpMessage)
    return
'''

###

commands.Add("help%", help)
#commands.Add("betahelp", betahelp)
