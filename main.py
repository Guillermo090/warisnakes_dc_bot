import discord
from discord.ext import commands
import requests
import secrets_env
import os
import asyncio

intents = discord.Intents.all()
intents.message_content = True


bot = commands.Bot(
    command_prefix='!', 
    intents=intents,
    permissions=discord.Permissions(
        send_messages=True,
        embed_links=True,
        read_messages=True,
        add_reactions=True,
        manage_messages=True  # Para eliminar reacciones no permitidas
    )
)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

async def load():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            print(filename)
            await bot.load_extension(f"cogs.{filename[:-3]}")

async def main():
    async with bot:
        await load()
        await bot.start(secrets_env.TOKEN)

asyncio.run(main())