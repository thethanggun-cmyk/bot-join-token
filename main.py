import discord
from discord.ext import commands
import asyncio
import httpx
import os

# Cấu hình đã dán ID của bạn
ADMIN_ID = 1480239176329859195  
TOKEN_BOT = os.getenv('TOKEN_BOT')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Bot {bot.user} đã ONLINE và sẵn sàng chiến!')

@bot.command()
async def addtoken(ctx, *, tokens):
    if ctx.author.id != ADMIN_ID: return
    token_list = tokens.split()
    with open("clones.txt", "a") as f:
        for t in token_list:
            f.write(t + "\n")
    await ctx.send(f"✅ Đã nạp {len(token_list)} clone vào kho.")

@bot.command()
async def xoatoken(ctx):
    if ctx.author.id != ADMIN_ID: return
    if os.path.exists("clones.txt"):
        os.remove("clones.txt")
    await ctx.send("🧹 Đã dọn sạch kho token.")

@bot.command()
async def join(ctx, invite_code):
    if ctx.author.id != ADMIN_ID: return
    if not os.path.exists("clones.txt"):
        return await ctx.send("❌ Kho đang trống, nạp token đi bro!")

    with open("clones.txt", "r") as f:
        tokens = [line.strip() for line in f.readlines() if line.strip()]

    await ctx.send(f"🚀 Bắt đầu kéo {len(tokens)} clone (1.5s/acc)...")

    async with httpx.AsyncClient() as client:
        for token in tokens:
            url = f"https://discord.com/api/v10/invites/{invite_code}"
            headers = {"Authorization": token}
            try:
                res = await client.post(url, headers=headers)
                print(f"Status {res.status_code} cho token {token[:10]}")
            except:
                pass
            await asyncio.sleep(1.5)

    await ctx.send("🏁 Xong!")

if __name__ == "__main__":
    if TOKEN_BOT is None:
        print("❌ LỖI: Bạn chưa cài TOKEN_BOT trong Environment Variables trên Render!")
    else:
        bot.run(TOKEN_BOT)
