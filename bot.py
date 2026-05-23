import discord
import os

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)

# einfache Filterliste
bad_words = ["idiot", "dumm", "opfer", "hurensohn", "arsch"]

BOT_NAME = "ShadowBot"

@client.event
async def on_ready():
    print(f"{BOT_NAME} ist online als {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    content = message.content.lower()
    author_name = message.author.display_name

    # Bot Name zeigen
    if message.content.startswith("!name"):
        await message.channel.send(f"Mein Name ist {BOT_NAME}")
        return

    # User Info
    if message.content.startswith("!user"):
        await message.channel.send(f"Du bist: {author_name}")
        return

    # Beleidigung erkennen
    if any(word in content for word in bad_words):
        await message.channel.send(
            f"⚠️ Hey {author_name}, bleib bitte respektvoll im Chat."
        )
        return

    # kleine Chat-Reaktion
    if "hi" in content:
        await message.channel.send(f"Hey {author_name} 👋")

client.run(TOKEN)
