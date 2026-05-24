import discord
import aiohttp
from collections import deque

# =====================================
# DISCORD TOKEN
# =====================================

DISCORD_TOKEN = "DEIN_DISCORD_TOKEN"

# =====================================
# GROQ API KEY
# =====================================

GROQ_KEY = "DEIN_GROQ_API_KEY"

# =====================================
# CHANNEL ID
# =====================================

ALLOWED_CHANNEL_ID = 123456789012345678

# =====================================
# DISCORD SETUP
# =====================================

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

# =====================================
# MEMORY SYSTEME
# =====================================

user_memory = {}
friendship = {}
user_mood = {}

# =====================================
# PROVOKATION CHECK
# =====================================

def is_provocation(text):

    bad_words = [
        "idiot",
        "dumm",
        "stfu",
        "opfer",
        "trash",
        "noob"
    ]

    return any(word in text.lower() for word in bad_words)

# =====================================
# MOOD SYSTEM
# =====================================

def get_mood(value):

    if value <= -2:
        return "genervt"

    elif value >= 2:
        return "freundlich"

    return "normal"

# =====================================
# AI FUNKTION
# =====================================

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

    # memory
    if user not in user_memory:
        user_memory[user] = deque(maxlen=10)

    # friendship text
    if friendship[user] > 15:
        friend_text = f"{user} ist Stammuser 😏"

    elif friendship[user] > 5:
        friend_text = f"Du kennst {user} gut"

    else:
        friend_text = f"Neuer User: {user}"

    # system prompt
    system_prompt = f"""
Du bist ein cooler Discord AI Bot.

REGELN:
- Antworte kurz
- Nutze manchmal Slang wie abi, lan usw.
- Sei locker
- Keine krassen Beleidigungen
- Bei Provokation leicht frech

USER:
{friend_text}

STIMMUNG:
{get_mood(user_mood[user])}
"""

    messages = [
        {
            "role": "system",
            "content": system_prompt
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

                    error = await response.text()

                    print("API ERROR:", error)

                    return "⚠️ KI Fehler"

                data = await response.json()

                reply = data["choices"][0]["message"]["content"]

                # speichern
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

        print("FEHLER:", e)

        return "⚠️ Verbindungsfehler"

# =====================================
# READY EVENT
# =====================================

@client.event
async def on_ready():

    print("===================================")
    print(f"✅ BOT ONLINE ALS {client.user}")
    print("===================================")

# =====================================
# MESSAGE EVENT
# =====================================

@client.event
async def on_message(message):

    # bots ignorieren
    if message.author.bot:
        return

    # falscher channel
    if message.channel.id != ALLOWED_CHANNEL_ID:
        return

    content = message.content.strip()

    user = message.author.display_name

    # greetings
    if content.lower() in ["hi", "hey", "hallo", "selam"]:

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

# =====================================
# START BOT
# =====================================

print("BOT STARTET...")

try:

    client.run(DISCORD_TOKEN)

except Exception as e:

    print("BOT CRASH:", e)
