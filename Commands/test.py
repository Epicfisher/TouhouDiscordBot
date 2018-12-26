import commands

###

import bot
import asyncio

diagMessage = """```asciidoc
= Patchouli Knowledge Diagnosis Screen =

- Running %s other commands.
```"""

def tester_check(message):
    if message.author.id == bot.owner_id: # haha only I can test because I am a developer >:)
        return True
    return False

async def diagnostics(message):
    if not tester_check(message):
        return

    await message.channel.send(diagMessage % (len(bot.runningCommandsArray) - 1))

async def exception(message):
    if not tester_check(message):
        return

    raise ValueError('Manual test exception thrown.')
    return

async def test(message):
    if not tester_check(message):
        return

    counter = 0
    tmp = await message.channel.send('Calculating messages...')
    async for log in bot.client.logs_from(message.channel, limit=100):
        if log.author == message.author:
            counter += 1

    await tmp.edit('You have {} messages.'.format(counter))

async def sleep(message):
    if not tester_check(message):
        return

    await asyncio.sleep(5)
    await message.channel.send('Done sleeping')

async def cardraritytest(message):
    if not tester_check(message):
        return

    raw_names = await get_all_cards()

    card_options = GetCardOptions()
    card_options.get_rarity = True

    while True:
        try:
            random_card = randint(0, len(raw_names) - 1)
            card = await get_card_object(raw_names[random_card], card_options, True, False)
            print(card.rarity)
        except:
            pass

async def deadlythread(message):
    if not tester_check(message):
        return

    loop = asyncio.get_event_loop()
    await loop.run_in_executor(thread_pool, lambda: time.sleep(5000))
    print("Deadly Thread is Deadly No More\n")
    return

###

commands.Add("test.diag", diagnostics, count=False)
commands.Add("test.exception", exception, count=False)
commands.Add("test.test", test, count=False)
commands.Add("test.sleep", sleep, count=False)
commands.Add("test.raritytest", cardraritytest, count=False)
commands.Add("test.deadlythread", deadlythread, count=False)
