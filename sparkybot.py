# main.py
import keyid
import discord

import commands # Stores all commands used for the bot.

intents = discord.Intents.all()

bot = commands.create_bot(intents)

@bot.event
async def on_ready():
    print("SparkyBot is online.")

bot.run(keyid.BOT_TOKEN)
