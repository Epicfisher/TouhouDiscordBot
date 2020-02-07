import commands

###

import bot
import bot_io as io
import commands
import discord
from random import randint

class TradingCard:
    character_name = ""
    link = ""
    name = ""
    character_image = ""
    power = ""
    rarity = ""
    rarity_message = ""
    rarity_string = ""
    price = ""

class GetCardOptions:
    get_character_name = False
    get_link = False
    get_name = False
    get_image = False
    get_power = False
    get_rarity = False
    get_rarity_message = False
    get_rarity_string = False
    get_price = False

##################################################TRADING CARDS API############################################################
async def get_all_cards():
    html = await bot.get("https://en.touhouwiki.net/api.php?action=parse&prop=wikitext&format=json&page=Touhoudex_2/Touhoudex_2")

    raw_names = []

    keep_parsing = True
    while keep_parsing:
        try:
            html = html[html.index('}}') + 4:]
            html = html[html.index('{{Touhoudex 2/DexEntry') + 22:]
            for i in range(0, 2):
                html = html[html.index('|') + 1:]
            name = html[:html.index('|')]

            if not name == "None":
                raw_names.append(name)
        except:
            keep_parsing = False

    raw_names = raw_names[:-19] # Cut off misc. characters

    # Okay but add a few more back in though because they're pretty cool
    raw_names.append("TensokuG")
    raw_names.append("Kasen")
    raw_names.append("Satsuki")
    raw_names.append("EMarisa")
    raw_names.append("JKSanae")
    raw_names.append("MPSuika")
    raw_names.append("Ayakashi")

    return raw_names

async def get_card_object(raw_name, card_options, unboxing, print_in_console):
    character_html = await bot.get("https://en.touhouwiki.net/wiki/Touhoudex_2/" + raw_name)

    worked = False
    while not worked:
        card = TradingCard()

        if unboxing:
            card_options.get_rarity = True

        if card_options.get_rarity:
            card_options.get_power = True
        if card_options.get_rarity_message:
            card_options.get_rarity = True
            card_options.get_power = True
        if card_options.get_rarity_string:
            card_options.get_rarity = True
            card_options.get_power = True
        if card_options.get_price:
            card_options.get_power = True
        if card_options.get_link:
            card_options.get_character_name = True
        if card_options.get_name:
            card_options.get_character_name = True

        try: # New Template Parser
            character_name = character_html[character_html.index("vcard") + 4:]
            character_html = character_name
            if card_options.get_character_name:
                character_name = character_name[character_name.index("<b>") + 3:character_name.index("</b>")]
                if character_name.endswith("</a>"):
                    character_name = character_name[:-4]

                card.character_name = character_name

            if card_options.get_link:
                try:
                    link = character_name[character_name.index("href=") + 6:]
                    link = link[1:link.index('"')]
                    link = link[link.index("/") + 1:]
                except:
                    link = ""

                card.link = link

            if card_options.get_name:
                try:
                    name = character_name[character_name.index("<"):character_name.index(">") + 1]
                    name = character_name.replace(name, "")
                except:
                    name = character_name

                card.name = name

            if card_options.get_image:
                character_image = "Touhoudex 2/" + raw_name
                character_image = await bot.get_image(character_image, 1, True, False)

                card.character_image = character_image

            if card_options.get_power:
                power = character_html[character_html.index("Base Stats"):]
                #power = power[power.index("</tr>") + 5:power.index("</table>")]
                power = power[:power.index("</table>")]
                power = power[power.rfind("<td>") + 4:]
                power = power[:power.index("<") - 1]

                card.power = power

            #Lowest: 330
            #Highest: 720

            if card_options.get_rarity:
                rarity_remaining = float(power) - 330
                if rarity_remaining >= 390:
                    rarity = 10
                    rarity_symbol = ":white_circle:"
                else:
                    rarity = 0
                    rarity_symbol = ":blue_circle:"
                    while rarity_remaining >= 39:
                        rarity_remaining = rarity_remaining - 39
                        rarity = rarity + 1

                    if rarity >= 4:
                        rarity_symbol = ":red_circle:"
                        #if randint(0, 1) == 0:
                            #retry = True

                #rarity = rarity - 1

                card.rarity = rarity

                if unboxing:
                    rarity_check = randint(0, 10) - randint(0, 10) # Most commonly 0 to 5

                    if rarity_check < 0:
                        rarity_check = 0

                    if randint(1, 10) == 10:
                        if print_in_console:
                            print("Got lucky! Rarity check was previously '" + str(rarity_check) + "'")
                        #rarity_check = rarity_check + randint(1, 5)
                        rarity_check = rarity_check + 5

                    if rarity_check > 10:
                        rarity_check = 10

                    if rarity > rarity_check and bot.use_rarity_check:
                        if print_in_console:
                            print("Got a '" + str(rarity) + "', but was too unlucky to receive it with a rarity check of '" + str(rarity_check) + "'!")
                        return None

                    if print_in_console:
                        print("Posting with a rarity of '" + str(rarity) + "' and a rarity check of '" + str(rarity_check) + "'")

            if card_options.get_rarity_message:
                rarity_message = ""
                for i in range(0, 10):
                    if i <= rarity:
                        rarity_message = rarity_message + rarity_symbol
                    else:
                        rarity_message = rarity_message + ":black_circle:"

                card.rarity_message = rarity_message

            if card_options.get_rarity_string:
                rarity_string = "Common"
                #if card.rarity >= 4:
                    #rarity_string = "Rare"
                if card.rarity >= 1:
                    rarity_string = "Rare"
                if card.rarity >= 4:
                    rarity_string = "Epic"
                if card.rarity == 10:
                    rarity_string = "LEGENDARY"

                card.rarity_string = rarity_string

            if card_options.get_price:
                #price = int((int(power)*int(power)*int(power)*int(power)/2)/100000000) * (rarity + 1)
                #price = int((int(power)*int(power)*int(power)*2)/1000000) * (rarity + 1)
                price = int((int(power)*int(power)*int(power)*2)/1000000)

                if rarity >= 7:
                    for i in range(7, 10):
                        if rarity >= i:
                            price = price * 2

                card.price = price

            return card
        except: # Outdated Template Parser
            try:
                if print_in_console:
                    print("Outdated template parser not yet implemented!")
            except:
                if print_in_console:
                    print("Error parsing character page")

            return None

        ## Get 'Types' value(s) from character_page ( tokens required(?) )

