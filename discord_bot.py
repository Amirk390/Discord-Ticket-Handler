import discord
import asyncio
from discord.ext import commands

# Define the bot token (replace with your bot token)
TOKEN = 'YMTI2OTk3NDI0MTQ1Nzk5OTg3Mg.GCurSS.IHr5vA10R9NuMY1RltDrYV6I4TJn6REn7xuNT8'

# Define the channel ID to search in (replace with your logs channel ID)
LOGS_CHANNEL_ID = 1184558240864944128

# Create an instance of the bot
bot = commands.Bot(command_prefix='!')

async def search_logs_for_user(username):
    logs_channel = bot.get_channel(LOGS_CHANNEL_ID)
    if not logs_channel:
        return f"Channel with ID {LOGS_CHANNEL_ID} not found."

    messages = await logs_channel.history(limit=100).flatten()  # Adjust limit as needed
    for message in messages:
        if username.lower() in message.content.lower():
            return f"User '{username}' found in message: {message.content}"

    return f"User '{username}' not found in the logs."

@bot.event
async def on_ready():
    print(f'Bot is ready. Logged in as {bot.user}')

# Run the bot
bot.run(TOKEN)
