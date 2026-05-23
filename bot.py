import discord
import os
import requests

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GROQ_KEY = os.getenv("GROQ_KEY")

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
            {"role": "user", "content": prompt}
        ]
    }

    r = requests.post(url, headers=headers, json=data)

    print("STATUS:", r.status_code)
    print("TEXT:", r.text)

    if r.status_code == 200:
        return r.json()["choices"][0]["message"]["content"]
    else:
        return "❌ KI Fehler"

@client.event
async def on_ready():
    print("Bot ist online")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    async with message.channel.typing():
        reply = ask_ai(message.content)

        await message.channel.send(reply[:2000])

client.run(DISCORD_TOKEN)