##################################################TRADING CARDS############################################################
async def get_card(message):
    async with message.channel.typing():
        raw_names = await get_all_cards()

        #rarity_to_discover = 0
        #for i in range(0, 10):
            #if randint(0, 10) >= i:
                #rarity_to_discover += 1
            #else:
                #break

        worked = False
        while not worked:
            retry = False

            card_options = GetCardOptions()
            card_options.get_character_name = True
            card_options.get_link = True
            card_options.get_name = True
            card_options.get_image = True
            card_options.get_power = True
            card_options.get_rarity = True
            card_options.get_rarity_message = True
            card_options.get_rarity_string = True
            card_options.get_price = True

            card = None
            while card == None:
                random_card = randint(0, len(raw_names) - 1)

                #bot.use_rarity_check = False
                #random_card = 6                                    # 1 STAR CHARACTER
                #random_card = 2                                    # 2 STAR CHARACTER
                #random_card = 102                               # 5 STAR CHARACTER
                #random_card = 1                                    # 6 STAR CHARACTER
                #random_card = len(raw_names) - 5 # 7 STAR CHARACTER
                #random_card = len(raw_names) - 6 # 8 STAR CHARACTER
                #random_card = len(raw_names) - 2 # 9 STAR CHARACTER
                #random_card = len(raw_names) - 1 # 10 STAR CHARACTER

                card = await get_card_object(raw_names[random_card], card_options, True, True)

            embed = await view_card(card, message.author.display_name)

            await message.channel.send(embed=embed)
            worked = True

            return random_card

async def view_card(card, finder):
    embed = discord.Embed(title=finder.capitalize() + " found [ " + card.name + " ] < " + card.rarity_string + " >", color=bot.hex_color)
    embed.set_image(url=card.character_image.Url)
    embed.add_field(name="Power:", value=card.rarity_message, inline=False)
    #embed.add_field(name="Power:", value=power, inline=False)
    embed.add_field(name="Price:", value="¥" + str(card.price), inline=False)
    if len(card.link) > 0:
        embed.add_field(name="Character's Page:", value="https://en.touhouwiki.net/wiki/" + card.link, inline=False)

    return embed

async def view_card_handler(message):
    arguments = commands.GetArgumentsFromCommand(message.content)

    view_card_error_message = "You need to give me a Card number to view!\nGet one by typing `" + bot.prefix + "cards`"

    if arguments == False:
        await message.channel.send(view_card_error_message)
        return
    else:
        try:
            card_id_to_get = int(arguments[0]) - 1
        except:
            await message.channel.send(view_card_error_message)
            return

    if card_id_to_get < 0:
        await message.channel.send(view_card_error_message)
        return

    async with message.channel.typing():
        raw_names = await get_all_cards()

        id_to_lookup = message.author.id

        try:
            if not arguments[1] == None:
                id_to_lookup = arguments[1]
        except:
            pass

        possessive = "Their"
        if str(id_to_lookup) == str(message.author.id):
            possessive = "Your"

        cards = await search_data("owned_cards-" + str(id_to_lookup))
        if cards == False:
            await message.channel.send("No cards available!")
            return

        cards_list = cards[:-1].split(';')

        try:
            if not cards_list[card_id_to_get] == None:
                pass
        except:
            await message.channel.send("The Card number you've given me doesn't exist!")
            return

        card_options = GetCardOptions()
        card_options.get_character_name = True
        card_options.get_link = True
        card_options.get_name = True
        card_options.get_image = True
        card_options.get_power = True
        card_options.get_rarity = True
        card_options.get_rarity_message = True
        card_options.get_rarity_string = True
        card_options.get_price = True

        card = await get_card_object(raw_names[int(cards_list[card_id_to_get])], card_options, False, False)

        embed = await view_card(card, message.author.display_name)
        embed.title = "Viewing " + possessive.lower() + " [ " + card.name + "]"

        await message.channel.send(embed=embed)
        return

