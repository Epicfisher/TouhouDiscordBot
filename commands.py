import bot

class Command:
    name = ""
    command = None

def Add(name, command):
    _command = Command()
    _command.name = name
    _command.command = command
    commands.append(_command)

    #print("Loaded Command '" + bot.prefix + name + "'")

def GetArgumentsFromCommand(command):
    if command.startswith('<@' + str(bot.client.user.id) + '>'):
        command = command[len('<@' + str(bot.client.user.id) + '>'):]
        while command[0] == ' ':
            command = command[1:]
    else:
        command = command[len(bot.prefix):]

    try:
        command = command[command.index(bot.argumentChar) + 1: ]
    except:
        return False

    if command.endswith(bot.argumentKillChar) and len(bot.argumentKillChar) > 0:
        command = command[:-1]

    commandArray = command.split(bot.argumentSeperator)

    for commandUsed in commandArray:
        if commandUsed.startswith(' '):
            commandUsed = commandUsed[1:]

    return commandArray

commands = []
