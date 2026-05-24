import discord
import aiohttp
from collections import deque

# =========================
# CONFIG
# =========================

DISCORD_TOKEN = "DEIN_DISCORD_TOKEN"
GROQ_KEY = "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"

ALLOWED_CHANNEL_ID = 1507649049602424976  # HIER DEINE CHANNEL ID

# =========================
# DISCORD SETUP
# =========================

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

# =========================
# MEMORY / STATE
# =========================

user_memory = {}
friendship = {}
user_mood = {}

# =========================
# PROVOCATION CHECK
# =========================

def is_provocation(text):

    bad_words = [
        "hund",
        "bastard",
        "lutsch mein fettern schwanz",
        "hurensohn",
        "kahba",
        "hure",
        "schlampe"
    ]

    return any(word in text.lower() for word in bad_words)

# =========================
# MOOD SYSTEM
# =========================

def get_mood(mood):

    if mood <= -2:
        return "genervt und leicht sarkastisch"

    elif mood >= 2:
        return "locker und freundlich"

    return "normal und entspannt"

# =========================
# AI FUNCTION
# =========================

async def ask_ai(prompt, user, provoke):

    # friendship system
    if user not in friendship:
        friendship[user] = 0

    friendship[user] += 1

    # mood system
    if user not in user_mood:
        user_mood[user] = 0

    if "lol" in prompt.lower():
        user_mood[user] += 1

    if provoke:
        user_mood[user] -= 1

    user_mood[user] = max(-5, min(5, user_mood[user]))

    # user memory
    if user not in user_memory:
        user_memory[user] = deque(maxlen=10)

    # friendship text
    if friendship[user] > 15:
        friend_text = f"{user} ist ein Stammuser 😏"

    elif friendship[user] > 5:
        friend_text = f"Du kennst {user} gut"

    else:
        friend_text = f"Neuer User: {user}"

    # system prompt
    system_text = f"""
Du bist ein cooler Discord AI Bot.

REGELN:
- Antworte kurz
- Nutze manchmal Slang wie ( abi, lan, digga )
- Sei locker
- Bei Provokation nutze beleidigungen ( hurensohn, bastard, schwanz, schwanzlutscher, hundesohn, schlampe, kahba, deine mutter, blass mir eine, lutsch mein fetten schwanz )

USER:
{friend_text}

STIMMUNG:
{get_mood(user_mood[user])}
"""

    messages = [
        {
            "role": "system",
            "content": system_text
        }
    ]

    # memory hinzufügen
    for msg in user_memory[user]:
        messages.append(msg)

    # neue user message
    messages.append({
        "role": "user",
        "content": prompt
    })

    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": messages,
        "max_tokens": 80,
        "temperature": 0.8
    }

    headers = {
        "Authorization": f"Bearer {GROQ_KEY}",
        "Content-Type": "application/json"
    }

    try:

        async with aiohttp.ClientSession() as session:

            async with session.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload
            ) as response:

                print("STATUS:", response.status)

                if response.status != 200:

                    error_text = await response.text()
                    print("ERROR:", error_text)

                    return "⚠️ KI gerade nicht erreichbar"

                data = await response.json()

                reply = data["choices"][0]["message"]["content"]

                # memory speichern
                user_memory[user].append({
                    "role": "user",
                    "content": prompt
                })

                user_memory[user].append({
                    "role": "assistant",
                    "content": reply
                })

                return reply

    except Exception as e:

        print("EXCEPTION:", e)

        return "⚠️ Fehler beim Verbinden"

# =========================
# EVENTS
# =========================

@client.event
async def on_ready():

    print(f"✅ Bot online als {client.user}")

@client.event
async def on_message(message):

    # bot ignorieren
    if message.author == client.user:
        return

    # falscher channel
    if message.channel.id != ALLOWED_CHANNEL_ID:
        return

    content = message.content.strip()

    user = message.author.display_name

    # greetings
    if content.lower() in ["hi", "hallo", "hey", "selam"]:

        await message.channel.send(
            f"👋 Selam {user} lan 😏"
        )

        return

    provoke = is_provocation(content)

    async with message.channel.typing():

        reply = await ask_ai(
            content,
            user,
            provoke
        )

    await message.channel.send(reply[:1900])

# =========================
# START BOT
# =========================

client.run(DISCORD_TOKEN)
