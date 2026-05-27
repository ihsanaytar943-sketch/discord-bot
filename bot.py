import discord
import os
import requests

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GROQ_KEY = os.getenv("GROQ_KEY")

# =========================
# TOKENS CHECK
# =========================
if not DISCORD_TOKEN:
    print("DISCORD_TOKEN fehlt")
    exit()

if not GROQ_KEY:
    print("GROQ_KEY fehlt")
    exit()

# =========================
# NUR EIN CHANNEL
# =========================
ALLOWED_CHANNEL_ID = 1507649049602424976

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
# MOOD TEXT
# =========================
def get_mood():
    if mood <= -2:
        return "genervt und leicht sarkastisch"
    elif mood >= 2:
        return "locker und freundlich"
    else:
        return "normal und entspannt"

# =========================
# AI FUNCTION
# =========================
def ask_ai(prompt, user, provoke):

    global mood

    if user not in friendship:
        friendship[user] = 0

    friendship[user] += 1

    # Stimmung ändern
    if "lol" in prompt.lower():
        mood += 1

    if provoke:
        mood -= 1

    mood = max(-5, min(5, mood))

    # Freundschaftssystem
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
Du bist Abu Olaf.

REGELN:
- Dein Name ist Abu Olaf
- Wenn jemand fragt wer du bist, sag:
  "Ich bin Abu Olaf lan 😏"
- Antworte kurz (1-2 Sätze)
- Nutze manchmal Wörter wie:
  bruder, digga, lan
- Sei lustig und arrogant
- Bleibe immer in deiner Rolle
- Schreib nur deutsch
- Schreib normal und nicht zu cringe
- Nicht nach jedem Satz beleidigen
- Wenn jemand dich beleidigt, darfst du frech antworten
- Immer klein schreiben

User Status:
{friend_text}

