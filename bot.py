import discord
import os
import requests
import time

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GROQ_KEY = os.getenv("GROQ_KEY")

ALLOWED_CHANNEL_ID = 1507649049602424976  # <- DEIN CHANNEL

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)

memory = []
last_time = {}

PERSONALITY = """
Du bist ein frecher, sarkastischer Discord AI Bot.
Du antwortest auf alles im Chat.
Du darfst leicht frech sein, aber NICHT beleidigend.
"""

COOLDOWN_SECONDS = 3

def ask_ai(prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_KEY}",
        "Content-Type": "application/json"
    }

    messages = [{"role": "system", "content": PERSONALITY}]

    for m in memory[-8:]:
        messages.append(m)

    messages.append({"role": "user", "content": prompt})

    data = {
        "model": "llama-3.1-8b-instant",
        "messages": messages
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

    if message.channel.id != ALLOWED_CHANNEL_ID:
        return

    # Cooldown pro User
    now = time.time()
    uid = message.author.id

    if uid in last_time:
        if now - last_time[uid] < COOLDOWN_SECONDS:
            return

    last_time[uid] = now

    content = message.content

    if len(content) < 2:
        return

    async with message.channel.typing():
        reply = ask_ai(content)

        memory.append({"role": "user", "content": content})
        memory.append({"role": "assistant", "content": reply})

        if len(memory) > 30:
            memory = memory[-30:]

        if len(reply) > 2000:
            reply = reply[:1990]

        await message.channel.send(reply)

client.run(DISCORD_TOKEN)
