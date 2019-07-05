import commands

###

import bot
from random import randint
import discord

no_boys_tags = "-1boy+-2boys+-3boys+-4boys+-5boys+-6boys+-6%2Bboys"
no_girls_tags = "-1girl+-2girls+-3girls+-4girls+-5girls+-6girls+-6%2Bgirls"

characters_before = ['Aunn', 'Shikieiki', 'Yamaxanadu']
characters_after = ['Aun', 'Shiki', 'Eiki']

character_names = []
character_links = []

character_tags = []
character_genders = []

exclude_unless_wanted_tags = ['comic']
exclude_unless_wanted_lewd_tags = ['creepy']
exclude_unless_wanted_nsfw_tags = ['futa']

async def ParseCharacters(character_names, character_links):
    raw_characters_html = await bot.get("http://touhou.wikia.com/wiki/Character_List") # API is too confusing for a simpleton like me so I guess I'll just parse the webpage HTML don't mind me
    raw_characters_html = raw_characters_html[raw_characters_html.index('id="Character_List"'):raw_characters_html.index('id="Unnamed_Characters"')]

    while True:
        try:
            raw_characters_html = raw_characters_html[raw_characters_html.index('href="') + 6:]
            character_link = raw_characters_html[1:raw_characters_html.index('"')]
            character_link = character_link[character_link.index('/') + 1:]

            raw_characters_html = raw_characters_html[raw_characters_html.index('title="') + 7:]
            raw_character_name = raw_characters_html[:raw_characters_html.index('"')]
            for i in range(0, len(characters_before)):
                raw_character_name  = raw_character_name.replace(characters_before[i], characters_after[i])
            character_names.append(raw_character_name)
            character_links.append(character_link)
        except:
            break

    for i in range(0, len(character_names)):
        character_tags.append(None)
        character_genders.append(None)

