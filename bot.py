import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import discord
from discord.ext import commands
import datetime
import asyncio

# سيرفر لتأكيد حالة Live في Render
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")
        
    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

def run_health_check_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=run_health_check_server, daemon=True).start()

# --- إعدادات البوت ---
intents = discord.Intents.default()
intents.members = True
intents.voice_states = True
intents.moderation = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# الأيدي الخاص بك المحمي
MY_USER_ID = 1188601839751532660

@bot.event
async def on_ready():
    print(f'✅ نظام الحماية الشخصية شغال وجاهز باسم: {bot.user}')

@bot.event
async def on_voice_state_update(member, before, after):
    # الشرط الأول: الفحص يتفعل فقط إذا كان الشخص الذي خرج من الروم هو "أنت"
    if member.id == MY_USER_ID and before.channel is not None and after.channel is None:
        print("🚨 تم اكتشاف خروجك من الروم، جاري فحص مين اللي عطاك ديسكونكت...")
        await asyncio.sleep(1)
        
        try:
            async for entry in member.guild.audit_logs(limit=3, action=discord.AuditLogAction.member_disconnect):
                time_diff = datetime.datetime.now(datetime.timezone.utc) - entry.created_at
                
                # التأكد أن الهدف في السجل هو أنت وأن الطرد تم خلال آخر 8 ثوانٍ
                if entry.target and entry.target.id == MY_USER_ID and time_diff.total_seconds() < 8:
                    executor = entry.user
                    
                    # استثناء إذا طلعت بنفسك أو كان الفاعل بوت
                    if executor and executor.id != MY_USER_ID and not executor.bot:
                        guild_executor = member.guild.get_member(executor.id)
                        
                        if guild_executor:
                            try:
                                # 1. صك الفاعل ميوت ودِفن
                                await guild_executor.edit(mute=True, deafen=True, reason="Anti-Disconnect System (Protected User)")
                                
                                # 2. طرده من الروم الصوتي إذا كان متواجد داخل روم
                                if guild_executor.voice and guild_executor.voice.channel:
                                    await guild_executor.move_to(None)
                                    
                                print(f"🔥 تم الانتقام! صك {guild_executor.name} ميوت ودِفن وديسكونكت لأنه طردك!")
                            except discord.Forbidden:
                                print(f"❌ ما قدر يعاقبه: رتبة البوت أقل من رتبة {guild_executor.name}، ارفع رتبة البوت فوق رتبته!")
                        break
        except Exception as e:
            print(f"خطأ أثناء الفحص: {e}")

bot.run(os.environ.get('BOT_TOKEN'))
