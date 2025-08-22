async def settings_col(client):
    db = client.admin
    col = db['settings']
    result = col.find({})
    return result