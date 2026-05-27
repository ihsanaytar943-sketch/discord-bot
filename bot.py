import discord
import os
import requests

# =========================
# TOKENS
# =========================
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GROQ_KEY = os.getenv("GROQ_KEY")

if not DISCORD_TOKEN:
    print("DISCORD_TOKEN fehlt")
    exit()

if not GROQ_KEY:
    print("GROQ_KEY fehlt")
    exit()

# =========================
# EIN CHANNEL
# =========================
ALLOWED_CHANNEL_ID = 1507649049602424976

# =========================
# DISCORD SETUP
# =========================
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

# =========================
# MEMORY / FRIENDS / MOOD
# =========================
memory = []
friendship = {}
mood = 0

# =========================
# PROVOCATION CHECK
# =========================
def is_provocation(text):

    bad_words = [
        "hund",
        "bastard",
        "hurensohn",
        "hure",
        "schlampe"
    ]

    return any(word in text.lower() for word in bad_words)

# =========================
# MOOD SYSTEM
# =========================
def get_mood():

    global mood

    if mood <= -2:
        return "genervt und sarkastisch"

    elif mood >= 2:
        return "locker und freundlich"

    else:
        return "normal und entspannt"

# =========================
# AI FUNCTION
# =========================
def ask_ai(prompt, user, provoke):

    global mood

    # Freundschaftssystem
    if user not in friendship:
        friendship[user] = 0

    friendship[user] += 1

    # Stimmung ändern
    if "lol" in prompt.lower():
        mood += 1

    if provoke:
        mood -= 1

    mood = max(-5, min(5, mood))

    # User Status
    if friendship[user] > 15:
        friend_text = f"{user} ist ein Stammuser 😏"

    elif friendship[user] > 5:
        friend_text = f"Du kennst {user} gut"

    else:
        friend_text = f"Neuer User: {user}"

    # System Prompt
    system_text = f"""
du bist abu olaf

regeln:
- dein name ist abu olaf
- wenn jemand fragt wer du bist:
  "ich bin abu olaf lan 😏"
- antworte kurz
- nutze manchmal:
  bruder, digga, lan
- sei lustig und leicht arrogant
- bleib immer in rolle
- nur deutsch
- nicht zu cringe
- immer klein schreiben

user status:
{friend_text}

stimmung:
{get_mood()}
"""

    if provoke:
        system_text += "\nder user hat dich beleidigt, du darfst frecher antworten"

    messages = [
        {
            "role": "system",
            "content": system_text
        }
    ]

    # Memory
    for m in memory[-10:]:
        messages.append(m)

    # Neue Nachricht
    messages.append({
        "role": "user",
        "content": f"{user}: {prompt}"
    })

    # API Request
    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama-3.1-8b-instant",
        "messages": messages,
        "temperature": 0.8,
        "max_tokens": 120
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

            response_data = r.json()

            return response_data["choices"][0]["message"]["content"]

        else:

            print(r.text)

            return f"❌ fehler {r.status_code}"

    except Exception as e:

        print("ERROR:", e)

        return "❌ verbindung fehlgeschlagen"

# =========================
# READY EVENT
# =========================
@client.event
async def on_ready():

    print(f"abu olaf ist online als {client.user}")

# =========================
# MESSAGE EVENT
# =========================
@client.event
async def on_message(message):

    global memory

    # Eigene Nachrichten ignorieren
    if message.author == client.user:
        return

    # Nur EIN Channel
    if message.channel.id != ALLOWED_CHANNEL_ID:
        return

    user_text = message.content
    user_name = message.author.name

    provoke = is_provocation(user_text)

    # Memory speichern
    memory.append({
        "role": "user",
        "content": f"{user_name}: {user_text}"
    })

    # Max Memory
    memory = memory[-20:]

    # AI Antwort
    reply = ask_ai(
        user_text,
        user_name,
        provoke
    )

    # Antwort speichern
    memory.append({
        "role": "assistant",
        "content": reply
    })

    # Discord Antwort
    await message.reply(reply)

