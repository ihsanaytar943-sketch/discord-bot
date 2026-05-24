import discord
import os
import requests
import asyncio
from collections import deque

# =========================
# CONFIG
# =========================
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GROQ_KEY = os.getenv("GROQ_KEY")

ALLOWED_CHANNEL_ID = 1507649049602424976  # DEIN CHANNEL

# =========================
# DISCORD SETUP
# =========================
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# =========================
# MEMORY / STATE
# =========================
memory = deque(maxlen=20)
friendship = {}
user_mood = {}

# =========================
# PROVOCATION CHECK
# =========================
def is_provocation(text):
    bad_words = ["hund", "ayri", "schwanz", "hurensohn", "schlampe", "köpek", "schwanzlutscher"]
    return any(word in text.lower() for word in bad_words)

# =========================
# MOOD
# =========================
def get_mood(m):
    if m <= -2:
        return "genervt und leicht sarkastisch"
    elif m >= 2:
        return "locker und freundlich"
    else:
        return "normal und entspannt"

# =========================
# AI FUNCTION
# =========================
def ask_ai(prompt, user, provoke):

    if GROQ_KEY is None:
        return "❌ Kein API Key gesetzt"

    # friendship system
    if user not in friendship:
        friendship[user] = 0
    friendship[user] += 1

    # mood system pro user
    if user not in user_mood:
        user_mood[user] = 0

    if "lol" in prompt.lower():
        user_mood[user] += 1

    if provoke:
        user_mood[user] -= 1

    user_mood[user] = max(-5, min(5, user_mood[user]))

    # friend status
    if friendship[user] > 15:
        friend_text = f"{user} ist ein Stammuser 😏"
    elif friendship[user] > 5:
        friend_text = f"Du kennst {user} gut"
    else:
        friend_text = f"Neuer User: {user}"

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_KEY}",
        "Content-Type": "application/json"
    }

    system_text = f"""
Du bist ein Discord AI Bot.

REGELN:
- Antworte kurz (1–3 Sätze)
- Nutze manchmal Slang ( bruder, auf ernst, etc.)
- Sei freundlich zu normalen Usern
- Nur bei Beleidigungen zurück beleidgen ( hurensohn, hundesohn, schlampe, kahba, ayri, schwanzlutscher, deine mutter geht anschaffen für 10 euro, blass mir eine ) 

User Status:
{friend_text}

Stimmung:
{get_mood(user_mood[user])}
"""

    if provoke:
        system_text += "\nDer User hat dich provoziert, reagiere etwas frecher."

    messages = [{"role": "system", "content": system_text}]

    for m in memory:
        messages.append(m)

    messages.append({"role": "user", "content": prompt})

    data = {
        "model": "llama3-8b-8192",
        "messages": messages,
        "max_tokens": 80,
        "temperature": 0.8
    }

    try:
        r = requests.post(url, headers=headers, json=data, timeout=20)

        print("STATUS:", r.status_code)

        if r.status_code != 200:
            print("ERROR:", r.text)
            return "⚠️ KI gerade nicht erreichbar"

        data = r.json()

        if "choices" not in data:
            print("BAD RESPONSE:", data)
            return "⚠️ KI Antwort kaputt"

        return data["choices"][0]["message"]["content"]

    except Exception as e:
        print("EXCEPTION:", e)
        return "⚠️ Fehler beim Verbinden"

# =========================
# EVENTS
# =========================
@client.event
async def on_ready():
    print(f"Bot online als {client.user}")

@client.event
async def on_message(message):

    if message.author == client.user:
        return

    if message.channel.id != ALLOWED_CHANNEL_ID:
        return

    content = message.content.strip()
    user = message.author.display_name

    if content.lower() in ["hi", "hallo", "hey", "selam"]:
        await message.channel.send(f"👋 Selam {user} lan 😏")
        return

    provoke = is_provocation(content)

    async with message.channel.typing():
        reply = await asyncio.to_thread(ask_ai, content, user, provoke)

    memory.append({"role": "user", "content": content})
    memory.append({"role": "assistant", "content": reply})

    await message.channel.send(reply[:1900])

client.run(DISCORD_TOKEN)
