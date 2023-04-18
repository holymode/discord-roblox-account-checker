import aiohttp, discord
from discord.ext import tasks, commands

# set up the bot ----made-by-Holy#7875-----------------------------------------------------------------------------
bot_prefix = "!"
user_ids = [4415380132, 4415380132, 4415380132, 4415380132]  # Replace with the actual user IDs
post_channel:int = 1078752770221420685  # Replace with the actual channel ID
token = "xxxxx"  # Replace with the bot token
ping_role = "@everyone"

# vars ------------------------------------------------------------------------------------------------------------
allowed_mentions = discord.AllowedMentions(everyone=True)
client = commands.Bot(command_prefix=bot_prefix, help_command=None, intents=discord.Intents.all(), case_insensitive=False)
green = 0x3ace3a
red = 0xce3a3a

# -----------------------------------------------------------------------------------------------------------------


@client.event
async def on_ready():
    print("------------------------------------")
    print(f'Bot Name: {client.user.name}')
    print(f'Bot ID: {client.user.id}')
    print("------------------------------------")
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="roblox accounts.."))
    post_online_status.start()


online_status = {}


async def check_online_status(user_id):
    color = 0x2f3136
    headers = {'accept':'application/json', 'Content-Type':'application/json', }
    json_data = {'userIds':[user_id], }

    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://users.roblox.com/v1/users/{user_id}") as user_request:
            user_name_json = await user_request.json()
            user_name = user_name_json["displayName"].capitalize()

        async with session.post('https://presence.roblox.com/v1/presence/users', headers=headers, json=json_data) as response:
            if response.status != 200:
                return {'message': f"Error: {response.status} - {response.reason}", 'color': color, 'avatar': "https://www.pngall.com/wp-content/uploads/8/Warning-PNG-Picture.png"}

            status_json = await response.json()
            status = status_json['userPresences'][0]['userPresenceType']
            is_online = status in [1, 2]
            if user_id in online_status:
                if is_online and not online_status[user_id]:
                    online_status[user_id] = True
                    message = f"{user_name} is now online!"
                    color = green
                    ping = True

                elif not is_online and online_status[user_id]:
                    online_status[user_id] = False
                    message = f"T{user_name} is now offline."
                    color = red
                    ping = False
                else:
                    message = None
                    ping = False

            else:
                online_status[user_id] = is_online

                if is_online:
                    message = f"{user_name} is online!"
                    color = green
                    ping = False

                else:
                    message = f"{user_name} is offline."
                    color = red
                    ping = False


        async with session.get(f"https://thumbnails.roblox.com/v1/users/avatar?userIds={user_id}&size=720x720&format=Png&isCircular=false") as avatar_request:
            user_avatar_json = await avatar_request.json()
            user_avatar = user_avatar_json['data'][0]["imageUrl"]

        return {'message': message, 'color': color, "avatar": user_avatar, 'ping': ping}


@tasks.loop(seconds=60)
async def post_online_status():
    channel = client.get_channel(post_channel)

    messages = []
    ping = None
    for user_id in user_ids:
        message_dict = await check_online_status(user_id)
        if message_dict['message'] is not None:
            # Create an embed with the message and user profile link
            embed = discord.Embed(title=f"**{message_dict['message']}**", color=message_dict['color'])
            embed.set_author(name=f"User ID: {user_id}", url=f"https://www.roblox.com/users/{user_id}/profile")
            embed.set_thumbnail(url=message_dict['avatar'])
            embed.timestamp = discord.utils.utcnow()
            messages.append(embed)

            if message_dict['ping']:
                ping = ping_role

    if messages:
        await channel.send(content=ping, embeds=messages, allowed_mentions=allowed_mentions)


client.run(token)
