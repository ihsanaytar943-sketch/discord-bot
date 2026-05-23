import discord
import os
import requests
import time

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GROQ_KEY = os.getenv("GROQ_KEY")

ALLOWED_CHANNEL_ID = 1507649049602424976  # <- DEIN CHANNEL

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

# ======================
# MEMORY + MOOD
# ======================
memory = []
mood = 0
last_time = {}

COOLDOWN = 3

# ======================
# MOOD SYSTEM
# ======================
def mood_text():
    if mood <= -2:
        return "leicht sarkastisch und genervt"
    elif mood >= 2:
        return "freundlich und locker"
    else:
        return "neutral"

# ======================
# AI FUNCTION (STABLE)
# ======================
def ask_ai(prompt, user):
    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_KEY}",
        "Content-Type": "application/json"
    }

    system = f"""
Du bist ein Discord AI Bot.
Stil: {mood_text()}.

Regeln:
- Antworte kurz (2–5 Sätze)
- Kein Abbrechen
- Kein Spam
- Leicht frech/sarkastisch aber nicht beleidigend
"""

    messages = [{"role": "system", "content": system}]

    for m in memory[-6:]:
        messages.append(m)

    messages.append({"role": "user", "content": f"{user}: {prompt}"})

    data = {
        "model": "llama-3.1-8b-instant",
        "messages": messages,
        "max_tokens": 250,
        "temperature": 0.8
    }

    try:
        r = requests.post(url, headers=headers, json=data, timeout=20)

        print("STATUS:", r.status_code)
        print("TEXT:", r.text)

        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"]
        else:
            return "❌ KI Fehler"
    except Exception as e:
        print("ERROR:", e)
        return "❌ Verbindung Fehler"

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

    now = time.time()
    uid = message.author.id

    if uid in last_time:
        if now - last_time[uid] < COOLDOWN:
            return

    last_time[uid] = now

    content = message.content.strip()
    if len(content) < 2:
        return

    # Mood ändern
    if "lol" in content.lower():
        mood += 1
    if "stupid" in content.lower():
        mood -= 1

    mood = max(-5, min(5, mood))

    async with message.channel.typing():
        reply = ask_ai(content, message.author.display_name)

        # MEMORY
        memory.append({"role": "user", "content": content})
        memory.append({"role": "assistant", "content": reply})

        if len(memory) > 30:
            memory = memory[-30:]

        reply = reply[:1900]  # Discord safe limit

        await message.channel.send(reply)

client.run(DISCORD_TOKEN)
