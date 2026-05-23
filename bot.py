import discord
import os
import requests
import random
import time

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GROQ_KEY = os.getenv("GROQ_KEY")

ALLOWED_CHANNEL_ID = 1507649049602424976  # <- DEIN CHANNEL

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)

# ======================
# MEMORY + MOOD
# ======================
memory = []
user_names = {}
mood = 0  # -5 schlecht, +5 gut

last_time = {}
COOLDOWN = 3

# ======================
# MOOD REPLIES
# ======================
def get_mood_style():
    if mood <= -2:
        return "Du bist heute etwas genervt und sarkastisch."
    elif mood >= 2:
        return "Du bist heute freundlich und locker."
    else:
        return "Du bist neutral und ruhig."

# ======================
# AI
# ======================
def ask_ai(prompt, user):
    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_KEY}",
        "Content-Type": "application/json"
    }

    system = f"""
Du bist ein Discord AI Bot.

Regeln:
- Du antwortest auf alles.
- Du merkst dir User Namen.
- Du bist leicht frech/sarkastisch (kein echtes Beleidigen).
- Deine Stimmung: {get_mood_style()}
"""

    messages = [{"role": "system", "content": system}]

    # Memory
    for m in memory[-10:]:
        messages.append(m)

    messages.append({"role": "user", "content": f"{user}: {prompt}"})

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

# ======================
# EVENTS
# ======================
@client.event
async def on_ready():
    print(f"Bot online als {client.user}")

@client.event
async def on_message(message):
    global mood

    if message.author == client.user:
        return

    # nur 1 Channel
    if message.channel.id != ALLOWED_CHANNEL_ID:
        return

    user_id = message.author.id
    now = time.time()

    # cooldown
    if user_id in last_time:
        if now - last_time[user_id] < COOLDOWN:
            return

    last_time[user_id] = now

    content = message.content.strip()
    if len(content) < 2:
        return

    # Namen merken
    user_names[user_id] = message.author.display_name

    # Stimmung leicht verändern
    if "lol" in content.lower():
        mood += 1
    if "stupid" in content.lower():
        mood -= 1

    mood = max(-5, min(5, mood))

    async with message.channel.typing():
        reply = ask_ai(content, message.author.display_name)

        # Memory speichern
        memory.append({"role": "user", "content": content})
        memory.append({"role": "assistant", "content": reply})

        if len(memory) > 40:
            memory = memory[-40:]

        if len(reply) > 2000:
            reply = reply[:1990]

        await message.channel.send(reply)

client.run(DISCORD_TOKEN)
