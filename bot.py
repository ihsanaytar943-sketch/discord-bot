import discord
import os
import requests
import random

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GROQ_KEY = os.getenv("GROQ_KEY")

# =========================
# NUR DIESER CHANNEL
# =========================
ALLOWED_CHANNEL_ID = 123456789012345678  # <- DEINE CHANNEL ID

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

# =========================
# MEMORY + FRIENDS + MOOD
# =========================
memory = []

friendship = {}

mood = 0
# -5 = genervt
#  0 = normal
# +5 = gute laune

# =========================
# MOOD TEXT
# =========================
def get_mood():
    global mood

    if mood <= -2:
        return "Du bist genervt, frech und sarkastisch."
    elif mood >= 2:
        return "Du bist freundlich, lustig und locker."
    else:
        return "Du bist normal, leicht frech und entspannt."

# =========================
# AI FUNCTION
# =========================
def ask_ai(prompt, user):

    global mood

    # Freundschaft erhöhen
    if user not in friendship:
        friendship[user] = 0

    friendship[user] += 1

    # Stimmung ändern
    if "lol" in prompt.lower():
        mood += 1

    if any(x in prompt.lower() for x in ["idiot", "stfu", "dumm"]):
        mood -= 1

    mood = max(-5, min(5, mood))

    # Freundschaft Text
    if friendship[user] > 15:
        friend_text = f"{user} ist einer deiner Lieblingsuser."
    elif friendship[user] > 5:
        friend_text = f"Du kennst {user} schon gut."
    else:
        friend_text = f"Du kennst {user} noch nicht so lange."

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_KEY}",
        "Content-Type": "application/json"
    }

    system_text = f"""
Du bist ein frecher deutscher Discord Bot mit türkischem Slang.

Du darfst Wörter wie:
- abi
- lan
- manyak
- ayri
- pic
- hurensohn
- schwanz
- hundesohn
- wixxer
- bastard

benutzen.

Du roastest Leute humorvoll.
Keine extremen Beleidigungen.

{friend_text}

Deine aktuelle Stimmung:
{get_mood()}
"""

    messages = [
        {
            "role": "system",
            "content": system_text
        }
    ]

    # MEMORY
    for m in memory[-10:]:
        messages.append(m)

    messages.append({
        "role": "user",
        "content": f"{user}: {prompt}"
    })

    data = {
        "model": "llama-3.1-8b-instant",
        "messages": messages,
        "max_tokens": 200,
        "temperature": 0.9
    }

    try:
        r = requests.post(
            url,
            headers=headers,
            json=data,
            timeout=20
        )

        print("STATUS:", r.status_code)

        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"]
        else:
            print(r.text)
            return "❌ KI Fehler"

    except Exception as e:
        print("ERROR:", e)
        return "❌ Verbindung Fehler"

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

    # Nur EIN Channel
    if message.channel.id != ALLOWED_CHANNEL_ID:
        return

    content = message.content.strip()
    user = message.author.display_name

    # Begrüßung
    if content.lower() in ["hi", "hallo", "hey", "selam"]:
        await message.channel.send(
            f"👋 Selam {user} lan 😏"
        )
        return

    # KI Antwort
    async with message.channel.typing():

        reply = ask_ai(content, user)

        # MEMORY SPEICHERN
        memory.append({
            "role": "user",
            "content": f"{user}: {content}"
        })

        memory.append({
            "role": "assistant",
            "content": reply
        })

        # MEMORY LIMIT
        if len(memory) > 20:
            memory[:] = memory[-20:]

        # Discord Limit
        reply = reply[:1900]

        await message.channel.send(reply)

client.run(DISCORD_TOKEN)
