import commands

###

import bot
import discord
from random import randint
import asyncio
import time
import youtube_dl
import urllib.parse
import html
import math

options = {
    'extractaudio':True,
    'audioformat':'mp3',
    'format': 'bestaudio/best', # Is Best really the best query here? Discord already compresses the actual HECK out of the audio streams anyway, so is this just wasting bandwidth and risking stream disconnection on our end?
    #'format': 'worstaudio/best', # Although frankly this does sound terrible tbh
    'noplaylist':True,
    'nocheckcertificate': True,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'usenetrc': True,
    'simulate': True,
    'fixup': True,
    'nocheckcertificate': True
    #'skip_download': True
    #'''
    #'postprocessors': [{
        #'key': 'FFmpegExtractAudio',
        #'preferredcodec': 'mp3',
        #'preferredquality': '192',
    #}],
    #'''
}

#'ignoreerrors': True,

busy_servers = []

use_raw_parser = False
grab_stream_url_during_playtime = False

class Song:
    raw_english_title = ""
    raw_title = ""
    title = ""
    english_title = ""
    album = ""
    raw_album = ""
    english_raw_album = ""
    circle = ""
    duration = 0
    #src = None
    volume = 0.5
    url = ""
    friendly_url = ""
    caller_id = None

class InterruptableSleep:
    def __init__(self, loop):
        self.cancelling = False
        self.loop = loop
        self.tasks = set()

    async def Sleep(self, delay, result=None):
        if self.cancelling:
            return result

        #coro = asyncio.sleep(duration, result=result, loop=self.loop)
        coro = asyncio.sleep(delay, result=result, loop=self.loop)
        task = asyncio.ensure_future(coro)
        self.tasks.add(task)
        try:
            return await task
        except asyncio.CancelledError:
            return result
        finally:
            self.tasks.remove(task)

    async def Stop(self):
        self.cancelling = True
        for task in self.tasks:
            task.cancel()

