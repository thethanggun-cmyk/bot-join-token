import discord
from discord.ext import commands
import asyncio
import httpx
import os

# Cấu hình
ADMIN_ID = 123456789012345678  # THAY ID DISCORD CỦA BẠN VÀO ĐÂY
TOKEN_BOT = os.getenv('TOKEN_BOT') # Lấy token từ biến môi trường của Render

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot {bot.user} đã sẵn sàng!')

# Lệnh nạp token clone
@bot.command()
async def addtoken(ctx, *, tokens):
    if ctx.author.id != ADMIN_ID: return
    token_list = tokens.split()
    with open("clones.txt", "a") as f:
        for t in token_list:
            f.write(t + "\n")
    await ctx.send(f"✅ Đã thêm {len(token_list)} clone.")

# Lệnh xóa sạch kho token
@bot.command()
async def xoatoken(ctx):
    if ctx.author.id != ADMIN_ID: return
    open("clones.txt", "w").close()
    await ctx.send("🧹 Kho token đã trống.")

# Lệnh kéo clone vào server (1.5s/acc)
@bot.command()
async def join(ctx, invite_code):
    if ctx.author.id != ADMIN_ID: return
    
    if not os.path.exists("clones.txt"):
        return await ctx.send("❌ Không có token nào trong kho.")

    with open("clones.txt", "r") as f:
        tokens = [line.strip() for line in f.readlines() if line.strip()]

    await ctx.send(f"🚀 Bắt đầu kéo {len(tokens)} clone với tốc độ 1.5s/acc...")

    async with httpx.AsyncClient() as client:
        for token in tokens:
            url = f"https://discord.com/api/v10/invites/{invite_code}"
            headers = {"Authorization": token}
            
            try:
                res = await client.post(url, headers=headers)
                if res.status_code == 200:
                    print(f"Thành công: {token[:10]}")
                else:
                    print(f"Lỗi {res.status_code}: {token[:10]}")
            except Exception as e:
                print(f"Lỗi kết nối: {e}")
            
            await asyncio.sleep(1.5) # Tốc độ bạn yêu cầu

    await ctx.send("🏁 Đã hoàn thành đợt kéo clone!")

bot.run(TOKEN_BOT)
