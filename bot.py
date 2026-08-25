import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import discord
from discord.ext import commands
import datetime
import asyncio

# سيرفر وهمي لتأكيد حالة Live في Render
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

# --- إعدادات البوت والصلاحيات ---
intents = discord.Intents.default()
intents.members = True
intents.voice_states = True
intents.moderation = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'✅ البوت شغال وجاهز باسم: {bot.user}')

@bot.event
async def on_voice_state_update(member, before, after):
    # الفحص: إذا خرج شخص من الروم الصوتي
    if before.channel is not None and after.channel is None:
        try:
            await asyncio.sleep(1)
            async for entry in member.guild.audit_logs(limit=1, action=discord.AuditLogAction.member_disconnect):
                time_diff = datetime.datetime.now(datetime.timezone.utc) - entry.created_at
                
                # التأكد أن عملية الطرد حدثت للشخص في آخر 5 ثوانٍ
                if entry.target.id == member.id and time_diff.total_seconds() < 5:
                    executor = entry.user
                    
                    if executor.id != member.id and not executor.bot:
                        # 1. إعطاء ميوت ودِفن وطرد من الروم الصوتي إذا كان الفاعل في روم صوتي
                        if executor.voice and executor.voice.channel:
                            await executor.edit(
                                mute=True, 
                                deafen=True, 
                                voice_channel=None, 
                                reason="Anti-Disconnect System Triggered"
                            )
                        else:
                            # 2. إذا كان الفاعل خارج الروم الصوتي، يتم تطبيق الميوت والدفن فقط لحين دخوله
                            await executor.edit(
                                mute=True, 
                                deafen=True, 
                                reason="Anti-Disconnect System Triggered"
                            )
                            
                        print(f"🚨 تم إعطاء ميوت ودِفن وديسكونكت لـ {executor.name} لأنه طرد {member.name}")
                        break
        except Exception as e:
            print(f"خطأ أثناء التعديل: {e}")

bot.run(os.environ.get('BOT_TOKEN'))