Stimmung:
{get_mood()}
"""

    if provoke:
        system_text += "\nDer User hat dich provoziert, du darfst etwas frecher antworten."

    messages = [{"role": "system", "content": system_text}]

    # Letzte Nachrichten merken
    for m in memory[-10:]:
        messages.append(m)

    messages.append({
        "role": "user",
        "content": f"{user}: {prompt}"
    })

    data = {
        "model": "llama-3.1-8b-instant",
        "messages": messages,
        "max_tokens": 120,
        "temperature": 0.7
    }

    try:
        r = requests.post(
            url,
            headers=headers,
            json=data,
            timeout=20
        )

        print("STATUS:", r.status_code)

        # Erfolgreich
        if r.status_code == 200:

            response_data = r.json()

            if (
                "choices" in response_data and
                len(response_data["choices"]) > 0
            ):
                return response_data["choices"][0]["message"]["content"]

            print("API FEHLER:", response_data)
            return "❌ keine antwort von der ki"

        else:
            print("FEHLER TEXT:", r.text)
            return f"❌ ki fehler ({r.status_code})"

    except Exception as e:
        print("ERROR:", e)
        return "❌ verbindung fehler"

# =========================
# READY EVENT
# =========================
@client.event
async def on_ready():
    print(f"Abu Olaf ist online als {client.user}")

# =========================
# MESSAGE EVENT
# =========================
@client.event
async def on_message(message):

    global memory

    # Eigene Nachrichten ignorieren
    if message.author == client.user:
        return

    # Nur EIN Channel erlaubt
    if message.channel.id != ALLOWED_CHANNEL_ID:
        return

    user_text = message.content
    user_name = message.author.name

    provoke = is_provocation(user_text)

    # User Nachricht speichern
    memory.append({
        "role": "user",
        "content": f"{user_name}: {user_text}"
    })

    # Memory begrenzen
    memory = memory[-20:]

    # AI Antwort holen
    reply = ask_ai(user_text, user_name, provoke)

    # Antwort speichern
    memory.append({
        "role": "assistant",
        "content": reply
    })

    # Discord Antwort
    await message.reply(reply)

# =========================
# BOT STARTEN
# =========================
client.run(DISCORD_TOKEN)import discord
import os
import requests

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GROQ_KEY = os.getenv("GROQ_KEY")

# =========================
# TOKENS CHECK
# =========================
if not DISCORD_TOKEN:
    print("DISCORD_TOKEN fehlt")
    exit()

if not GROQ_KEY:
    print("GROQ_KEY fehlt")
    exit()

# =========================
# NUR EIN CHANNEL
# =========================
ALLOWED_CHANNEL_ID = 1507649049602424976

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
# MOOD TEXT
# =========================
def get_mood():
    if mood <= -2:
        return "genervt und leicht sarkastisch"
    elif mood >= 2:
        return "locker und freundlich"
    else:
        return "normal und entspannt"

# =========================
# AI FUNCTION
# =========================
def ask_ai(prompt, user, provoke):

    global mood

    if user not in friendship:
        friendship[user] = 0

    friendship[user] += 1

    # Stimmung ändern
    if "lol" in prompt.lower():
        mood += 1

    if provoke:
        mood -= 1

    mood = max(-5, min(5, mood))

    # Freundschaftssystem
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
Du bist Abu Olaf.

REGELN:
- Dein Name ist Abu Olaf
- Wenn jemand fragt wer du bist, sag:
  "Ich bin Abu Olaf lan 😏"
- Antworte kurz (1-2 Sätze)
- Nutze manchmal Wörter wie:
  bruder, digga, lan
- Sei lustig und arrogant
- Bleibe immer in deiner Rolle
- Schreib nur deutsch
- Schreib normal und nicht zu cringe
- Nicht nach jedem Satz beleidigen
- Wenn jemand dich beleidigt, darfst du frech antworten
- Immer klein schreiben

User Status:
{friend_text}

Stimmung:
{get_mood()}
"""

    if provoke:
        system_text += "\nDer User hat dich provoziert, du darfst etwas frecher antworten."

    messages = [{"role": "system", "content": system_text}]

    # Letzte Nachrichten merken
    for m in memory[-10:]:
        messages.append(m)

    messages.append({
        "role": "user",
        "content": f"{user}: {prompt}"
    })

    data = {
        "model": "llama-3.1-8b-instant",
        "messages": messages,
        "max_tokens": 120,
        "temperature": 0.7
    }

    try:
        r = requests.post(
            url,
            headers=headers,
            json=data,
            timeout=20
        )

        print("STATUS:", r.status_code)

        # Erfolgreich
        if r.status_code == 200:

            response_data = r.json()

            if (
                "choices" in response_data and
                len(response_data["choices"]) > 0
            ):
                return response_data["choices"][0]["message"]["content"]

            print("API FEHLER:", response_data)
            return "❌ keine antwort von der ki"

        else:
            print("FEHLER TEXT:", r.text)
            return f"❌ ki fehler ({r.status_code})"

    except Exception as e:
        print("ERROR:", e)
        return "❌ verbindung fehler"

# =========================
# READY EVENT
# =========================
@client.event
async def on_ready():
    print(f"Abu Olaf ist online als {client.user}")

# =========================
# MESSAGE EVENT
# =========================
@client.event
async def on_message(message):

    global memory

    # Eigene Nachrichten ignorieren
    if message.author == client.user:
        return

    # Nur EIN Channel erlaubt
    if message.channel.id != ALLOWED_CHANNEL_ID:
        return

    user_text = message.content
    user_name = message.author.name

    provoke = is_provocation(user_text)

    # User Nachricht speichern
    memory.append({
        "role": "user",
        "content": f"{user_name}: {user_text}"
    })

    # Memory begrenzen
    memory = memory[-20:]

    # AI Antwort holen
    reply = ask_ai(user_text, user_name, provoke)

    # Antwort speichern
    memory.append({
        "role": "assistant",
        "content": reply
    })

    #import discord
import os
import requests

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GROQ_KEY = os.getenv("GROQ_KEY")

