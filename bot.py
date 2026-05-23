import discord
import os
import requests

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GROQ_KEY = os.getenv("GROQ_KEY")

ALLOWED_CHANNEL_ID = 1507649049602424976  # dein Channel

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

def ask_ai(prompt, user):
    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {
                "role": "system",
                "content": (
                    "Du bist ein sehr frecher, sarkastischer Discord Bot. "
                    "Du darfst Leute leicht roasten und witzig provozieren, "
                    "aber KEINE echten Beleidigungen, keine Hasssprache."
                )
            },
            {"role": "user", "content": f"{user}: {prompt}"}
        ],
        "max_tokens": 200
    }

    r = requests.post(url, headers=headers, json=data, timeout=20)

    if r.status_code == 200:
        return r.json()["choices"][0]["message"]["content"]
    else:
        return "❌ KI Fehler"

@client.event
async def on_ready():
    print(f"Bot online als {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.channel.id != ALLOWED_CHANNEL_ID:
        return

    content = message.content.lower().strip()
    user = message.author.display_name

    # 👋 Begrüßung
    if content in ["hi", "hallo", "hey"]:
        await message.channel.send(f"👋 Hey {user}… was geht 😏")
        return

    # 🤖 AI Antwort
    async with message.channel.typing():
        reply = ask_ai(content, user)
        await message.channel.send(reply[:1900])

client.run(DISCORD_TOKEN)
