# Touhou Discord Bot
A Work-In-Progress Discord bot based on the largely popular Touhou series by ZUN.

*Official Bot Invite Link: https://discordapp.com/oauth2/authorize?client_id=408736647480475648&scope=bot*

[![Discord Bots](https://discordbots.org/api/widget/status/408736647480475648.svg?noavatar=true)](https://discordbots.org/bot/408736647480475648)
[![Discord Bots](https://discordbots.org/api/widget/servers/408736647480475648.svg?noavatar=true)](https://discordbots.org/bot/408736647480475648)

## Features
### Commands
The bot comes with plenty of fun Touhou-based commands
```
* Play Touhou music from any of the PC Games, including doujin and arranges
* Post Touhou images (SFW and NSFW) using the Gelbooru API
* Post Touhou quotes from the mainline PC Games (6-16)
* Query touhouwiki.net for pages and portraits of characters, albums, people, etc.

* ...And More! See all commands in-bot by executing the command 'k.help'
```

## Setup
### Install Requirements
To install requirements, you can install directly from the requirements.txt file
#### Linux
```
pip3 install -r requirements.txt
```
#### Windows
```
python -m pip install -r requirements.txt
```

### Config Variables
#### Config Files
You can store your Config Variables as files. Just ensure they are in the same directory as your ```DiscordBot.py``` file

##### Mandatory:
```
'token.txt' = Token from your Discord App (https://discordapp.com/developers/applications/me/)
```
##### Optional:
```
'prefix.txt' = Customize the Command Prefix ('k.' by Default)
'closed-access-users.txt' = Allows for ONLY a list of User IDs to access the bot (Disabled by Default)

'dbl-token.txt' = Allows for discordbots.org API functionality (Disabled by Default)

'data-guild-id.txt' = The Guild ID the Bot will use for it's Data Storage (Disabled by Default)
'data-channel-id.txt' = The Channel ID the Bot will use for it's Data Storage (Disabled by Default)

'suggestions-guild-id.txt' = The Guild ID the Bot will output Suggestions to (Disabled by Default)
'suggestions-channel-id.txt' = The Channel ID the Bot will output Suggestions to (Disabled by Default)
```

#### System Environment Variables
Or, as an alternative, you can choose to store your Config Variables within System Environment Variables

##### Mandatory:
```
'PATCHYBOT-TOKEN' = Token from your Discord app (https://discordapp.com/developers/applications/me/)
```
##### Optional:
```
'PATCHYBOT-PREFIX' = Customize the Command Prefix ('k.' by Default)
'PATCHYBOT-CLOSEDACCESSUSER' = Allows for only a single User ID to access the bot (Disabled by Default)

'PATCHYBOT-DBLTOKEN' = Allows for discordbots.org API functionality (Disabled by Default)

'PATCHYBOT-DATAGUILDID' = The Guild ID the Bot will use for it's Data Storage (Disabled by Default)
'PATCHYBOT-DATACHANNELID' = The Channel ID the Bot will use for it's Data Storage (Disabled by Default)

'PATCHYBOT-SUGGESTIONSGUILDID' = The Guild ID the Bot will output Suggestions to (Disabled by Default)
'PATCHYBOT-SUGGESTIONSCHANNELID' = The Channel ID the Bot will output Suggestions to (Disabled by Default)
```

## Usage
The Bot can be started by running the ```DiscordBot.py``` file in your preferred version of Python 3
