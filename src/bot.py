import discord
from discord.ext import commands
import os 
from dotenv import load_dotenv
from rag import setup_rag, query_rag
from log import log_activity
import time
from datetime import datetime
from collections import defaultdict
from google.api_core.exceptions import ResourceExhausted

# Load các biến từ file .env (gồm API gemini key và discord token)
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
KB_path = r"D:\STUDY\DISCORD_BOT\Documents\information_client_basic.docx"

###### DISCORD BOT ########
'''
Trong discord.py thì intents dùng để xác định loại sự kiện (events) mà bot sẽ nhận được từ Discord
Cụ thể:
    - Trong Discord thì sẽ có nhiều loại sự kiện(events): như messages, người dùng join server, change status...
    - Để tối ưu và sử dụng hiệu quả thì cần phải bật intents phù hợp
'''
intents = discord.Intents.default() # Bật intents cơ bản
intents.message_content = True 

# Khởi tạo bot
bot = commands.Bot(command_prefix="@", intents=intents)

# Khởi tạo biến để lưu thời gian truy vấn cuối cùng của mỗi người
last_query_time = defaultdict(float)

# Status online của chatbot
@bot.event
async def on_ready():
    print(f"Bot {bot.user} is ready!")
    bot.rag_chain = setup_rag(KB_path)

# Greeting new member
@bot.event
async def on_member_join(member):
    channel = member.guild.system_channel
    if channel is not None:
        await channel.send(f"Chào mừng {member.mention} đến với server!")

# Tránh repeat và tránh hiểu lầm message là cmd
@bot.event 
async def on_message(message):
    if message.author == bot.user:
        return 
    elif message.content.strip() == bot.user.mention:
        await message.channel.send("Tôi - QT_Bot đây Ი︵𐑼")
        await message.channel.send("""\n✅ `@hello` - Để chào tôi \n✅ `@talk <nội dung>` - Trò chuyện cùng bot\n✅ `@addinfo <nội dung>` - Bổ sung thông tin vào KB\n✅ `@update` - Cập nhật lại cơ sở tri thức\nVí dụ: `@talk Đỗ Mạnh Đoan là ai?`""")
        return 
    
    # Cho phép xử lý các lệnh khác
    await bot.process_commands(message)

# Say hello
@bot.command(name="hello")
async def hello_command(ctx):
    await ctx.send("Xin chào bạn! Tôi là QT_bot đây, rất vui vì được trò chuyện với bạn")

 
'''
---------- Talk to QT_bot ----------
Input = Question or information which users want to talk
Return answer 
'''
@bot.command(name="talk")
async def talk_command(ctx, *, question):
    current_time = time.time()
    user_id = ctx.author.id
    if current_time - last_query_time[user_id] < 5:
        await ctx.send("Vui lòng chờ 5 giây trước khi gửi câu hỏi tiếp theo.")
        return
    last_query_time[user_id] = current_time
    await ctx.send("Đang xử lý જ⁀➴ Bạn chờ tôi chút nha! •⩊•")
    try:
        response = query_rag(bot.rag_chain, question)
        fallback_trigger_phrases = [
            "tôi không tìm thấy", "không rõ", "không có thông tin", "tôi không biết"
        ]
        if any(phrase in response.lower() for phrase in fallback_trigger_phrases):
            await ctx.send("Không tìm thấy trong KB, đang tìm kiến thức mở rộng từ Gemini...")
            try:
                gemini_response = bot.rag_chain.invoke(question)  # Dùng rag_chain thay vì llm_fallback
                if any(phrase in gemini_response.lower() for phrase in fallback_trigger_phrases):
                    await ctx.send(
                        "Xin lỗi, cả KB và Gemini đều chưa có thông tin phù hợp.\n"
                        "Bạn có thể bổ sung kiến thức bằng lệnh:\n"
                        "`@addinfo <nội dung>` để tôi học và phục vụ tốt hơn."
                    )
                    return
                else:
                    response = gemini_response
            except ResourceExhausted:
                await ctx.send("Đã vượt quá giới hạn quota Gemini API. Vui lòng thử lại sau")
                return
            except Exception as e:
                await ctx.send(f"Lỗi khi truy vấn Gemini: {str(e)}")
                return
        log_activity(ctx.author, question, response)
        MAX_MESSAGE_LENGTH = 1800
        if len(response) <= MAX_MESSAGE_LENGTH:
            await ctx.send(response)
        else:
            for i in range(0, len(response), MAX_MESSAGE_LENGTH):
                await ctx.send(response[i:i+MAX_MESSAGE_LENGTH])
        
    except Exception as e:
        await ctx.send(f"Lỗi: {str(e)}")

@bot.command(name="addinfo")
async def add_info_command(ctx, *, info):
    author_name = ctx.author.display_name.lower()
    info_lower = info.lower()
    
    # Ưu tiên
    self_identifiers = ["tôi", "là tôi", "là tao", "là tớ", "là mình", "mình là", "ta là", author_name]
    if any(s in info_lower for s in self_identifiers):
        priority = "high"
    else:
        priority = "normal"
    
    if len(info.strip()) < 10:
        await ctx.send("Thông tin quá ngắn, vui lòng cung cấp chi tiết hơn (ít nhất 10 ký tự).")
        return

    forbidden_words = ["dcm", "dm", "cac"]
    if any(word in info.lower() for word in forbidden_words):
        await ctx.send("Thông tin chứa nội dung không phù hợp.")
        return

    # Lưu thông tin vào file txt log
    with open(r"D:\STUDY\DISCORD_BOT\Documents\user_contributions.txt", "a", encoding="utf-8") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] {ctx.author} | Priority: {priority} | Info: {info}\n")

    # Update KB file (tùy chọn, có thể viết append .docx để bot tự học)
    from docx import Document
    doc = Document(KB_path)
    doc.add_paragraph(info)
    doc.save(KB_path)

    await ctx.send(f"Cảm ơn bạn đã cung cấp thông tin! Ưu tiên: {priority}. Bot sẽ cập nhật lại cơ sở tri thức.")

@bot.command(name="update")
async def update_command(ctx):
    await ctx.send("Đang cập nhật lại cơ sở tri thức...")
    try:
        bot.rag_chain = setup_rag(KB_path)
        await ctx.send("⤷ Cập nhật cơ sở tri thức thành công!")
    except Exception as e:
        await ctx.send(f"Lỗi khi cập nhật: {str(e)}")
            
# Hướng dẫn
# @bot.command(name = "guild")
# async def help_command(ctx):
#     await ctx.send("Dưới đây là các lệnh để sử dụng QT_Bot:\n")
#     await ctx.send("""
#     @hello - Chào bot
#     @talk <nội dung> - Trò chuyện cùng bot
#     @update - Cập nhật lại cơ sở tri thức
#     @guild - Hiển thị hướng dẫn sử dụng
#     @addinfo <nội dung> - Cập nhật thông tin vào kb
#     Ví dụ @talk Đỗ Mạnh Đoan là thằng nào?
#     """)
     
bot.run(DISCORD_TOKEN)