async def PostImage(message, rating, tags, APILink, genders, negativeGenders):
    image_seperator_char = ' '
    image_space_char = '_'

    tags = "rating:" + rating + "+" + tags # Format and add the Rating into the total Tags

    bad_tags = ['guro']
    bad_lewd_tags = ['style_parody']
    bad_nsfw_tags = ['loli', 'shota']

    bad_sfw_tags = ['nude', 'pov_feet', 'ass', 'anus', 'thighs', 'underboob', 'sideboob', 'breasts', 'hanging_breasts', 'nipples', 'erect_nipples', 'topless', 'panties', 'striped_panties', 'underwear', 'underwear_only', 'thong', 'thong_bikini', 'micro_bikini', 'bandaids_on_nipples' 'panty_shot', 'cameltoe', 'dress_lift', 'skirt_lift', 'upskirt', 'under_skirt', 'no_panties', 'no_bra', 'removing_panties', 'pussy_juice', 'sexually_suggestive', 'suggestive_fluid', 'vibrator', 'rape', 'bdsm', 'sex', 'masturbation', 'fingering', 'implied_masturbation', 'futa', 'yuri', 'yaoi', 'vore', 'tentacles', 'cum', 'blood', 'vomit', 'piss', 'pee', 'peeing', 'toilet', 'toilet_use']

    arguments = commands.GetArgumentsFromCommand(message.content)

    additional_tags = ""
    additional_tags_list_check = []

    tags_array = []

    if not arguments == False:
        additional_tags = arguments[0]

        tags_array = additional_tags.split(image_seperator_char)
        if genders:
            if len(tags_array) > 6:
                await message.channel.send("How do you expect me to find *that* many people?\n(Please only enter a maximum of up to 6 characters!)")
                return

    boys = 0
    girls = 0

    async with message.channel.typing():
        if not arguments == False:
            #character_names = []
            #character_links = []
            #ParseCharacters(character_names, character_links)

            translations_before = ['patchy', 'raymoo', 'flan', 'gif', 'dab', 'pc98']
            translations_after = ['patchouli', 'reimu', 'flandre', 'animated_gif', 'dab_(dance)', 'touhou_(pc-98)']

            #tags_array = list(set(tags_array)) # Removes all Duplicate elements from the Array
            valid_tags = len(tags_array)
            additional_tags = ""
            i = 0
            for tag in tags_array:
                while tag.startswith(' '):
                    tag = tag[1:]
                while tag.endswith(' '):
                    tag = tag[0:-1]

                raw_tag = tag
                if tag.startswith('-'):
                    raw_tag = raw_tag[1:]

                for i in range(0, len(translations_before)):
                    if raw_tag.lower() == translations_before[i]:
                        new_tag = translations_after[i]
                        if tag.startswith('-'):
                            new_tag = '-' + new_tag

                        tag = new_tag
                        break

                character = ''
                character_index = None
                if tag.startswith("$") and tag.endswith("$"): # Disable Character Recognition
                    tag = tag[1:-1] # Hide the symbols
                else: # We don't want to disable Character Recognition
                    tag = tag.lower()

                    for i in range(0, len(characters_before)):
                        tag  = tag.replace(characters_before[i].lower(), characters_after[i].lower())

                    swap_names_back = False
                    found_character = False
                    #for character_name in character_names:
                    for i in range(0, len(character_names) - 1):
                        character_name = character_names[i]

                        if found_character:
                            break
                        character_index = i
                        character_array = character_name.split(" ")
                        if len(character_array) >= 2:
                            for character_word in character_array:
                                tag_words = tag.split(image_space_char)
                                for tag_word in tag_words:
                                    if tag_word == character_word.lower() and not character_word.lower() == 'no' and not character_word.lower() == 'giant' and not character_word.lower() == 'three' and not character_word.lower() == 'mischievous':
                                        if len(character_array) > 2:
                                            character = character_name.replace(" ", "_")
                                        else:
                                            character = character_array[1] + "_" + character_array[0]
                                            swap_names_back = True

                                        found_character = True
                                        break
                        else:
                            if tag == character_name.lower():
                                character = character_name

                                found_character = True
                                break

                if len(character) > 0:
                    if character_tags[character_index] == None:
                        keep_testing = True
                        try_end_touhou_tag = True
                        got_character = False
                        while keep_testing:
                            keep_testing = False

                            html = await bot.get(APILink + "?page=dapi&s=post&q=index&limit=1&json=1&pid=10&tags=" + tags + "+" + character) # We're going to check if our new name has atleast 10 results
                            if not "file_url" in html: # If it doesn't...
                                #print("Trying " + character)
                                if swap_names_back:
                                    if character.startswith(character_array[1]):
                                        character = character_array[0] + "_" + character_array[1] # Swap the names around again back to it's original positions
                                    else:
                                        character = character_array[1] + "_" + character_array[0] # Swap the names around again back to it's reversed positions
                                    swap_names_back = False
                                    keep_testing = True
                                    if not try_end_touhou_tag:
                                        character = character + "_(touhou)"
                                if not character.endswith("_(touhou)") and swap_names_back == False and keep_testing == False and try_end_touhou_tag:
                                    character = character + "_(touhou)"
                                    if len(character_array) == 2:
                                        swap_names_back = True
                                    keep_testing = True
                                    try_end_touhou_tag = False
                            else: # If we were able to find atleast 10 images of our character tag...
                                #print("Working " + character)
                                character_tags[character_index] = character # Cache our Tag!
                                keep_testing = False
                                got_character = True
                                tag = character
                    else:
                        got_character = True
                        tag = character_tags[character_index]

                    if not got_character:
                        valid_tags = valid_tags - 1
                        if valid_tags < 1:
                            #await message.channel.send("I couldn't find any pictures in my library on '" + arguments[0] + "'.")
                            await message.channel.send("I couldn't find an image!")
                            return
                        #await message.channel.send("I couldn't find an image of your character '" + tag + "'!\nPro Tip: Don't want me to treat a tag as a character? Simple! Just let me know by putting a '$' symbol at the start and end of your tag!")
                        #return
                        tag = ''

                if len(tag) > 0:
                    raw_tag = tag
                    if tag.startswith('-'):
                        raw_tag = raw_tag[1:]

                    is_good_tag = True

                    if raw_tag.startswith("rating"): # Disallow modification to the Rating tag
                        is_good_tag = False

                    for bad_tag in bad_tags: # Disallow certain tags. Cycle through all bad tags
                        if raw_tag == bad_tag: # Check for a match with the current tag
                            is_good_tag = False
                            break

                    if rating == "questionable": # Disallow certain tags if we're in Questionable
                        for bad_tag in bad_lewd_tags: # Cycle through all bad Lewd tags
                            if raw_tag == bad_tag: # Check for a match with the current tag
                                is_good_tag = False
                                break

                    if rating == "questionable" or rating == "explicit": # Disallow certain tags if we're NSFW
                        for bad_tag in bad_nsfw_tags: # Cycle through all bad NSFW tags
                            if raw_tag == bad_tag: # Check for a match with the current tag
                                is_good_tag = False
                                break

                    if rating == "safe": # Disallow certain tags if we're supposed to be SFW
                        for bad_tag in bad_sfw_tags: # Cycle through all bad SFW tags
                            if raw_tag == bad_tag: # Check for a match with the current tag
                                is_good_tag = False
                                break

                    if is_good_tag:
                        if not tag in additional_tags_list_check:
                            additional_tags_list_check.append(tag)
                            additional_tags = additional_tags + tag + '+'

                            if genders:
                                if not character == None and not character == '' and got_character:
                                    # Now that we have our unique working character 100%, let's get it's gender in preparation for adding it to the FINAL LIST
                                    if character_genders[character_index] == None:
                                        print("Getting Gender of '" + character + "' From '" + character_links[character_index] + "'")
                                        #print("https://touhou.fandom.com/wiki/" + character_links[character_index])
                                        gender = await bot.get("https://touhou.fandom.com/wiki/" + character_links[character_index])
                                        gender = gender[gender.index('id="PageHeader"') + 15:]
                                        gender = gender[:gender.index('</div>')]
                                        try:
                                            gender = gender[gender.index('class="page-header__categories-links">') + 38:]
                                        except:
                                            pass
                                        gender = gender[gender.index('<'):]
                                    else:
                                        print("Loading Cached Gender of '" + character + "' From '" + character_links[character_index] + "' As '" + character_genders[character_index][:-1] + "'")
                                        gender_check = character_genders[character_index]
                                    while True:
                                        try:
                                            if character_genders[character_index] == None:
                                                gender = gender[gender.index('/Category:') + 10:]
                                                gender_check = gender[:gender.index('"')]

                                            if gender_check == "Males":
                                                character_genders[character_index] = "Males" # Cache our Gender!
                                                boys += 1
                                                break
                                            if gender_check == "Females":
                                                character_genders[character_index] = "Females" # Cache our Gender!
                                                girls += 1
                                                break
                                        except:
                                            break

        boys_tag = ""
        if boys > 0:
            if negativeGenders:
                boys_tag += '-'
            if boys > 6:
                boys_tag = '6%2Bboys'
            else:
                boys_tag += str(boys) + "boy"
                if boys > 1:
                    boys_tag += 's'

        girls_tag = ""
        if girls > 0:
            if negativeGenders:
                girls_tag += '-'
            if girls > 6:
                girls_tag = '6%2Bgirls'
            else:
                girls_tag += str(girls) + "girl"
                if girls > 1:
                    girls_tag += 's'

        if not negativeGenders and rating == 'safe': # Generally if you search for a Safe image you only want 1 boy or 1 girl. Questionable or Explicit results though could have a mix of the two, so we'll disable this for those
            if girls > 0 and boys < 1:
                girls_tag = girls_tag + "+" + no_boys_tags
            if boys > 0 and girls < 1:
                boys_tag = boys_tag + "+" + no_girls_tags

        if not boys_tag == "":
            additional_tags += boys_tag + '+'
        if not girls_tag == "":
            additional_tags +=  girls_tag + '+'

        bad_tag = False

        for i in range(0, len(exclude_unless_wanted_tags)):
            for ii in range(0, len(tags_array)):
                bad_tag = False
                if exclude_unless_wanted_tags[i] == tags_array[ii].lower():
                    bad_tag = True
                    break
            if not bad_tag:
                additional_tags += '-' + exclude_unless_wanted_tags[i] + '+'

        if rating == "questionable":
            bad_tag = False

            for i in range(0, len(exclude_unless_wanted_lewd_tags)):
                for ii in range(0, len(tags_array)):
                    bad_tag = False
                    if exclude_unless_wanted_lewd_tags[i] == tags_array[ii].lower():
                        bad_tag = True
                        break
                if not bad_tag:
                    additional_tags += '-' + exclude_unless_wanted_lewd_tags[i] + '+'

        if rating == "questionable" or rating == "explicit":
            bad_tag = False

            for i in range(0, len(exclude_unless_wanted_nsfw_tags)):
                for ii in range(0, len(tags_array)):
                    bad_tag = False
                    if exclude_unless_wanted_nsfw_tags[i] == tags_array[ii].lower():
                        bad_tag = True
                        break
                if not bad_tag:
                    additional_tags += '-' + exclude_unless_wanted_nsfw_tags[i] + '+'

        for bad_tag in bad_tags: # Add a filter for all bad tags so they aren't shown
            additional_tags = additional_tags + '-' + bad_tag + '+'

        if rating == "questionable":
            for bad_tag in bad_lewd_tags: # Add a filter for all bad tags if we're in Questionable so they aren't shown
                additional_tags = additional_tags + '-' + bad_tag + '+'

        if rating == "questionable" or rating == "explicit":
            for bad_tag in bad_nsfw_tags: # Add a filter for all bad tags if we're NSFW so they aren't shown
                additional_tags = additional_tags + '-' + bad_tag + '+'

        if len(additional_tags) > 0:
            print("Using additional tags: '" + additional_tags[0:-1].replace(image_space_char, '_') + "'")

        additional_tags += "score:>=0+" # Filter our results with negative ratings, could be pornography or something else bad

        if rating == "safe":
            for bad_tag in bad_sfw_tags: # Add a filter for all bad tags if we're SFW so they aren't shown
                additional_tags = additional_tags + '-' + bad_tag + '+'

        if not additional_tags == None:
            tags = tags + '+' + additional_tags.replace(image_space_char, "_")

        while tags.endswith('+'):
            tags = tags[0:-1]  # Cut off the last '+'s

        html = await bot.get(APILink + "?page=dapi&s=post&q=index&limit=1&json=1&pid=1&tags=" + tags)
        if not "file_url" in html:
            await message.channel.send("I couldn't find an image!")
            return

        #print("Using total tags: '" + tags + "'")

        page_scope = 20000
        i = 1

        worked = False
        while not worked:
            html = await bot.get(APILink + "?page=dapi&s=post&q=index&limit=1&json=1&pid=" + str(randint(0, page_scope)) + "&tags=" + tags)

            try:
                fileUrl = html[html.index('file_url":"') + 11 : - 3]
                fileUrl = fileUrl.replace("\/", "/")
                fileUrl = fileUrl[0:fileUrl.index('"')]

                source = html[html.index('source":"') + 9:]
                source = source[:source.index('"')]
                source = source.replace("\/", "/")

                source = source.encode().decode("unicode-escape")

                print("Posting Image: " + fileUrl)
                if len(source) > 0:
                    print("Image Source: " + source)

                worked = True
            except:
                i = i + 1
                if i <= 2:
                    page_scope = int(page_scope / 2)
                else:
                    page_scope = int(page_scope / 3)

                if page_scope < 1:
                    await message.channel.send("I couldn't find an image!")
                    return
                #else:
                    #print("Dividing our search scope to '" + str(page_scope) + "'... [Attempt " + str(i) + "]") # Mainly for debug purposes

        messageEmbed = discord.Embed(color=bot.hex_color)
        messageEmbed.set_image(url=fileUrl)
        messageEmbed.add_field(name="Image URL", value=fileUrl, inline=False)
        if len(source) > 0:
            messageEmbed.add_field(name="Image Source",value=source, inline=False)

        await message.channel.send(embed=messageEmbed)

