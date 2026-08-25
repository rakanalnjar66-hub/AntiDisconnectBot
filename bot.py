import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import discord
from discord.ext import commands
import datetime
import asyncio

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_health_check_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=run_health_check_server, daemon=True).start()

# إعدادات البوت الشاملة
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# الأيدي الخاص بك
MY_USER_ID = 1188601839751532660

@bot.event
async def on_ready():
    print(f'✅ بوت حماية عمار شغال وجاهز: {bot.user}')

@bot.event
async def on_voice_state_update(member, before, after):
    # إذا طلعت أنت من الروم
    if member.id == MY_USER_ID and before.channel is not None and after.channel is None:
        print("🚨 تم اكتشاف خروج عمار من الروم، جاري الفحص والتطبيق...")
        await asyncio.sleep(0.5)
        
        # يجيب أي شخص كان مع عمار بنفس الروم ويصكه ميوت ودِفن وديسكونكت فوراً
        for target in before.channel.members:
            if target.id != MY_USER_ID and not target.bot:
                try:
                    await target.edit(mute=True, deafen=True)
                    if target.voice and target.voice.channel:
                        await target.move_to(None)
                    print(f"🔥 تم جلد: {target.name}")
                except Exception as e:
                    print(f"❌ تعذر جلد {target.name}: {e}")

bot.run(os.environ.get('BOT_TOKEN'))
