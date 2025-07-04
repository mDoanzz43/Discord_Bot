import os
from dotenv import load_dotenv
import discord
from discord.ext import commands

# Load biến môi trường
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# Tạo intents
intents = discord.Intents.default()
intents.message_content = True

# Khởi tạo bot
bot = commands.Bot(command_prefix="@", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot đã online với tên: {bot.user}")

@bot.command()
async def hello(cmd):
    await cmd.send("Xin chào bạn! Tôi là QT_BOT đẹp trai đây")

# Chạy bot
bot.run(DISCORD_TOKEN)