async def Check_Nsfwimage(message):
        isok = True

        try:
            if not message.channel.is_nsfw(): # If it isn't an NSFW channel, don't allow it
                isok = False
        except:
            pass

        if isok:
            return True
        else:
            print("Failed NSFW Image: Channel not NSFW!")
            bad_generic_channel_quotes = ["I-I don't think this is the kind of channel for THAT.", "S-Shouldn't we do that kind of stuff i-in another channel?"]

            bad_reimu_channel_quotes = ["You know, if you love Reimu so much, I'm sure she wouldn't mind a donation.", "I'm sure she'd appreciate a donation more than you looking at her pictures."]
            bad_patchy_channel_quotes = ["I-I hope you were referring to a *different* Patchouli.", "M-Me? Don't you have anybody else you'd rather stare at?"]
            bad_remilia_channel_quotes = ["You should consider yourself lucky I'm not reporting that.", "*Sigh* I'll overlook this with the Mistress this once."]
            bad_flandre_channel_quotes = ["You should consider yourself lucky she's still in the basement.", "You know, if she caught wind if you doing this, it wouldn't end well. For you."]
            bad_koakuma_channel_quotes = ["This request will have to get through me first.", "Careful. She's a... Nervermind."]

            bad_channel_quotes = bad_generic_channel_quotes

            message_lower = message.content.lower()
            if "reimu" in message_lower.split():
                bad_channel_quotes = bad_reimu_channel_quotes
            if "patchouli" in message_lower.split() or "patchy" in message_lower.split():
                bad_channel_quotes = bad_patchy_channel_quotes
            if "remilia" in message_lower.split():
                bad_channel_quotes = bad_remilia_channel_quotes
            if "flandre" in message_lower.split() or "flan" in message_lower.split():
                bad_channel_quotes = bad_flandre_channel_quotes
            if "koakuma" in message_lower.split():
                bad_channel_quotes = bad_koakuma_channel_quotes

            await message.channel.send(bad_channel_quotes[randint(0, len(bad_channel_quotes) - 1)] + "\n(That command only works in NSFW channels!)")
            return False

