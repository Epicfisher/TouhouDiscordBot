async def write_data_unsafe(key, data):
    try:
        await data_channel.send("[k]" + key + "[d]" + data)
        return True
    except:
        return False

async def get_data():
    try:
        return await data_channel.history().flatten()
    except:
        return False

async def search_data(key):
    data = await get_data()
    for data_piece in data:
        if data_piece.content.startswith("[k]" + key + "[d]"):
            return data_piece.content[data_piece.content.index("[d]") + 3:]

    return False

async def write_data(key, data):
    all_data = await get_data()
    for data_piece in all_data:
        if data_piece.content.startswith("[k]" + key + "[d]"):
            print("Data key already exists!")
            return False

    await write_data_unsafe(key, data)
    return True

async def edit_data(key, data, add_data_to_end):
    all_data = await get_data()
    for data_piece in all_data:
        if data_piece.content.startswith("[k]" + key + "[d]"):
            if add_data_to_end:
                await data_piece.edit(content="[k]" + key + "[d]" + data_piece.content[data_piece.content.index("[d]") + 3:] + data) # This will add on to the existing data piece
            else:
                await data_piece.edit(content="[k]" + key + "[d]" + data)
            return True

    print("Could not find data to edit!")
    return False

async def overwrite_data(key, data):
    all_data = await get_data()
    for data_piece in all_data:
        if data_piece.content.startswith("[k]" + key + "[d]"):
            await data_piece.edit(content="[k]" + key + "[d]" + data)
            return True

    await write_data_unsafe(key, data)
    return False

async def delete_data(key):
    all_data = await get_data()
    for data_piece in all_data:
        if data_piece.content.startswith("[k]" + key + "[d]"):
            await data_piece.delete()
            return True

    print("Could not find data to delete!")
    return False
