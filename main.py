import discord
from discord.ext import commands
import asyncio
import httpx
import os

# Cấu hình gốc
OWNER_ID = 1480239176329859195  
TOKEN_BOT = os.getenv('TOKEN_BOT')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Danh sách Admin (Lưu ID của bạn làm mặc định)
admins = [OWNER_ID]

@bot.event
async def on_ready():
    print(f'✅ Bot {bot.user} Online | Chủ: {OWNER_ID}')

# --- HỆ THỐNG QUẢN LÝ ADMIN ---

@bot.command()
async def themad(ctx, user_id: int):
    if ctx.author.id != OWNER_ID: return
    if user_id not in admins:
        admins.append(user_id)
        await ctx.send(f"✅ Đã thêm `{user_id}` vào hàng ngũ Admin.")
    else:
        await ctx.send("❌ ID này đã có quyền Admin rồi.")

@bot.command()
async def xoaad(ctx, user_id: int):
    if ctx.author.id != OWNER_ID: return
    if user_id == OWNER_ID:
        return await ctx.send("❌ Bạn không thể tự phế truất chính mình!")
    if user_id in admins:
        admins.remove(user_id)
        await ctx.send(f"🧹 Đã xóa quyền Admin của `{user_id}`.")
    else:
        await ctx.send("❌ ID này không có trong danh sách.")

@bot.command()
async def checkad(ctx):
    if ctx.author.id not in admins: return
    
    msg = "**🛡️ Danh sách Admin hiện tại:**\n"
    for i, ad_id in enumerate(admins, 1):
        status = "(Chủ)" if ad_id == OWNER_ID else "(Được cấp quyền)"
        msg += f"{i}. `{ad_id}` {status}\n"
    
    await ctx.send(msg)

# --- HỆ THỐNG TOKEN & CHIẾN ---

@bot.command()
async def addtoken(ctx):
    if ctx.author.id not in admins: return
    
    if not ctx.message.attachments:
        return await ctx.send("⚠️ Hãy đính kèm file .txt rồi gõ `!addtoken` nhé.")
    
    attachment = ctx.message.attachments[0]
    async with httpx.AsyncClient() as client:
        response = await client.get(attachment.url)
        content = response.text
        
    token_list = [line.strip() for line in content.split('\n') if line.strip()]
    
    with open("clones.txt", "a") as f:
        for t in token_list:
            f.write(t + "\n")
            
    await ctx.send(f"✅ Đã nạp thành công {len(token_list)} clone từ file `{attachment.filename}`.")

@bot.command()
async def check(ctx):
    if ctx.author.id not in admins: return
    count = sum(1 for line in open("clones.txt")) if os.path.exists("clones.txt") else 0
    await ctx.send(f"📊 Kho: {count} clone đang sẵn sàng.")

@bot.command()
async def xoatoken(ctx):
    if ctx.author.id not in admins: return
    if os.path.exists("clones.txt"):
        os.remove("clones.txt")
    await ctx.send("🧹 Kho token đã được dọn sạch.")

@bot.command()
async def join(ctx, invite_code):
    if ctx.author.id not in admins: return
    if not os.path.exists("clones.txt"):
        return await ctx.send("❌ Kho trống, hãy nạp token trước.")

    with open("clones.txt", "r") as f:
        tokens = [line.strip() for line in f.readlines() if line.strip()]

    await ctx.send(f"🚀 Admin **{ctx.author.name}** kích hoạt lệnh kéo {len(tokens)} clone (1.5s/acc)...")
    
    async with httpx.AsyncClient() as client:
        for token in tokens:
            url = f"https://discord.com/api/v10/invites/{invite_code}"
            headers = {"Authorization": token}
            try:
                res = await client.post(url, headers=headers)
                print(f"Join: {res.status_code}")
            except: pass
            await asyncio.sleep(1.5)

    await ctx.send("🏁 Quá trình kéo clone đã hoàn tất!")

if __name__ == "__main__":
    bot.run(TOKEN_BOT)