# =========================
# TOKENS CHECK
# =========================
if not DISCORD_TOKEN:
    print("DISCORD_TOKEN fehlt")
    exit()

if not GROQ_KEY:
    print("GROQ_KEY fehlt")
    exit()

# =========================
# NUR EIN CHANNEL
# =========================
ALLOWED_CHANNEL_ID = 1507649049602424976

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
# MOOD TEXT
# =========================
def get_mood():
    if mood <= -2:
        return "genervt und leicht sarkastisch"
    elif mood >= 2:
        return "locker und freundlich"
    else:
        return "normal und entspannt"

# =========================
# AI FUNCTION
# =========================
def ask_ai(prompt, user, provoke):

    global mood

    if user not in friendship:
        friendship[user] = 0

    friendship[user] += 1

    # Stimmung ändern
    if "lol" in prompt.lower():
        mood += 1

    if provoke:
        mood -= 1

    mood = max(-5, min(5, mood))

    # Freundschaftssystem
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
Du bist Abu Olaf.

REGELN:
- Dein Name ist Abu Olaf
- Wenn jemand fragt wer du bist, sag:
  "Ich bin Abu Olaf lan 😏"
- Antworte kurz (1-2 Sätze)
- Nutze manchmal Wörter wie:
  bruder, digga, lan
- Sei lustig und arrogant
- Bleibe immer in deiner Rolle
- Schreib nur deutsch
- Schreib normal und nicht zu cringe
- Nicht nach jedem Satz beleidigen
- Wenn jemand dich beleidigt, darfst du frech antworten
- Immer klein schreiben

User Status:
{friend_text}

Stimmung:
{get_mood()}
"""

    if provoke:
        system_text += "\nDer User hat dich provoziert, du darfst etwas frecher antworten."

    messages = [{"role": "system", "content": system_text}]

    # Letzte Nachrichten merken
    for m in memory[-10:]:
        messages.append(m)

    messages.append({
        "role": "user",
        "content": f"{user}: {prompt}"
    })

    data = {
        "model": "llama-3.1-8b-instant",
        "messages": messages,
        "max_tokens": 120,
        "temperature": 0.7
    }

    try:
        r = requests.post(
            url,
            headers=headers,
            json=data,
            timeout=20
        )

        print("STATUS:", r.status_code)

        # Erfolgreich
        if r.status_code == 200:

            response_data = r.json()

            if (
                "choices" in response_data and
                len(response_data["choices"]) > 0
            ):
                return response_data["choices"][0]["message"]["content"]

            print("API FEHLER:", response_data)
            return "❌ keine antwort von der ki"

        else:
            print("FEHLER TEXT:", r.text)
            return f"❌ ki fehler ({r.status_code})"

    except Exception as e:
        print("ERROR:", e)
        return "❌ verbindung fehler"

# =========================
# READY EVENT
# =========================
@client.event
async def on_ready():
    print(f"Abu Olaf ist online als {client.user}")

# =========================
# MESSAGE EVENT
# =========================
@client.event
async def on_message(message):

    global memory

    # Eigene Nachrichten ignorieren
    if message.author == client.user:
        return

    # Nur EIN Channel erlaubt
    if message.channel.id != ALLOWED_CHANNEL_ID:
        return

    user_text = message.content
    user_name = message.author.name

    provoke = is_provocation(user_text)

    # User Nachricht speichern
    memory.append({
        "role": "user",
        "content": f"{user_name}: {user_text}"
    })

    # Memory begrenzen
    memory = memory[-20:]

    # AI Antwort holen
    reply = ask_ai(user_text, user_name, provoke)

    # Antwort speichern
    memory.append({
        "role": "assistant",
        "content": reply
    })

    # Discord Antwort
    await message.reply(reply)

# =========================
# BOT STARTEN
# =========================
client.run(DISCORD_TOKEN) Discord Antwort
    await message.reply(reply)

# =========================
# BOT STARTEN
# =========================
client.run(DISCORD_TOKEN)