class RadioPlayer:
    def __init__(self):
        self.vc = None
        self.voice_channel = None

        self.initialised = False

        self.play_message = ""

        self.stop_after = False

        self.get = GetSong(asyncio.get_event_loop())

        self.queue = []
        #self.use_queue = False # Queues only for None autoplays
        self.use_queue = True # Queues open all the time
        self.automatic_queue_disable = False
        self.preparing_queue = False
        self.song = None
        self.next_song = None

        self.vote_skippers = []
        self.skip_cooldown = None

        self.saved_query = None

        self.playing_loop = True

        self.volume = 0.5

        self.sleep = InterruptableSleep(asyncio.get_event_loop())

    async def Initialise(self, message):
        #for member in self.voice_channel.guild.members:
            #if member.id = id:
                #target = m

        try:
            vc = await connect_voice(self.voice_channel) # Connect to the Voice Channel
        except:
            self.voice_channel.disconnect()
            await message.channel.send("Whoops! I couldn't join '" + str(self.voice_channel) + "'. Please try again!")
            return False

        try:
            self.vc = vc
        except:
            await vc.disconnect()
            try:
                vc = await connect_voice(self.voice_channel) # Reconnect to Voice Channel
            except:
                await message.channel.send("Whoops! I couldn't join '" + str(self.voice_channel) + "'. Please try again!")
                return False

            self.vc = vc

        return True

    async def Play(self, message):
        #while self.playing_loop:
        if self.song == None: # Should first-run. If we don't have a song...
            async with message.channel.typing():
                self.song = await self.get.busy_get_song(message, None, False, self.saved_query, False, False, None) # Get a new Random song.
                if self.song == False: # If we couldn't find a song...
                    await self.Stop() # Bad custom request? Kill the radio.
                    return

        if self.initialised == False:
            if self.saved_query == None:
                self.use_queue = True
            else:
                #self.automatic_queue_disable = True
                pass

            if not await self.Initialise(message):
                print("Failed to Initialise; Returning now")
                await self.Stop()
                return
            self.initialised = True

            await message.channel.send(self.play_message) # Announce ourselves! Ta-da!

        if grab_stream_url_during_playtime:
            print("Quickly Grabbing New Link...")
            with youtube_dl.YoutubeDL(options) as ydl:
                #quick_video_info = await bot.get("http://www.youtube.com/get_video_info?&video_id=buExjuF27_4&el=detailpage&ps=default&eurl=&gl=US&hl=en")
                #token = quick_video_info[quick_video_info.index('t=') + 2:]
                #token = token[token.index('%')]
                #self.song.url = 'http://www.youtube.com/get_video?video_id=%s&t=%s&eurl=&el=detailpage&ps=default&gl=US&hl=en' % ('buExjuF27_4', token)
                #print(quick_video_info)
                #print(token)
                #return False

                #result = youtube_dl.extractor.youtube.InfoExtractor.extract(youtube_dl.extractor.youtube.InfoExtractor.extract, self.song.friendly_url)
                #result = youtube_dl.extractor.YoutubeIE._real_extract(youtube_dl.extractor.YoutubeIE, self.song.friendly_url)

                result = await bot.run_in_threadpool(lambda: ydl.extract_info(self.song.friendly_url + " -g", download=False))
                pass

            self.song.url = result['url']
            #print(self.song.url)
            print("Grabbed!")

        #self.src = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(self.song.url))
        #self.src = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(self.song.url, before_options="-reconnect 1 -reconnect_at_eof 1 -reconnect_streamed 1 -reconnect_delay_max 2 -timeout -1 -multiple_requests 1", options='-vn'))
        #self.src = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(self.song.url, before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 2 -timeout -1 -listen_timeout -1 -re -thread_queue_size 512 -analyzeduration 15000000 -multiple_requests 1"))
        self.src = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(self.song.url, before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"))

        #self.src = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(self.song.url, before_options="-reconnect 1 -reconnect_streamed 1"))
        self.src.volume = self.volume

        try:
            if len(self.vc.channel.members) < 2:
                await self.Stop()
                return
        except:
            await self.Stop()
            return

        #try:
            #await vc.play(src, after=lambda e: finish_music(src, vc))
            #await self.vc.play(self.src) # Actually play the music.
        #except:
            #pass

        self.skip_cooldown = time.time()

        loop = asyncio.get_event_loop()
        self.vc.play(self.src, after=lambda e: loop.create_task(self.NextSong(message)))

        #while vc.is_playing():

        if self.song.circle == "":
            await self.sleep.Sleep(self.song.duration / 2) # Wait for the length of the song in Seconds, divided by two. Half of it's duration.
        else:
            await self.sleep.Sleep(self.song.duration / 4) # Wait for the length of the song in Seconds, divided by four. A Quarter of it's duration. This is because arranges can typically take far longer to retrieve, and so they need the extra time.

        if not self.playing_loop:
            await self.Stop()
            return
        #next_song_start_time = time.time()
        if not self.preparing_queue and not self.sleep.cancelling and len(self.queue) < 1:
            self.preparing_queue = True
            print("Preparing next song early due to lack of queue...")
            self.next_song = await self.get.handle_get_song(message, None, False, self.saved_query, False, False, self.song.title) # Prepare the next song a little early, so the playback seems continuous.
            self.preparing_queue = False
        #next_song_start_time = time.time() - next_song_start_time
        #await self.sleep.Sleep(self.song.duration / 2 - next_song_start_time) # Wait for the second length of the song in Seconds, divided by two and incremented by one just to be safe

    async def NextSong(self, message):
        if not self.playing_loop:
            await self.Stop()
            return
        if self.stop_after:
            await self.Stop()
            return
        self.vote_skippers = [] # Clear any Vote Skippers, as this will now be a new song.
        print("Officially Finished Playing Song!")

        if not self.playing_loop:
            await self.Stop()
            return

        if self.preparing_queue:
            print("Already preparing the next song! Now waiting...")
            while self.preparing_queue: # Wait for the next song to prepare.
                await asyncio.sleep(1)

                if not self.playing_loop:
                    await self.Stop()
                    return
        else:
            if len(self.queue) < 1 and self.next_song == None:
                self.preparing_queue = True
                print("I'm not preparing the next song, and there isn't one! I must have skipped? Preparing next song due to lack of queue...")
                self.next_song = await self.get.busy_get_song(message, None, False, self.saved_query, False, False, self.song.title)
                self.preparing_queue = False

        if not self.playing_loop:
            await self.Stop()
            return

        if len(self.queue) > 0: # Check to see if we've acqured a queued song. If so...
            print("Popping from next Queue Song!")
            self.next_song = self.queue[0] # Our next song becomes the queued song.
            self.queue.pop(0) # Remove the queued song from the list so it isn't used again.
        self.sleep.cancelling = False # We're not cancelling anymore, so reset this so we can cancel again next loop.
        self.preparing_queue = False
        #await vc.disconnect()

        if not self.playing_loop:
            await self.Stop()
            return

        self.song = self.next_song
        self.next_song = None

        loop = asyncio.get_event_loop()
        loop.create_task(self.Play(message))
        #self.Play(message)

    async def Stop(self):
        if not self.playing_loop:
            return

        self.playing_loop = False # Stop the Music while loop.
        print("Properly Killing Radio!")
        #global radio_players

        await self.sleep.Stop() # Interrupt awaited sleeps.
        await self.get.Stop() # Interrupt all Get Songs

        try:
            self.vc.stop() # Stop audio playback
        except:
            pass

        try:
            await self.vc.disconnect() # Disconnect from the Voice Channel.
        except:
            pass

        try:
            #bot.radio_players.pop(self.index_in_radios) # Remove the Radio Player instance entirely, since at this point it isn't even needed since the entire thing is just stopped
            bot.radio_players.remove(self)
        except:
            pass

        #del bot.radio_players[index_in_radios]
        #try:
        try:
            busy_servers.remove(voice_channel.guild.id)
        except:
            pass

        return

    async def Pause(self):
        if self.vc.is_paused():
            self.vc.resume()
            return
        else:
            self.vc.pause()
            return

    async def Skip(self):
        if self.vc.is_playing():
            try:
                await self.vc.stop() # Stop Playback First.
            except:
                pass

            await self.sleep.Stop() # Interrupt awaited sleeps.
        return

    async def VoteSkip(self, message):
        if self.vc.is_playing():
            Voteskipping = False

            if len(self.vote_skippers) >= math.ceil(float(len(self.voice_channel.members) - 1) / float(2)):
                Voteskipping = True

            if not Voteskipping:
                if message.author.id in self.vote_skippers:
                    await message.channel.send("You've already Voted to Skip this Song!")
                    return
                self.vote_skippers.append(message.author.id)

            #print(str(bot.music_cooldowntime - math.floor(time.time() - self.skip_cooldown)))
            print("Voted to Skip. " + str(len(self.vote_skippers)) + " / " +  str(len(self.voice_channel.members) - 1) + " Need " + str(math.ceil(float(len(self.voice_channel.members) - 1) / float(2))))
            if len(self.vote_skippers) >= math.ceil(float(len(self.voice_channel.members) - 1) / float(2)):
                time_left = bot.music_cooldowntime - math.floor(time.time() - self.skip_cooldown)
                if time_left > 0:
                    self.vc.stop()
                    time.sleep(time_left)
                await self.Skip()
                return
            else:
                await message.channel.send("Voted to Skip. [" + str(len(self.vote_skippers)) + " / " + str(len(self.voice_channel.members) - 1) + "] (" + str(math.ceil(float(len(self.voice_channel.members) - 1) / float(2))) + " Needed)")
                return

    async def Togglequeue(self):
        if self.use_queue:
            self.use_queue = False
            self.queue = [] # Clear the Song Queue.
            return
        else:
            self.use_queue = True
            return

    async def Volume(self, volume):
        self.volume = volume
        self.src.volume = volume
        return

'''
class DummyFile(object):
    def write(self, x): pass
    def flush(self): pass

@contextlib.contextmanager
def nostdout():
    save_stdout = sys.stdout
    sys.stdout = DummyFile()
    yield
    sys.stdout = save_stdout
'''

class GetSong:
    def __init__(self, loop):
        self.cancelling = False
        self.loop = loop
        self.tasks = set()

    async def busy_get_song(self, message, caller_user_id, download_song, query, doujin, pc98, old_song):
        if not await busy_me(message):
            return

        return_value = await self.handle_get_song(message, caller_user_id, download_song, query, doujin, pc98, old_song)

        busy_servers.remove(message.guild.id)

        return return_value

    async def handle_get_song(self, message, caller_user_id, download_song, query, doujin, pc98, old_song):
        if self.cancelling:
            return False

        #coro = self.get_song(message, caller_user_id, download_song, query, doujin, pc98, old_song)
        #task = asyncio.ensure_future(coro)
        #task = self.loop.create_task(self.get_song(message, caller_user_id, download_song, query, doujin, pc98, old_song))
        #self.tasks.add(task)

        coro = self.get_song(message, caller_user_id, download_song, query, doujin, pc98, old_song)
        task = asyncio.ensure_future(coro)
        self.tasks.add(task)
        try:
            return await task
        except asyncio.CancelledError:
            print("Cancelled!")
            return False
        finally:
            self.tasks.remove(task)
            #pass
        #return_value = await get_song(message, caller_user_id, download_song, query, doujin, pc98, old_song)
        #return return_value

    async def Stop(self):
        self.cancelling = True
        for task in self.tasks:
            print("Cancelling Task")
            task.cancel()

    async def get_song(self, message, caller_user_id, download_song, query, doujin, pc98, old_song):
        all = False

        #if not query == None:
            #if 'all' in query.lower():
                #all = True
                #query = query.replace("all", "")

        random = True

        if not query == None:
            if query.lower().endswith('win'):
                #query = None
                query = query[:-3]

        #print(query)
        if not query == None:
            if query.lower().startswith('arranges'):
                doujin = True
                random = False
                #print("NO RANDOM. FORCED DOUJIN")
                query = query[8:]
            if query.lower().startswith('doujins'):
                doujin = True
                random = False
                #print("NO RANDOM. FORCED DOUJIN")
                query = query[7:]
            if query.lower().startswith('arrange'):
                doujin = True
                random = False
                #print("NO RANDOM. FORCED DOUJIN")
                query = query[7:]
            if query.lower().startswith('doujin'):
                doujin = True
                random = False
                #print("NO RANDOM. FORCED DOUJIN")
                query = query[6:]
            if query.lower().startswith('ost'):
                doujin = False
                random = False
                #print("NO RANDOM. FORCED OST")
                query = query[3:]
            query = check_argument_query(query)
            '''
            if query.lower().startswith("all"):
                all = True
                query = query[3:]
            '''
            if query.isdigit():
                if int(query) < 6:
                    pc98 = True
                    #print("PC98 MODE")
                    query = query[1:]
            if query.lower().startswith('pc98'):
                pc98 = True
                #print("PC98 MODE")
                query = query[4:]
            if query.lower().startswith('all'):
                all = True
                #print("ALL MODE")
                query = query[3:]

        if random: # Are we playing random music?
            #print("RANDOM MODE")
            if randint(0, 1) == 0: # If we get half chance...
                doujin = True # We're playing a Doujin/Arrange now. Otherwise, this would just play regular Touhou music, with the other half chance.

            #if query.lower().startswith('arrange') or query.lower().startswith('doujin') or query.lower().startswith('arranges') or query.lower().startswith('doujins'):
            #if doujin:
        if query == "":
            query = None

            #query = check_argument_query(query)

        doujin_title_tags = ['arrange', 'arrangement', 'instrumental', 'rock', 'metal', 'orchestral', 'piano', 'synthesia', 'midi', 'house', 'vocal', 'subs']
        bad_title_tags = ['demo', 'preview', 'intro', 'crossfade', 'xfd', 'speedpaint', 'osu', 'sound voltex', 'sdvx', 'nightcore', 'night core']

        original_games = await bot.get('https://epicfisher.github.io/TouhouWikiArrangeParser/root/')
        original_games = html.unescape(original_games)
        #original_games = original_games[original_games.index('"<body>"') + 6:]

        link_to_use = None

        try:
            query_first_lower = query.split(' ')[0].lower()
        except BaseException:
            pass

        raw_albums = []
        english_raw_albums = []
        links = []

        keep_parsing = True
        while keep_parsing:
            stop = False

            try:
                item = original_games[original_games.index('<li>') + 4: original_games.index('</li>') - 4]

                game = item[:item.index('<') - 1]
                album = item[item.index('>') + 1:]
                english_album = album[album.index('<i>') + 3:]
                album = album[:album.index('</a>')]
                raw_album = album
                english_raw_album = english_album
                #print(str(int(game[game.index('.') + 1:])))

                if game.endswith('.0'):
                    game = game[0:-2]
                if game == "15.5":
                    stop = True # Alright, basically this game just doesn't work right now, there are like TWO arranges and like a few OST songs that even WORK. I hate to just disable this, but it's really the best way to avoid annoyance for everybody else. I humbly apologise, Touhou 15.5 fans. As soon as the arranges and YouTube OST videos populate, I wouldn't hesitate to re-enable Touhou 15.5 music playback, but as this stands, it's more of a hinderance to the enjoyability of the bot for everyone else. You're free to clone this bot and remove these lines of code if you REALLY want to listen to Touhou 15.5 music, just be prepared for immense dissapointment.
                if not game[0].isdigit():
                    break # Non-game album. I'll add support for this later, maybe. In order to keep it simple, I'll just have support for the actual games OSTs for now.

                if not pc98 and not all and float(game) < 6: # If we're not in PC98 but the game number is less than 6...
                    stop = True
                if pc98 and float(game) > 5:
                    stop = True
                #if not doujin and int(game[game.index('.') + 1:]) > 0:
                    #stop = True # I guess I'll treat the sub-game OSTs as 'Doujin' for now.

                if not stop:
                    link = item[item.index('<a href="') + 9:]
                    link = link[:link.index('"')]
                    link = link[:link.index('/') + 1]
                    link = urllib.parse.unquote(link)

                    if query == None:
                        raw_albums.append(raw_album)
                        english_raw_albums.append(english_raw_album)
                        links.append(link)
                    else:
                        album = game + " " + album

                        album_words = album.split(' ')
                        for album_word in album_words:
                            if query_first_lower == album_word.lower():
                                album = raw_album
                                link_to_use = link
                                keep_parsing = False
                                break

                #if not stop:
                    #games.append(game)

                    #link = item[item.index('<a href="') + 9:]
                    #link = link[:link.index('"') - 1]
                    #link = urllib.parse.unquote(link) + '/'
                    #links.append(link)
                    #name = item[item.rfind('>') + 1:]
                    #names.append(name)

                    #if game == game_to_use and not game == None:
                        #link_to_use = link
                        #break

                original_games = original_games[original_games.index('</li>') + 5:]
            except BaseException:
                keep_parsing = False

        if link_to_use == None and not query == None:
            await message.channel.send("I couldn't find what you told me to look for!")
            return False
        #else:
            #if not game_to_use in games:
            #await message.channel.send("I couldn't find what you told me to look for!")
            #return False

        #print("Getting music from '" + str(game_to_use) + "'")

        keep_retrying = True
        while keep_retrying:
            if query == None:
                random_number = randint(0, len(links) - 1)

                album = raw_albums[random_number]
                raw_album = album
                english_raw_album = english_raw_albums[random_number]
                link_to_use = links[random_number]

            songs = await bot.get('https://epicfisher.github.io/TouhouWikiArrangeParser/root/' + link_to_use + 'index.html')
            #songs = html.unescape(songs)
            #songs = songs[songs.index('song_list') + 9:]

            #print(songs)

            keep_retrying = False

            jap_titles = []
            titles= []
            arrange_links = []

            keep_parsing = True
            while keep_parsing:
                try:
                    songs = songs[songs.index('href="') + 6:]
                    jap_title = songs[songs.index('>') + 1:songs.index('</a>')]
                    jap_title = html.unescape(jap_title)
                    jap_titles.append(jap_title)

                    try:
                        #title = songs[songs.index('trans_title">') + 13:]
                        #title = title[:title.index('</dt>')]
                        title = songs[songs.index('<i>') + 3:songs.index('</i>')]
                        title = html.unescape(title)
                        titles.append(title)
                    except BaseException:
                        titles.append('')
                        #print("No English title present for Japanese song '" + jap_title + "'")
                        pass

                    if doujin:
                        arrange_link = songs[:songs.index('"')]
                        arrange_link = html.unescape(arrange_link)
                        arrange_links.append(arrange_link)

                    #print(jap_title + " | " + title)

                    #songs = songs[songs.index('"song_box"') + 10:]
                except BaseException:
                    keep_parsing = False

                if len(jap_titles) < 1:
                    if query == None:
                        print("Couldn't find a song from base game album. Retrying...")
                        keep_retrying = True
                    else:
                        await message.channel.send("Sorry, I don't currently know any songs from that game!\nMaybe check back another time?")
                        return False

        keep_getting_arranges = True
        keep_trying_arranges = True
        while keep_getting_arranges:
            while keep_trying_arranges:
                print("Restarting with new Random Song!")
                keep_getting_arranges = False
                keep_trying_arranges = False

                get_unique_song = True
                while get_unique_song:
                    get_unique_song = False

                    random_song = randint(0, len(jap_titles) - 1)

                    if not old_song == None:
                        if not doujin:
                            if len(jap_titles) > 1: # If we only have one base song, uh, just play that regardless? I'm not implementing such a specific use-case scenario to return back to the base games. Literally nobody is going to care.
                                if jap_titles[random_song] == old_song:
                                    print("Same song! '" + jap_titles[random_song] + "' | '" + old_song + "'")
                                    get_unique_song = True

                additional_tags = ""

                if doujin:
                    keep_retrying = True
                    get_next_arrange_song = False
                    while keep_retrying == True:
                        keep_retrying = False

                        if get_next_arrange_song:
                            random_song = randint(0, len(jap_titles) - 1)
                        else:
                            get_next_arrange_song = True

                        arrange_link_to_use = arrange_links[random_song]
                        print("Getting an arrange from: https://epicfisher.github.io/TouhouWikiArrangeParser/root/" + link_to_use + arrange_link_to_use + "")
                        arranges = await bot.get('https://epicfisher.github.io/TouhouWikiArrangeParser/root/' + link_to_use + arrange_link_to_use)
                        #arranges = html.unescape(arranges)
                        #arranges = arranges[arranges.index('Arranged music'):]
                        #if len(arranges) > 0:
                            #arranges = arranges[arranges.index('song_box"') + 8:]
                            #arranges = arranges[arranges.index('song_box"') + 32:]
                        if len(arranges) < 1:
                            #if query == None:
                            print("Could not find any Arranges from random base game album. Retrying...")
                            keep_retrying = True
                            #else:
                                #await message.channel.send("Sorry, I don't currently know any arranges from that song!\nMaybe check back another time?")
                                #return False

                        arrange_circles = []
                        arrange_titles = []
                        arrange_albums = []

                        keep_parsing = True
                        #print(arranges)
                        while keep_parsing:
                            worked = True

                            try:
                                arrange_title = arranges[arranges.index('&bull;') + 7:]
                                arrange_title = arrange_title[:arrange_title.index('&bull;') - 1]
                                arrange_title = html.unescape(arrange_title)
                                #print("Title: '" + arrange_title + "'")

                                arrange_album = arranges[arranges.index('&bull;') + 6:]
                                arrange_album = arrange_album[arrange_album.index('&bull;') + 1:]
                                try:
                                    arrange_album = arrange_album[arrange_album.index('">') + 2:]
                                    arrange_album = arrange_album[:arrange_album.index('</a>')]
                                except BaseException:
                                    pass
                                arrange_album = html.unescape(arrange_album)
                                if arrange_album == arrange_title:
                                    print("Found a Title with identical Album! ('" + arrange_album + "' / '" + arrange_title + "') To keep it safe, we're going to ignore this result.")
                                    worked = False
                                #print("Album: '" + arrange_album + "'")

                                if worked:
                                    arrange_circle = arranges[8:arranges.index('</b>')]
                                    arrange_circle = html.unescape(arrange_circle)
                                    #print("Circle: '" + arrange_circle + "'")

                                    arrange_circles.append(arrange_circle)
                                    arrange_titles.append(arrange_title)
                                    arrange_albums.append(arrange_album)

                                #arranges = arranges[arranges.index('song_box"') + 32:]
                                arranges = arranges[arranges.index('</li>') + 5:]
                            except BaseException:
                                keep_parsing = False

                    if (len(arrange_titles) < 1) or (len(arrange_titles) == 1 and arrange_titles[0] == old_song):
                        print("No arranges! Let's try again for another base song and get another set!")
                        keep_getting_arranges = True
                        keep_trying_arranges = True
                    #if len(arrange_titles) < 13: # If we have less than 13 arranges, probably a safe bet to say we don't have atleast one arrange that works...
                        #print("Not enough arranges! Let's try again for another base song and get more!")
                        #keep_getting_arranges = True

            get_song = True
            get_next_song = False
            while get_song:
                get_song = False

                if doujin:
                    if get_next_song:
                        print("Getting another arrange!")

                    get_unique_song = True
                    while get_unique_song:
                        get_unique_song = False

                        random_arrange = randint(0, len(arrange_titles) - 1)

                        if not old_song == None:
                            if len(arrange_titles) > 1: # If we have only one arrange, then screw it, play that song anyway
                                print(arrange_titles[random_arrange] + " | " + old_song)
                                if arrange_titles[random_arrange] == old_song:
                                    print("Same arrange! '" + arrange_titles[random_arrange] + "' | '" + old_song + "'")
                                    get_unique_song = True

                    raw_song_jap = jap_titles[random_song]
                    try:
                        raw_song = titles[random_song]
                    except BaseException:
                        raw_song = ""
                    song = arrange_titles[random_arrange]
                    english_song = ""
                    album = arrange_albums[random_arrange]
                    circle = arrange_circles[random_arrange]
                    additional_tags = '"' + arrange_circles[random_arrange] + '"'
                else:
                    if get_next_song:
                        print("Getting another Base Song!")
                        random_song = randint(0, len(jap_titles) - 1)
                    else:
                        get_next_song = True

                    raw_song_jap = ""
                    raw_song = ""
                    song = jap_titles[random_song]
                    try:
                        english_song = titles[random_song]
                    except BaseException:
                        english_song = ""

                    additional_tags = '"原曲"+coreytaiyo' # Coreytaiyo seems to have uploaded all if not most of the classic 2hu songs under relatively good quality, so I guess I'll rely on him for getting these non-doujin tunes. Keep it up my dude.
                    circle = "" # This doesn't belong to a circle, unless you count ZUN himself as the circle of life.

                    try:
                        album = album[:album.index('～')]
                    except BaseException:
                        #print("Touhou Album '" + album + "' has no ～, please advise.")
                        pass

                    if album[len(album) - 1] == '　':
                        album = album[:-1]
                    #[:album.index('～ ')]

                #video_results = await bot.get('https://www.youtube.com/results?search_query=' + 'touhou+' + str(game_to_use) + '+' + song.replace(' ', '+') + '+theme&page=1') # For Non-Japanese Results?

                #video_results = await bot.get('https://www.youtube.com/results?search_query=' + song.replace(' ', '+') + '&page=1') # For Japanese results? (OLD)
                print("Now searching for: '" + song + "' / '" + english_song + "'\nFrom the album: '" + album + "'")
                if not circle == "":
                    print("From the circle: '" + circle + "'")

                working_url = None
                working_duration_seconds = None

                if use_raw_parser:
                    search_query = '"' + song.replace(' ', '+') + '"+"' + album.replace(' ', '+') + '"+' + additional_tags # For Japanese results?

                    #video_results = await bot.get('https://www.youtube.com/results?search_query="原曲"+"' + song.replace(' ', '+') + '"+"' + album[:album.index('～ ')] + '"+coreytaiyo&page=1') # For Japanese results?
                    #video_results = await bot.get('https://www.youtube.com/results?search_query=東方"' + song.replace(' ', '+') + '"+"' + album.replace(' ', '+') + '"+' + additional_tags + '&page=1') # For Japanese results?
                    video_results = await bot.get('https://www.youtube.com/results?search_query=' + search_query + '&page=1')

                    if 'This page appears when Google automatically detects requests' in video_results:
                        print("Blocked by YouTube. Forcing Radio termination.")
                        #await message.channel.send("An error occured!")
                        return False
                else:
                    search_query = '"' + song + '" "' + album + '" ' + additional_tags.replace('+', ' ') # For Japanese results?

                    #ydl = youtube_dl.YoutubeDL(options)
                    #except youtube_dl.utils.YoutubeDLError as e:
                    with youtube_dl.YoutubeDL(options) as ydl:
                        try:
                            video_results = await bot.run_in_threadpool(lambda: ydl.extract_info("ytsearch2:" + search_query, download=False))
                            #video_results = await bot.run_in_threadpool(lambda: ydl.extract_info("ytsearch2:" + search_query + " --get-url", download=False))
                        except youtube_dl.utils.YoutubeDLError:
                            video_results = None

                keep_parsing = True
                i = 0
                while keep_parsing and not video_results == None:
                    worked = True

                    try:
                        if use_raw_parser:
                            url_start_index = video_results.index('/watch?v=')
                            video_result = video_results[url_start_index:]
                            video_result = "https://youtube.com" + video_result[:video_result.index('"')]
                            if '&amp' in video_result:
                                i = i - 1
                                print("&amp in URL! Must be a playlist, therefore it's bad.")
                                worked = False
                        else:
                            video_result = video_results['entries'][i] # Don't have to worry about playlists, since they're already excluded within our YoutubeDL options variable.

                        if worked:
                            if use_raw_parser:
                                duration = video_results[video_results.index('Duration: ') + 10:]
                                duration = duration[:duration.index('.')]
                                duration_hours = 0
                                if duration.count(':') > 1:
                                    duration_hours = int(duration[:duration.index(':')])
                                    duration = duration[duration.index(':') + 1:]
                                duration_seconds = int(duration[duration.index(':') + 1:])
                                duration_minutes = int(duration[:duration.index(':')])
                                if duration_hours > 0:
                                    duration_minutes = duration_minutes + (duration_hours * 60)

                                duration_full_seconds = (duration_minutes * 60) + duration_seconds
                            else:
                                duration_full_seconds = video_result['duration']
                                duration_minutes = math.floor(duration_full_seconds / 60)
                                # Whole Duration portion below is entirely for debug purposes. It can be removed and the performance might increase.
                                #duration = None
                                duration = str(duration_full_seconds / 60)
                                duration_seconds = int(duration[duration.index('.') + 1:])
                                duration_seconds = str(duration_seconds * 60)[:2]
                                if len(duration_seconds) == 1:
                                    duration_seconds = "0" + duration_seconds
                                duration = duration[:duration.index('.')]
                                duration = duration + ":" + duration_seconds

                            print("Looking at a song of duration '" + str(duration_minutes) + "' Minutes.")
                            if duration_minutes > 8: # If the song is longer than 8 minutes...
                                #i = i - 1 # We have one less
                                print("That YouTube Song is too Long!")
                                worked = False # Doesn't count as a working video
                            if duration_minutes < 1: # If the song is shorter than 1 minute...
                                print("That YouTube Song is too Short!")
                                worked = False # Doesn't count as a working video

                        if use_raw_parser:
                            video_results = video_results[url_start_index + 9:]
                            #print(video_results)

                        if worked:
                            if use_raw_parser:
                                title = video_results[video_results.index('data-video-ids=') + 15:]
                                title = title[title.index('spf-link') + 8:]
                                title = title[title.index('title="') + 7:] # Kind of messy but shh
                                title = title[:title.index('"')]
                                title = html.unescape(title)
                            else:
                                title = video_result['title']

                            title = title.replace('「', '')
                            title = title.replace('」', '')
                            title = title.replace("'", '')
                            title = title.replace('"', '')
                            title = title.replace('？', '?')
                            title_lower = title.lower()

                            print("Looking at a video with title '" + title_lower + "'")

                            if use_raw_parser:
                                description = video_results[video_results.index('yt-lockup-description') + 21:]
                                description = description[description.index('>') + 1:]
                                description = description[:description.index('</div>')]
                                description = html.unescape(description)
                                description = description.replace('</b>', '')
                                description = description.replace('<b>', '')
                            else:
                                description = video_result['description']
                                try:
                                    description = description[:120]
                                except BaseException:
                                    pass
                                description = description.replace('\n', ' ')

                            description_lower = description.lower()

                            print("Looking at a video with description '" + description_lower + "'")

                            song_consistent = song.lower().replace('　', ' ')
                            song_consistent = song_consistent.replace('？', '?')
                            song_consistent = song_consistent.replace('(', '').replace(')', '').replace('[', '').replace(']', '')

                            if not song_consistent in title_lower.replace('　', ' ').replace('？', '?').replace('(', '').replace(')', '').replace('[', '').replace(']', '') and not song_consistent in description_lower.replace('　', ' ').replace('？', '?').replace('(', '').replace(')', '').replace('[', '').replace(']', ''):
                                print("That video title and description has no song name (" + song_consistent + ") in it! Must be a bad one. Let's ignore it.")
                                worked = False

                        if worked:
                            if doujin:
                                for title_tag in bad_title_tags:
                                    if title_tag in title_lower:
                                        print("That song had a bad title tag!")
                                        #i = i - 1
                                        worked = False
                                        break
                                    if title_tag in description_lower:
                                        print("That song had a bad title tag in the description!")
                                        worked = False
                                        break
                            else:
                                for title_tag in doujin_title_tags: # This might not be needed for the Japanese queries.
                                    if title_tag in title_lower:
                                        print("That song had a doujin title tag when we didn't want one!")
                                        #i = i - 1
                                        worked = False
                                        break

                        if worked:
                            if use_raw_parser:
                                working_url = video_result
                                url = None
                            else:
                                working_url = video_result['webpage_url']
                                url = video_result['url']

                            working_duration_seconds = duration_full_seconds
                            break

                        if use_raw_parser:
                            video_results = video_results[video_results.index('/watch?v=') + 9:] # We need to do it twice for some reason AAAA
                    except BaseException:
                        keep_parsing = False

                    i = i + 1
                    #if i >= 15: # After we've parsed through 15 songs...
                    if i >= 2: # After we've parsed through 2 songs...
                        keep_parsing = False # Stoppu

                if working_url == None:
                    #await message.channel.send("I couldn't find a song!")
                    print("I couldn't find a YouTube song! Retrying...")
                    if doujin:
                        arrange_titles.pop(random_arrange) # Remove this failed song
                        if len(arrange_titles) > 0:
                            get_song = True
                        else:
                            print("Ran out of Arranges! Trying next Song...")
                            keep_getting_arranges = True
                            keep_trying_arranges = True
                    else:
                        get_song = True

        if url == None and not grab_stream_url_during_playtime:
            ##with nostdout():
            with youtube_dl.YoutubeDL(options) as ydl:
                ##loop = asyncio.get_event_loop()
                ##result = await loop.run_in_executor(thread_pool, lambda: ydl.extract_info(working_url, download=False))
                result = await bot.run_in_threadpool(lambda: ydl.extract_info(working_url + " -g", download=False))

            ##await message.channel.send("Now playing Music in '" + str(vc.channel.name) + "'!")

            url = result['url']

        if download_song:
            try:
                local_url = os.path.dirname(os.path.realpath(__file__)) + '\\temp_music\\' + str(message.guild.id) + ".webm"
                print("Now Downloading Video...")
                #urllib.request.urlretrieve(url, local_url)
                await get_file(url, local_url)
                url = local_url
                print("Download Successful! Using Local File for URL...")
            except:
                print("Download Failed! Opting for a Direct Stream URL Instead!")
                pass
        else:
            print("Downloading Disabled; Opting for a Direct Stream URL Instead!")
            pass

        #print(url)

        print("Posting URL '" + working_url + "' With a Title of '" + song + "' And a Duration of '" + str(duration) + "' Minutes and '" + str(working_duration_seconds) + "' Full Seconds\n")

        if not doujin:
            album = raw_album
            raw_album = ""

        song_output = Song()
        song_output.title = song
        song_output.raw_english_title = raw_song
        song_output.raw_title = raw_song_jap
        song_output.album = album
        song_output.raw_album = raw_album
        song_output.english_raw_album = english_raw_album
        song_output.circle = circle
        song_output.english_title = english_song
        song_output.duration = working_duration_seconds
        #song_output.src = src
        song_output.url = url
        song_output.friendly_url = working_url
        song_output.caller_id = caller_user_id

        return song_output

##################################################MUSIC############################################################
async def busy_check(message):
    if message.guild.id in busy_servers:
        await message.channel.send("I'm already doing something!")
        print("Busy Server!")
        return False
    return True

async def busy_me(message):
    #if not await busy_check(message):
        #return False
    busy_servers.append(message.guild.id)
    return True

async def connect_voice(voice_channel):
    #vc = await voice_channel.connect()
    vc = None

    if not voice_channel.guild.voice_client == None:
        if voice_channel == voice_channel.guild.voice_client.channel:
            print("Reusing old VC")
            return voice_channel.guild.voice_client
        else:
            print("Forcing Kill of Old Radio VC")
            await voice_channel.guild.voice_client.disconnect()

    try:
        vc = await voice_channel.connect()
    except:
        if vc == None:
            #await message.channel.send("I couldn't find your Voice Channel!")
            return
        else:
            #await voice_channel.disconnect()
            #await self.vc.disconnect()
            await bot.client.disconnect()
            try:
                vc = await voice_channel.connect()
            except:
                pass

    return vc

async def play_music(message):
    output = await handle_manage_music(message, True)
    if output == False:
        return

    if not await busy_check(message):
        return

    command = message.content

    if command.startswith('<@' + str(bot.client.user.id) + '>'):
        command = command[len('<@' + str(bot.client.user.id) + '>'):]
        while command[0] == ' ':
            command = command[1:]
    else:
        command = command[len(bot.prefix):]

    #if len(message.content) - len(bot.prefix) > 4:
    if len(command) > 4:
        if not command[4] == bot.argumentChar:
            return

    #if await check_music_direct_message(message) == False:
        #return

    #if await check_music_manage_channel(message, True) == False:
        #return

    voice_channel = None
    changed_channel = False

    saved_query = None

    arguments = commands.GetArgumentsFromCommand(message.content)

    if not arguments == False:
        saved_query = arguments[0]

    #saved_query = "all"

    ''' # Uncomment me for argument-based voice channel joining based on the given voice channel ID. I also thought this might be useful at first, but later decided it would be way cooler and more useful to have the play command's arguments play specific queued music, all the time, so I removed this functionality and added in that instead.
    #if not arguments == False:
        #try:
            #voice_channel = message.guild.get_channel(int(arguments[0]))
        #except:
            #await message.channel.send("Please give me a valid Voice Channel ID you want me to join!\nOr, alternatively, join the Voice Channel and execute '" + bot.prefix + "play'")
            #return

    #if voice_channel == None:
    '''
    try:
        if message.author.voice:
            voice_channel = message.author.voice.channel
    except:
        await message.channel.send("Unfortunately, I don't work in Direct Messaging as of yet!\nIf you want me to play Music, invite me to a Server!")
        return

    ''' # Uncomment me for saved voice channel support. I thought this might be useful at first, and it was one of the very first things I implemented, but on further thought this isn't really mentioned anywhere and might lead to some confusion or anger when it joins a voice channel that was unintended.
    saved_voice_channel = await search_data('music_channel-' + str(message.guild.id))
    if saved_voice_channel == False: # No saved Voice Channel.
        try:
            await write_data('music_channel-' + str(message.guild.id), str(voice_channel.id)) # Save the Voice Channel.
        except:
            voice_channel = None
    else:
        if not voice_channel == None:
            if not str(voice_channel.id) == saved_voice_channel:
                await edit_data('music_channel-' + str(message.guild.id), str(voice_channel.id), False) # Edit the Saved Voice Channel.
                changed_channel = True
        else:
            voice_channel = message.guild.get_channel(int(saved_voice_channel))
    '''

    if voice_channel == None:
        print("User not in Voice Channel!")
        await message.channel.send("Please join a Voice Channel you want me to play music in, and try this command again!")
        return

    if len(voice_channel.members) < 2:
        if len(voice_channel.members) < 1 or voice_channel.members[0].bot:
            #await message.channel.send("The Voice Channel '" + str(voice_channel) + "' is empty!")
            await message.channel.send("But there's nobody in '" + str(voice_channel) + "'. Who would I be playing music to?")
            return

    voice_channel_perms = voice_channel.permissions_for(voice_channel.guild.me)

    if not voice_channel_perms.connect:
        await message.channel.send("I don't have permission to play in '" + str(voice_channel) + "'!")
        return False

    for i in range(0, len(bot.radio_players)):
        #if bot.radio_players[i].vc.channel.id == voice_channel.id:
            #await message.channel.send("Hey, I'm already playing music in '" + str(bot.radio_players[i].vc.channel) + "'!")
            #return
        #else:
            #if bot.radio_players[i].vc.guild.id == voice_channel.guild.id:
                #await bot.radio_players[i].vc.disconnect() # We're playing in the same guild, just a different voice channel. If so, disconnect it from the old one, so we can play instead in a new channel, essentially moving it.
        if bot.radio_players[i].vc.guild.id == voice_channel.guild.id:
            await message.channel.send("Hey, I'm already playing music in '" + str(bot.radio_players[i].vc.channel) + "'!")
            return

    if len(bot.radio_players) >= 5 and not message.author.id == bot.owner_id: # Beta Testing Thingy
        print("Prevented Too Many Music Servers!")
        await message.channel.send("You cant play Music right now. Please try again later!")
        #await message.channel.send("<Hey! Sorry for the inconvenience, but this command is currently being tested in public closed-beta! Only the first *5 servers* who use this command are currently allowed to listen to Music. I'm currently in the process of testing whether or not my service provider would be able to handle multiple audio streams to dozens of servers at once, and so I'm starting small to benchmark it's performance. If you were dying to try this command, either try again later when (hopefully) a server stops playing music and a test slot opens (`k.info` can help you there), or wait for the full unrestricted release of this command. While you wait, why not try the new-and-improved `k.image` command? `k.help` for more! Sorry again, and thanks for being patient. -Epicfisher>")
        return

    play_message = ""

    if changed_channel:
        #await message.channel.send("I have changed my Music channel to '" + str(voice_channel) + "'")
        play_message = "Playing Music in new channel '" + str(voice_channel) + "'!"
    else:
        play_message = "Playing Music in '" + str(voice_channel) + "'!"

    radio_player = RadioPlayer()
    radio_player.voice_channel = voice_channel
    radio_player.play_message = play_message
    radio_player.saved_query = saved_query
    bot.radio_players.append(radio_player)
    #await bot.radio_players[len(bot.radio_players) - 1].Play(message) # Hopefully the one we just added???
    #bot.radio_players[len(bot.radio_players) - 1].Play(message) # Hopefully the one we just added???
    loop = asyncio.get_event_loop()
    loop.create_task(bot.radio_players[len(bot.radio_players) - 1].Play(message))

    #await play_music(message, vc)
    return

def check_argument_query(query):
    if query != None and len(query) > 0:
        if query[0] == '/' or query[0] == '\\':
            query = query[1:]

    return query

async def get_radio_player(guild_id):
    for i in range(0, len(bot.radio_players)):
        if not bot.radio_players[i].vc == None:
            if bot.radio_players[i].vc.guild.id == guild_id:
                return(bot.radio_players[i])
        else:
            break

    return None

async def playing_song(message):
    if await check_music_direct_message(message) == False:
        return False

    radio_player = await get_radio_player(message.author.guild.id)

    if radio_player == None:
        await message.channel.send("I'm not playing any Music!")
        return

    english_title = radio_player.song.english_title
    circle = radio_player.song.circle
    output = ""
    if english_title == "":
        if circle == "":
            output = "Now Playing: 「" + radio_player.song.title + "」\nFrom Album: '" + radio_player.song.english_raw_album + "'\n「" + radio_player.song.album + "」\n" + radio_player.song.friendly_url
        else:
            raw_album = radio_player.song.raw_album
            raw_english_title = radio_player.song.raw_english_title
            if not raw_album == "":
                raw_title = radio_player.song.raw_title
                if raw_english_title == "":
                    output = "Now Playing: 「" + radio_player.song.title + "」\nFrom Circle:「" + circle + "」\nFrom Album:「" + radio_player.song.album + "」\n\nArranged From Song:「" + raw_title + "」\nArranged From Album: '" + radio_player.song.english_raw_album + "'\n「" + radio_player.song.raw_album + "」\n" + radio_player.song.friendly_url
                else:
                    output = "Now Playing: 「" + radio_player.song.title + "」\nFrom Circle:「" + circle + "」\nFrom Album:「" + radio_player.song.album + "」\n\nArranged From Song: '" + raw_english_title + "'\n「" + raw_title + "」\nArranged From Album: '" + radio_player.song.english_raw_album + "'\n「" + radio_player.song.raw_album + "」\n" + radio_player.song.friendly_url
    else:
        output = "Now Playing: '" + english_title + "'\n「" + radio_player.song.title + "」\nFrom Album: '" + radio_player.song.english_raw_album + "'\n「" + radio_player.song.album + "」\n" + radio_player.song.friendly_url

    await message.channel.send(output)

    return

async def check_valid_request(message, radio_player):
    if len(radio_player.queue) >= 10:
        await message.channel.send("The Song Queue is full!")
        return False
    if not message.author in radio_player.voice_channel.members:
        await message.channel.send("How are you ever going to listen to that request if you're not in the Voice Channel?")
        return False
    #if message.author in radio_player.voice_channel.members:
    spam_request = False # For keeping track of if the User has two song instances in the queue, False for 0 and True for 1. If it finds another while it's True, the User has two Song Requests.
    for i in range(0, len(radio_player.queue)):
        if message.author.id == radio_player.queue[i].caller_id and not await check_music_manage_channel(message, False):
            if spam_request:
                await message.channel.send("You've already requested two songs to the Queue!")
                return False
            spam_request = True

    return True

async def handle_music_queue(message):
    if await check_music_direct_message(message) == False:
        return False

    radio_player = await get_radio_player(message.author.guild.id)

    if radio_player == None:
        await message.channel.send("I'm not playing any Music!")
        return

    if not radio_player.use_queue:
        if radio_player.saved_query == None:
            await message.channel.send("The Queue has been disabled!")
        else:
            if radio_player.automatic_queue_disable:
                #await message.channel.send("The Queue has been automatically disabled for customised music playback!\nIf you want to utilise a Queue, play completely random music with the command `" + bot.prefix + "play`!")
                await message.channel.send("The Queue has been automatically disabled for customised music playback!\nTo re-enable the Queue, enter the command `" + bot.prefix + "togglequeue`!")
            else:
                await message.channel.send("The Queue has been disabled!")
        return

    arguments = commands.GetArgumentsFromCommand(message.content)

    if arguments == False:
        if len(radio_player.queue) < 1:
            await message.channel.send("The Song Queue is empty!")
            return
        queue_string = "Current Music Queue:\n```"
        for i in range(0, len(radio_player.queue)):
            title = radio_player.queue[i].english_title
            if title == "":
                title = radio_player.queue[i].title

            if radio_player.queue[i].circle == "":
                album = radio_player.queue[i].english_raw_album
                circle = "ZUN"
            else:
                album = radio_player.queue[i].album
                circle = radio_player.queue[i].circle

            queue_string = queue_string + "#" + str(i + 1) + ") '" + title + "' - " + album + " - " + circle + "\n"
        queue_string = queue_string + "```"
        await message.channel.send(queue_string)
        return
    else:
        if not await check_valid_request(message, radio_player):
            return

        async with message.channel.typing():
            query = arguments[0]

            if len(radio_player.queue) > 0:
                song = await radio_player.get.handle_get_song(message, message.author.id, False, query, False, False, radio_player.queue[len(radio_player.queue) - 1].title)
            else:
                song = await radio_player.get.handle_get_song(message, message.author.id, False, query, False, False, radio_player.song.title)
            if song == False:
                return

            if not await check_valid_request(message, radio_player):
                return
            radio_player.queue.append(song)

            title = song.english_title # Let's use the English title here! (This should work 100% of the time for regular ZUN-created 2hu Music)
            if title == "": # Or, if it doesn't exist...
                title = song.title # We'll settle on the default and guarentted Japanese title instead. This will happen 100% of the time for any and all Doujins requested.

        await message.channel.send("'" + title + "' Added to the Queue in position #" + str(len(radio_player.queue)))

    return

async def check_music_direct_message(message):
    try:
        if message.author.voice:
            voice_channel = message.author.voice.channel
            return True
    except:
        await message.channel.send("Unfortunately, I don't work in Direct Messaging as of yet!\nIf you want me to play Music, invite me to a Server!")
        return False

async def check_music_manage_channel(message, display):
    perms = message.channel.permissions_for(message.author)
    if not perms.manage_channels:
        if display:
            await message.channel.send("You must have the 'Manage Channels' permission to perform that command!")
        return False
    return True

async def handle_manage_music(message, basic_control):
    if await check_music_direct_message(message) == False:
        return False

    if basic_control:
        if bot.moderatorOnlyMusic == False:
            return True

    if await check_music_manage_channel(message, True) == False:
        return False

    #saved_voice_channel = await search_data('music_channel-' + str(message.guild.id))
    #if saved_voice_channel == False:
        #await message.channel.send("I'm not playing any Music!")
        #return False

    return True

async def stop_music(message):
    output = await handle_manage_music(message, True)
    if output == False:
        return

    radio_player = await get_radio_player(message.guild.id)
    if not radio_player == None:
        await radio_player.Stop()
        return

    await message.channel.send("I'm not playing any Music!")
    return

async def stop_music_after(message):
    output = await handle_manage_music(message, True)
    if output == False:
        return

    radio_player = await get_radio_player(message.guild.id)
    if not radio_player == None:
        radio_player.stop_after = True
        await message.channel.send("Stopping Music Playback after finishing current song!")
        return

    await message.channel.send("I'm not playing any Music!")
    return

async def pause_music(message):
    output = await handle_manage_music(message, True)
    if output == False:
        return

    radio_player = await get_radio_player(message.guild.id)
    if not radio_player == None:
        await radio_player.Pause()
        return

    await message.channel.send("I'm not playing any Music!")
    return

async def skip_song(message):
    output = await handle_manage_music(message, True)
    if output == False:
        return

    radio_player = await get_radio_player(message.guild.id)
    if not radio_player == None:
        valid_members = 0
        for member in radio_player.voice_channel.members:
            if not member.bot:
                valid_members = valid_members + 1

        if valid_members == 1:
            if not radio_player.skip_cooldown == None:
                time_left = bot.music_cooldowntime - math.floor(time.time() - radio_player.skip_cooldown)
                if time_left > 0:
                    radio_player.vc.stop()
                    time.sleep(time_left)
            await radio_player.Skip()
            return

        output = await handle_manage_music(message, False)
        if output == False:
            return

        if not radio_player.skip_cooldown == None:
            time_left = bot.music_cooldowntime - math.floor(time.time() - radio_player.skip_cooldown)
            if time_left > 0:
                radio_player.vc.stop()
                time.sleep(time_left)
        await radio_player.Skip()
        return

    await message.channel.send("I'm not playing any Music!")
    return

async def vote_skip(message):
    output = await handle_manage_music(message, True)
    if output == False:
        return

    radio_player = await get_radio_player(message.guild.id)
    if not radio_player == None:
        await radio_player.VoteSkip(message)
        return

    await message.channel.send("I'm not playing any Music!")
    return

async def toggle_queue(message):
    output = await handle_manage_music(message, False)
    if output == False:
        return

    radio_player = await get_radio_player(message.guild.id)
    if not radio_player == None:
        await radio_player.Togglequeue()
        if radio_player.use_queue:
            await message.channel.send('The Queue has been Enabled!')
        else:
            radio_player.automatic_queue_disable = False
            await message.channel.send('The Queue has been Disabled!')
        return

    await message.channel.send("I'm not playing any Music!")
    return

async def change_volume(message):
    output = await handle_manage_music(message, False)
    if output == False:
        return

    arguments = commands.GetArgumentsFromCommand(message.content)

    force = False
    volume = 0.5

    if not arguments == False:
        volume = arguments[0]
        try:
            if arguments[1] == 'force':
                force = True
        except:
            pass

        if volume.endswith('force'):
            force = True
            volume = volume[:-5]

    string_volume = str(volume)

    if len(bot.radio_players) > 0:
        for i in range(0, len(bot.radio_players)):
            if not bot.radio_players[i].vc == None:
                if bot.radio_players[i].vc.guild.id == message.guild.id:
                    try:
                        volume = float(volume)
                    except:
                        await message.channel.send("You need to give me an actual volume number!\n(Minimum value is 0.0, maximum value is 1.0. Default is 0.5)")
                        return

                    if volume > 1.0 and not force:
                        await message.channel.send("But if I did that, that would wake up the mistress!\n(Force by adding 'force' to the end of your command. Might be loud. Don't say I didn't warn you)")
                        return

                    if volume > 10000:
                        await message.channel.send("Okay, now you're taking this a LITTLE too far, wouldn't you agree?")
                        return

                    try:
                        if len(string_volume[string_volume.index('.') + 1:]) >= 5:
                            await message.channel.send("Hey, do you really need the volume to be THAT precise?")
                            return
                    except:
                        pass

                    if arguments == False:
                        await message.channel.send("The Volume is currently set to " + str(bot.radio_players[i].src.volume) + ".")
                        return
                    await bot.radio_players[i].Volume(volume)
                    return
            else:
                break

    await message.channel.send("I'm not playing any Music!")
    return

async def playing(message):
    await playing_song(message)
    return

async def play(message):
    await play_music(message)
    return

async def queue(message):
    await handle_music_queue(message)
    return

async def stop(message):
    await stop_music(message)
    return

async def stopafter(message):
    await stop_music_after(message)
    return

async def pause(message):
    await pause_music(message)
    return

async def skip(message):
    await skip_song(message)
    return

async def voteskip(message):
    await vote_skip(message)
    return

async def togglequeue(message):
    await toggle_queue(message)
    return

async def volume(message):
    await change_volume(message)
    return

###

commands.Add("playing", playing)
commands.Add("nowplaying", playing, count=False)
commands.Add("play%", play)
commands.Add("queue%", queue)
commands.Add("request%", queue, count=False)
commands.Add("stop", stop)
commands.Add("leave", stop, count=False)
commands.Add("disconnect", stop, count=False)
commands.Add("stopafter", stopafter)
commands.Add("pause", pause)
commands.Add("unpause", pause, count=False)
commands.Add("resume", pause, count=False)
commands.Add("skip", skip)
commands.Add("voteskip", voteskip)
commands.Add("togglequeue", togglequeue)
commands.Add("volume%", volume)
