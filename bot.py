import discord
import os
import requests

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GROQ_KEY = os.getenv("GROQ_KEY")

ALLOWED_CHANNEL_ID = 1507649049602424976  # <- DEINE CHANNEL ID

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

def ask_ai(prompt):
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
                "content": "Du bist ein frecher, sarkastischer Discord Bot. Du antwortest auf alles im Chat, aber bleibst humorvoll und nicht beleidigend."
            },
            {"role": "user", "content": prompt}
        ]
    }

    r = requests.post(url, headers=headers, json=data)

    if r.status_code == 200:
        return r.json()["choices"][0]["message"]["content"]
    else:
        print("KI FEHLER:", r.status_code, r.text)
        return "❌ KI Fehler"

@client.event
async def on_ready():
    print(f"Bot online als {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # nur 1 Channel
    if message.channel.id != ALLOWED_CHANNEL_ID:
        return

    # KEIN "hi" filter, KEIN anderes if davor!

    async with message.channel.typing():
        reply = ask_ai(message.content)

        if len(reply) > 2000:
            reply = reply[:1990]

        await message.channel.send(reply)

client.run(DISCORD_TOKEN)
