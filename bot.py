import discord
from discord.ext import commands
import asyncio
import httpx
import os
import re

# Cấu hình gốc
OWNER_ID = 1480239176329859195  
TOKEN_BOT = os.getenv('TOKEN_BOT')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

admins = [OWNER_ID]

@bot.event
async def on_ready():
    print(f'✅ Bot {bot.user} đã lên đèn!')

# --- QUẢN LÝ ADMIN ---
@bot.command()
async def themad(ctx, user_id: int):
    if ctx.author.id != OWNER_ID: return
    if user_id not in admins:
        admins.append(user_id)
        await ctx.send(f"✅ Đã cấp quyền Admin cho `{user_id}`.")

@bot.command()
async def xoaad(ctx, user_id: int):
    if ctx.author.id != OWNER_ID: return
    if user_id in admins and user_id != OWNER_ID:
        admins.remove(user_id)
        await ctx.send(f"🧹 Đã gỡ quyền Admin của `{user_id}`.")

@bot.command()
async def checkad(ctx):
    if ctx.author.id not in admins: return
    msg = "**🛡️ Danh sách Admin:**\n" + "\n".join([f"- `{ad}`" for ad in admins])
    await ctx.send(msg)

# --- QUẢN LÝ TOKEN ---
@bot.command()
async def addtoken(ctx):
    if ctx.author.id not in admins: return
    if not ctx.message.attachments:
        return await ctx.send("⚠️ Đính kèm file .txt rồi gõ `!addtoken` nhé.")
    
    attachment = ctx.message.attachments[0]
    async with httpx.AsyncClient() as client:
        res = await client.get(attachment.url)
        content = res.text
        
    token_list = [line.strip() for line in content.split('\n') if line.strip()]
    with open("clones.txt", "a") as f:
        for t in token_list: f.write(t + "\n")
    await ctx.send(f"✅ Đã nạp thêm {len(token_list)} clone vào kho.")

@bot.command()
async def xoatoken(ctx):
    if ctx.author.id not in admins: return
    if os.path.exists("clones.txt"): os.remove("clones.txt")
    await ctx.send("🧹 Kho token đã trống trơn.")

@bot.command()
async def check(ctx):
    if ctx.author.id not in admins: return
    count = sum(1 for line in open("clones.txt")) if os.path.exists("clones.txt") else 0
    await ctx.send(f"📊 Kho hiện tại: {count} clone.")

# --- LỆNH JOIN (HỖ TRỢ CẢ LINK VÀ MÃ) ---
@bot.command()
async def join(ctx, invite_input):
    if ctx.author.id not in admins: return
    if not os.path.exists("clones.txt"): return await ctx.send("❌ Kho trống, nạp file đi đã!")

    # Tự động lọc mã mời từ link (ví dụ discord.gg/abc -> lấy abc)
    invite_code = invite_input.split('/')[-1]

    with open("clones.txt", "r") as f:
        tokens = [line.strip() for line in f.readlines() if line.strip()]

    await ctx.send(f"🚀 **{ctx.author.name}** bắt đầu kéo {len(tokens)} clone vào mã `{invite_code}`...")

    async with httpx.AsyncClient() as client:
        for token in tokens:
            url = f"https://discord.com/api/v10/invites/{invite_code}"
            headers = {
                "Authorization": token,
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_8 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1"
            }
            try:
                res = await client.post(url, headers=headers)
                
                if res.status_code == 200:
                    await ctx.send(f"✅ `{token[:10]}...`: **Đã join thành công**.")
                elif res.status_code == 401:
                    await ctx.send(f"❌ `{token[:10]}...`: **TOKEN DIE** (Unauthorized).")
                elif res.status_code == 403:
                    await ctx.send(f"❌ `{token[:10]}...`: **BỊ CHẶN/CAPTCHA** (Forbidden).")
                elif res.status_code == 429:
                    await ctx.send(f"⚠️ `{token[:10]}...`: **BỊ RATE LIMIT** (Chờ xíu rồi chạy tiếp).")
                    await asyncio.sleep(10) # Nghỉ lâu hơn nếu dính rate limit
                else:
                    await ctx.send(f"❓ `{token[:10]}...`: Lỗi {res.status_code}")
            except Exception as e:
                await ctx.send(f"🔥 Lỗi hệ thống: {str(e)}")
            
            await asyncio.sleep(2.5) # Nghỉ 2.5s để giảm tỉ lệ bị quét

    await ctx.send("🏁 Đã chạy xong danh sách token!")

bot.run(TOKEN_BOT)