# =========================
# BOT START
# =========================
client.run(DISCORD_TOKEN)import discord
import os
import requests

# =========================
# TOKENS
# =========================
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GROQ_KEY = os.getenv("GROQ_KEY")

if not DISCORD_TOKEN:
    print("DISCORD_TOKEN fehlt")
    exit()

if not GROQ_KEY:
    print("GROQ_KEY fehlt")
    exit()

# =========================
# EIN CHANNEL
# =========================
ALLOWED_CHANNEL_ID = 1507649049602424976

# =========================
# DISCORD SETUP
# =========================
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

# =========================
# MEMORY / FRIENDS / MOOD
# =========================
memory = []
friendship = {}
mood = 0

# =========================
# PROVOCATION CHECK
# =========================
def is_provocation(text):

    bad_words = [
        "hund",
        "bastard",
        "hurensohn",
        "hure",
        "schlampe"
    ]

    return any(word in text.lower() for word in bad_words)

# =========================
# MOOD SYSTEM
# =========================
def get_mood():

    global mood

    if mood <= -2:
        return "genervt und sarkastisch"

    elif mood >= 2:
        return "locker und freundlich"

    else:
        return "normal und entspannt"

# =========================
# AI FUNCTION
# =========================
def ask_ai(prompt, user, provoke):

    global mood

    # Freundschaftssystem
    if user not in friendship:
        friendship[user] = 0

    friendship[user] += 1

    # Stimmung ändern
    if "lol" in prompt.lower():
        mood += 1

    if provoke:
        mood -= 1

    mood = max(-5, min(5, mood))

    # User Status
    if friendship[user] > 15:
        friend_text = f"{user} ist ein Stammuser 😏"

    elif friendship[user] > 5:
        friend_text = f"Du kennst {user} gut"

    else:
        friend_text = f"Neuer User: {user}"

    # System Prompt
    system_text = f"""
du bist abu olaf

regeln:
- dein name ist abu olaf
- wenn jemand fragt wer du bist:
  "ich bin abu olaf lan 😏"
- antworte kurz
- nutze manchmal:
  bruder, digga, lan
- sei lustig und leicht arrogant
- bleib immer in rolle
- nur deutsch
- nicht zu cringe
- immer klein schreiben

user status:
{friend_text}

stimmung:
{get_mood()}
"""

    if provoke:
        system_text += "\nder user hat dich beleidigt, du darfst frecher antworten"

    messages = [
        {
            "role": "system",
            "content": system_text
        }
    ]

    # Memory
    for m in memory[-10:]:
        messages.append(m)

    # Neue Nachricht
    messages.append({
        "role": "user",
        "content": f"{user}: {prompt}"
    })

    # API Request
    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama-3.1-8b-instant",
        "messages": messages,
        "temperature": 0.8,
        "max_tokens": 120
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

            response_data = r.json()

            return response_data["choices"][0]["message"]["content"]

        else:

            print(r.text)

            return f"❌ fehler {r.status_code}"

    except Exception as e:

        print("ERROR:", e)

        return "❌ verbindung fehlgeschlagen"

# =========================
# READY EVENT
# =========================
@client.event
async def on_ready():

    print(f"abu olaf ist online als {client.user}")

# =========================
# MESSAGE EVENT
# =========================
@client.event
async def on_message(message):

    global memory

    # Eigene Nachrichten ignorieren
    if message.author == client.user:
        return

    # Nur EIN Channel
    if message.channel.id != ALLOWED_CHANNEL_ID:
        return

    user_text = message.content
    user_name = message.author.name

    provoke = is_provocation(user_text)

    # Memory speichern
    memory.append({
        "role": "user",
        "content": f"{user_name}: {user_text}"
    })

    # Max Memory
    memory = memory[-20:]

    # AI Antwort
    reply = ask_ai(
        user_text,
        user_name,
        provoke
    )

    # Antwort speichern
    memory.append({
        "role": "assistant",
        "content": reply
    })

    # Discord Antwort
    await message.reply(reply)

# =========================
# BOT START
# =========================
client.run(DISCORD_TOKEN)
