import discord
from discord.ext import commands
import os 
from dotenv import load_dotenv
from rag import setup_rag, query_rag
from log import log_activity
import time 
from collections import defaultdict

# Load các biến từ file .env (gồm API gemini key và discord token)
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

###### DISCORD BOT ########
'''
Trong discord.py thì intents dùng để xác định loại sự kiện (events) mà bot sẽ nhận được từ Discord
Cụ thể:
    - Trong Discord thì sẽ có nhiều loại sự kiện(events): như messages, người dùng join server, change status...
    - Để tối ưu và sử dụng hiệu quả thì cần phải bật intents phù hợp
'''
intents = discord.Intents.default() # Bật intents cơ bản
intents.message_content = True # Cho phép bot đọc được nội dung các discord

# Khởi tạo bot
bot = commands.Bot(command_prefix="@", intents=intents)

# Khởi tạo biến để lưu thời gian truy vấn cuối cùng của mỗi người
last_query_time = defaultdict(float)

@bot.event
async def on_ready():
    print(f"Bot {bot.user} is ready!")
    bot.rag_chain = setup_rag(r"D:\STUDY\DISCORD_BOT\Documents\information_client_basic.docx")

@bot.event
async def on_member_join(member):
    channel = member.guild.system_channel
    if channel is not None:
        await channel.send(f"Chào mừng {member.mention} đến với server!")

@bot.event 
async def on_message(message):
    if message.author == bot.user:
        return 
    await bot.process_commands(message)

@bot.command(name="hello")
async def hello_command(ctx):
    await ctx.send("Xin chào! Tôi tôi là QT_bot đây")
    
@bot.command(name="ask")
async def ask_command(ctx, *, question):
    current_time = time.time()
    user_id = ctx.author.id
    if current_time - last_query_time[user_id] < 5:  # Giới hạn 1 truy vấn mỗi 5 giây
        await ctx.send("Vui lòng chờ 5 giây trước khi gửi câu hỏi tiếp theo.")
        return
    last_query_time[user_id] = current_time
    await ctx.send("Đang xử lý...")
    try:
        response = query_rag(bot.rag_chain, question)
        log_activity(ctx.author, question, response)
        await ctx.send(response)
    except Exception as e:
        await ctx.send(f"Lỗi: {str(e)}")

@bot.command(name="update")
async def update_command(ctx):
    await ctx.send("Đang cập nhật cơ sở tri thức...")
    bot.rag_chain = setup_rag(r"D:\STUDY\DISCORD_BOT\Documents\information_client_basic.docx")
    await ctx.send("Cơ sở tri thức đã được cập nhật!")
           
bot.run(DISCORD_TOKEN)