import discord
import os

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print("Bot ist online")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("!gpt"):
        text = message.content[5:]

        await message.channel.send("Du hast geschrieben: " + text)

client.run(DISCORD_TOKEN)