async def image(message):
    await PostImage(message, "safe", "touhou", "https://gelbooru.com/index.php", True, True)
    return

async def lewdimage(message):
    if await Check_Nsfwimage(message):
        await PostImage(message, "questionable", "touhou", "https://gelbooru.com/index.php", True, True)
    return

async def nsfwimage(message):
    if await Check_Nsfwimage(message):
        await PostImage(message, "explicit", "touhou", "https://gelbooru.com/index.php", True, True)
    return

async def photo(message):
    await PostImage(message, "safe", "touhou", "https://gelbooru.com/index.php", True, False)
    return

async def lewdphoto(message):
    if await Check_Nsfwimage(message):
        await PostImage(message, "questionable", "touhou", "https://gelbooru.com/index.php", True, False)
    return

async def nsfwphoto(message):
    if await Check_Nsfwimage(message):
        await PostImage(message, "explicit", "touhou", "https://gelbooru.com/index.php", True, False)
    return

###

commands.Add("imagewith%", image)
commands.Add("image%", photo)
commands.Add("lewdimagewith%", lewdimage, count=False)
commands.Add("lewdimage%", lewdphoto, count=False)
commands.Add("lewdwith%", lewdimage)
commands.Add("lewd%", lewdphoto)
commands.Add("nsfwimagewith%", nsfwimage, count=False)
commands.Add("nsfwimage%", nsfwphoto, count=False)
commands.Add("nsfwwith%", nsfwimage)
commands.Add("nsfw%", nsfwphoto)
