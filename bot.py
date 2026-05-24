import discord
import os
import requests

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GROQ_KEY = os.getenv("GROQ_KEY")

# NUR DIESER CHANNEL
ALLOWED_CHANNEL_ID = 1507649049602424976  # <- DEINE CHANNEL ID

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

# =========================
# MEMORY
# =========================
memory = []

# =========================
# AI FUNCTION
# =========================
def ask_ai(prompt, user):
    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_KEY}",
        "Content-Type": "application/json"
    }

    system_message = {
        "role": "system",
        "content": (
            "Du bist ein frecher deutscher Discord Bot mit türkischem Slang. "
            "Du antwortest lustig, locker und manchmal leicht provozierend. "
            "Du darfst Wörter wie 'manyak', 'ayri', 'pic', 'lan', 'abi' benutzen, "
            "aber bleib humorvoll und nicht extrem beleidigend. "
            "Du verhältst dich wie ein lustiger Freund aus Discord Calls. "
            "Du merkst dir Gespräche und Namen."
        )
    }

    messages = [system_message]

    # MEMORY (letzte Nachrichten)
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

    # Nur 1 Channel
    if message.channel.id != ALLOWED_CHANNEL_ID:
        return

    content = message.content.lower().strip()
    user = message.author.display_name

    # Begrüßung
    if content in ["hi", "hallo", "hey", "selam"]:
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

        # Nicht zu groß werden lassen
        if len(memory) > 20:
            memory[:] = memory[-20:]

        # Discord Limit
        reply = reply[:1900]

        await message.channel.send(reply)

client.run(DISCORD_TOKEN)
