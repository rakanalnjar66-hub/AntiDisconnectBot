import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import discord
from discord.ext import commands
import datetime
import asyncio

# --- سيرفر فحص الصحة (يدعم GET و HEAD لإرضاء UptimeRobot) ---
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()

def run_health_check_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=run_health_check_server, daemon=True).start()

# --- إعدادات البوت والـ Intents ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# الأيدي الخاص بك
MY_USER_ID = 1188601839751532660

@bot.event
async def on_ready():
    print(f'✅ بوت حماية عمار شغال المطور: {bot.user}')

@bot.event
async def on_voice_state_update(member, before, after):
    # الفحص عند خروجك أنت فقط من الروم
    if member.id == MY_USER_ID and before.channel is not None and after.channel is None:
        await asyncio.sleep(0.5)
        punished = False

        # 1. محاولة صك الفاعل الحقيقي فقط من السجل
        try:
            async for entry in before.guild.audit_logs(limit=3, action=discord.AuditLogAction.member_disconnect):
                time_diff = datetime.datetime.now(datetime.timezone.utc) - entry.created_at
                
                if entry.target and entry.target.id == MY_USER_ID and time_diff.total_seconds() < 8:
                    executor = entry.user
                    # استثناء نفسك وأي بوتات أخرى من العقاب
                    if executor and executor.id != MY_USER_ID and not executor.bot:
                        target_mem = before.guild.get_member(executor.id)
                        if target_mem:
                            await target_mem.edit(mute=True, deafen=True)
                            if target_mem.voice and target_mem.voice.channel:
                                await target_mem.move_to(None)
                            print(f"🔥 تم جلد الفاعل الحقيقي فقط: {target_mem.name}")
                            punished = True
                        break
        except Exception as e:
            print(f"خطأ سجل: {e}")

        # 2. في حال لم يُعرف الفاعل، يعاقب الأعضاء فقط ويستثني البوتات تماماً (مثل بوت القرآن)
        if not punished:
            for target in before.channel.members:
                if target.id != MY_USER_ID and not target.bot:
                    try:
                        await target.edit(mute=True, deafen=True)
                        if target.voice and target.voice.channel:
                            await target.move_to(None)
                        print(f"🔥 تم جلد العضو: {target.name}")
                    except Exception as e:
                        print(f"❌ تعذر جلد {target.name}: {e}")

# تشغيل البوت باستخدام الـ Token
bot.run(os.environ.get('BOT_TOKEN'))
