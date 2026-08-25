import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import discord
from discord.ext import commands
import datetime
import asyncio

# سيرفر تأكيد حالة Live لـ Render
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

@bot.event
async def on_ready():
    print(f'✅ البوت شغال وجاهز باسم: {bot.user}')

@bot.event
async def on_voice_state_update(member, before, after):
    if before.channel is not None and after.channel is None:
        try:
            await asyncio.sleep(1)
            async for entry in member.guild.audit_logs(limit=1, action=discord.AuditLogAction.member_disconnect):
                time_diff = datetime.datetime.now(datetime.timezone.utc) - entry.created_at
                
                if entry.target.id == member.id and time_diff.total_seconds() < 5:
                    executor = entry.user
                    
                    if executor.id != member.id and not executor.bot:
                        # جلب العضو كـ Member لتطبيق الإجراءات
                        guild_executor = member.guild.get_member(executor.id)
                        if guild_executor:
                            if guild_executor.voice and guild_executor.voice.channel:
                                await guild_executor.edit(
                                    mute=True, 
                                    deafen=True, 
                                    voice_channel=None, 
                                    reason="Anti-Disconnect Triggered"
                                )
                            else:
                                await guild_executor.edit(
                                    mute=True, 
                                    deafen=True, 
                                    reason="Anti-Disconnect Triggered"
                                )
                            print(f"🚨 تم صك ميوت ودِفن وديسكونكت لـ {guild_executor.name}")
                        break
        except Exception as e:
            print(f"خطأ: {e}")

bot.run(os.environ.get('BOT_TOKEN'))
