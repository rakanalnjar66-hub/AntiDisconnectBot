import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import discord
from discord.ext import commands
import datetime
import asyncio

# سيرفر تأكيد حالة Live في Render
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

# الأيدي الخاص بك (معفي من العقاب)
MY_USER_ID = 1188601839751532660

@bot.event
async def on_ready():
    print(f'✅ البوت شغال وجاهز باسم: {bot.user}')

@bot.event
async def on_voice_state_update(member, before, after):
    # خروج عضو من روم صوتي
    if before.channel is not None and after.channel is None:
        try:
            await asyncio.sleep(1.5)
            
            async for entry in member.guild.audit_logs(limit=5, action=discord.AuditLogAction.member_disconnect):
                time_diff = datetime.datetime.now(datetime.timezone.utc) - entry.created_at
                
                # فحص الحدث خلال آخر 10 ثوانٍ
                if entry.target and entry.target.id == member.id and time_diff.total_seconds() < 10:
                    executor = entry.user
                    
                    # استثناء البوت، الشخص الذي طرد نفسه، وأنت صاحب الأيدي المكتوب
                    if executor and executor.id != member.id and executor.id != MY_USER_ID and not executor.bot:
                        guild_executor = member.guild.get_member(executor.id)
                        
                        if guild_executor:
                            # 1. إعطاء ميوت ودِفن
                            await guild_executor.edit(
                                mute=True, 
                                deafen=True, 
                                reason="Anti-Disconnect Triggered"
                            )
                            
                            # 2. طرده من الروم الصوتي إذا كان متواجد
                            if guild_executor.voice and guild_executor.voice.channel:
                                await guild_executor.move_to(None)
                                
                            print(f"🚨 تم صك الفاعل ({guild_executor.name} - ID: {guild_executor.id}) ميوت ودِفن وديسكونكت!")
                        break
        except Exception as e:
            print(f"خطأ أثناء الفحص: {e}")

bot.run(os.environ.get('BOT_TOKEN'))
