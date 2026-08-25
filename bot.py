import os
import asyncio
import datetime
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.members = True
intents.voice_states = True
intents.moderation = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

TIMEOUT_MINUTES = 10

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
                        duration = datetime.timedelta(minutes=TIMEOUT_MINUTES)
                        await executor.timeout(duration, reason="Anti-Disconnect System Triggered")
                        print(f"🚨 تم صك {executor.name} تايم أوت لأنه أعطى ديسكونكت لـ {member.name}")
                        break
        except Exception as e:
            print(f"خطأ أثناء فحص السجل: {e}")

bot.run(os.environ.get('BOT_TOKEN'))
