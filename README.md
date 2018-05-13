# THIS BRANCH OF THE BOT USES 'ASYNC' AND IS NO LONGER BEING ACTIVELY DEVELOPED
# IT IS HIGHLY RECOMMENDED TO SWITCH TO THE NEW 'REWRITE' VERSION IN THE MASTER BRANCH

# Touhou Discord Bot
A Work-In-Progress Discord bot based on the largely popular Touhou series by ZUN.

*Official Bot Invite Link: https://discordapp.com/oauth2/authorize?client_id=408736647480475648&scope=bot*

## Features
### Commands
The bot comes with plenty of fun Touhou-based commands
```
* Post Touhou images (SFW and NSFW) using the Gelbooru API
* Post Touhou quotes from the mainline PC Games (6-16)
* Query touhouwiki.net for pages and portraits of characters, albums, people, etc.

* ...And More! See all commands in-bot by executing the command 'k.help'
```

## Setup
### Install Requirements
To install requirements, you can install directly from the requirements.txt file
```
pip3 install -r requirements.txt
```

### Config Variables
#### Config Files
You can store your Config Variables locally within files. Just ensure they are in the same directory as your ```bot.py``` file
```
'token.txt' = Token from your Discord App (https://discordapp.com/developers/applications/me/)
```

#### System Environment Variables
Or, as an alternative, you can choose to store your Config Variables within  System Environment Variables
```
'TOKEN' = Token from your Discord app (https://discordapp.com/developers/applications/me/)
```
