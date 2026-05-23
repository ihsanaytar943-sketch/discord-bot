import discord
import os
import requests

# ======================
# TOKENS
# ======================
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GROQ_KEY = os.getenv("GROQ_KEY")  # optional für KI

BOT_NAME = "ShadowBot"

# ======================
# INTENTS
# ======================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)

# ======================
# KI FUNCTION (optional)
# ======================
def ask_ai(prompt):
    if not GROQ_KEY:
        return "❌ Kein KI Key gesetzt"

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content": "Du bist ein hilfreicher deutscher Discord Bot."},
            {"role": "user", "content": prompt}
        ]
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
    print(f"{BOT_NAME} ist online als {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    content = message.content.lower()
    user = message.author.display_name

    # ------------------
    # COMMAND: NAME
    # ------------------
    if content.startswith("!name"):
        await message.channel.send(f"🤖 Mein Name ist {BOT_NAME}")
        return

    # ------------------
    # COMMAND: USER INFO
    # ------------------
    if content.startswith("!user"):
        await message.channel.send(f"👤 Du bist: {user}")
        return

    # ------------------
    # KI COMMAND
    # ------------------
    if content.startswith("!gpt"):
        prompt = message.content[5:].strip()

        if not prompt:
            await message.channel.send("❌ Schreib etwas nach !gpt")
            return

        async with message.channel.typing():
            answer = ask_ai(prompt)

            if len(answer) > 2000:
                answer = answer[:1990]

            await message.channel.send(answer)
        return

    # ------------------
    # SIMPLE REACTIONS
    # ------------------
    if "hi" in content:
        await message.channel.send(f"👋 Hey {user}")
        return

    if "lol" in content:
        await message.channel.send("😂 haha nice")
        return

client.run(DISCORD_TOKEN)