async def get_cards(message):
    async with message.channel.typing():
        page_number = 0

        arguments = commands.GetArgumentsFromCommand(message.content)

        id_to_lookup = message.author.id

        try:
            if not arguments[1] == None:
                id_to_lookup = arguments[1]
        except:
            pass

        possessive = "They"
        if str(id_to_lookup) == str(message.author.id):
            possessive = "You"

        cards = await search_data("owned_cards-" + str(id_to_lookup))
        if cards == False:
            await message.channel.send(possessive + " don't have any cards!")
            return

        cards_list = cards[:-1].split(';')

        last_page_number = math.floor((len(cards_list) - 1) / 5)

        if not arguments == False:
            if arguments[0].lower() == 'last':
                page_number = last_page_number
            else:
                try:
                    page_number = int(arguments[0]) - 1
                except:
                    page_number = 0

        try:
            if not cards_list[page_number * 5] == None:
                pass
        except:
            await message.channel.send("That page doesn't exist!")
            return

        raw_names = await get_all_cards()
        cards_array = []

        for i in range(page_number * 5, page_number * 5 + 5):
            try:
                card_options = GetCardOptions()
                card_options.get_name = True
                card_options.get_rarity_message = True

                card = await get_card_object(raw_names[int(cards_list[i])], card_options, False, True)

                cards_array.append("`Card " + str(i + 1) + ") [ " + card.name + " ] |` " + card.rarity_message + "\n")
            except:
                break

        max_length = 0
        for i in range(0, len(cards_array)):
            real_card = cards_array[i]
            real_card = real_card[1:real_card.index('|') -1]
            if len(real_card) > max_length:
                max_length = len(real_card)

        for i in range(0, len(cards_array)):
            real_card = cards_array[i]
            real_card = real_card[1:real_card.index('|') -1]

            cards_array[i] = cards_array[i].replace("|", (' ' * (max_length - len(real_card))) + "|")

        if len(cards_list) == 1:
            cards_array.insert(0, possessive + " currently own `" + str(len(cards_list)) + "` card!\n\n")
        else:
            cards_array.insert(0, possessive + " currently own `" + str(len(cards_list)) + "` cards!\n\n")

        cards_string = ''
        for i in range(0, len(cards_array)):
            cards_string = cards_string + cards_array[i]

        ending_string = '\n' + "Page " + str(page_number + 1) + " of " + str(last_page_number + 1) + "\n\n"

        if page_number > 0:
            ending_string = ending_string + "Previous Page: `" + bot.prefix + "cards" + bot.argumentChar + str(page_number) + bot.argumentKillChar

            if possessive == "They":
                ending_string = ending_string + bot.argumentSeperator + id_to_lookup

            ending_string = ending_string + "`"

        if page_number < last_page_number:
            if page_number > 0:
                ending_string = ending_string + " | "
            ending_string = ending_string + "Next Page: `" + bot.prefix + "cards" + bot.argumentChar + str(page_number + 2) + bot.argumentKillChar

            if possessive == "They":
                ending_string = ending_string + bot.argumentSeperator + id_to_lookup

            ending_string = ending_string + "`"

        await message.channel.send(cards_string + ending_string)

        return

async def daily(message):
    i = 0
    for command in bot.runningCommandsArray:
        if message.author.id == command:
            i = i + 1
        if i >= 2:
            await message.channel.send(bot.cooldown_message)
            return

    #all_owned_cards = await io.search_data("owned_cards-" + str(message.author.id))
    #if not all_owned_cards == False and len(all_owned_cards) >= 1995:
        #print("You have too many cards! Please remove one in order to receive your Daily Card!")

    #update_daily_cooldown = False
    #if await write_data("daily_card_cooldown-" + str(message.author.id), str(time.time())) == False:
        #print(str("It has been '" + str((((time.time() - float(await search_data("daily_card_cooldown-" + str(message.author.id)))) / 60) / 60))) + "' Hours since your last Daily.")
        #if (((time.time() - float(await search_data("daily_card_cooldown-" + str(message.author.id)))) / 60) / 60) >= 24: # If this user has already waited 24 Hours...
            #update_daily_cooldown = True
        #else:
            #await message.channel.send("You've already received your daily card!")
            #return

    card_id = await get_card(message)

    #if await io.write_data("owned_cards-" + str(message.author.id), str(card_id) + ";") == False:
        #await io.edit_data("owned_cards-" + str(message.author.id), str(card_id) + ";", True)

    #if update_daily_cooldown: # Make sure the user got their card before updating their cooldown, just in case
        #await io.edit_data("daily_card_cooldown-" + str(message.author.id), str(time.time()), False) # Update the Cooldown

    return

async def cards(message):
    await get_cards(message)
    return

async def view(message):
    await view_card_handler(message)
    return

###

#commands.Add("daily", daily)
commands.Add("card", daily)
#commands.Add("cards", cards)
#commands.Add("view", view)
