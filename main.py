import discord
from discord.ext import commands
import asyncio
import httpx
import os

# Cấu hình
OWNER_ID = 1480239176329859195  
TOKEN_BOT = os.getenv('TOKEN_BOT')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

admins = [OWNER_ID]

@bot.event
async def on_ready():
    print(f'✅ Bot {bot.user} Online | Fix lỗi 400 Ready')

# --- LỆNH JOIN FIX LỖI 400 ---
@bot.command()
async def join(ctx, invite_input):
    if ctx.author.id not in admins: return
    if not os.path.exists("clones.txt"): return await ctx.send("❌ Kho trống!")

    # Lọc mã mời chuẩn hơn (xử lý cả link dài và mã ngắn)
    invite_code = invite_input.split('/')[-1].split(' ')[0]

    with open("clones.txt", "r") as f:
        tokens = [line.strip() for line in f.readlines() if line.strip()]

    await ctx.send(f"🚀 Đang kéo {len(tokens)} clone vào `{invite_code}`...")

    async with httpx.AsyncClient() as client:
        for token in tokens:
            # URL chuẩn của Discord API v10
            url = f"https://discord.com/api/v10/invites/{invite_code}"
            
            headers = {
                "Authorization": token,
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            
            try:
                # FIX 400: Thêm json={} vào request
                res = await client.post(url, headers=headers, json={})
                
                if res.status_code == 200:
                    await ctx.send(f"✅ `{token[:10]}...`: Thành công.")
                elif res.status_code == 400:
                    await ctx.send(f"❌ `{token[:10]}...`: Lỗi 400 (Mã mời sai hoặc Token cần Verify SĐT).")
                elif res.status_code == 401:
                    await ctx.send(f"❌ `{token[:10]}...`: Token Die.")
                elif res.status_code == 429:
                    await ctx.send(f"⚠️ `{token[:10]}...`: Bị chặn IP (Rate Limit).")
                    await asyncio.sleep(15)
                else:
                    await ctx.send(f"❓ Lỗi {res.status_code}")
            except Exception as e:
                print(f"Error: {e}")
            
            await asyncio.sleep(3.0) # Nghỉ 3s cho an toàn

    await ctx.send("🏁 Hoàn tất!")

# Giữ nguyên các lệnh khác (themad, checkad, addtoken...) bên dưới
bot.run(TOKEN_BOT)
