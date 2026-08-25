import discord
from discord.ext import commands
import datetime
import asyncio

intents = discord.Intents.default()
intents.members = True
intents.voice_states = True
intents.moderation = True

bot = commands.Bot(command_prefix="!", intents=intents)

TIMEOUT_MINUTES = 10 

@bot.event
async def on_ready():
    print(f'✅ البوت شغال وجاهز باسم: {bot.user}')

@bot.event
async def on_voice_state_update(member, before, after):
    # الفحص: إذا كان الشخص في روم صوتي وفجأة طلع (صار None)
    if before.channel is not None and after.channel is None:
        try:
            # انتظار ثانية واحدة لضمان تسجيل الحدث في الـ Audit Log
            await asyncio.sleep(1)
            
            # البحث في الـ Audit Logs عن آخر عملية طرد صوتي
            async for entry in member.guild.audit_logs(limit=1, action=discord.AuditLogAction.member_disconnect):
                time_diff = datetime.datetime.now(datetime.timezone.utc) - entry.created_at
                
                # التأكد أن العملية حدثت لنفس الشخص وفي آخر 5 ثوانٍ
                if entry.target.id == member.id and time_diff.total_seconds() < 5:
                    executor = entry.user
                    
                    # تجنب إعطاء تايم أوت للبوت أو للشخص إذا طرد نفسه
                    if executor.id != member.id and not executor.bot:
                        duration = datetime.timedelta(minutes=TIMEOUT_MINUTES)
                        await executor.timeout(duration, reason="Anti-Disconnect System Triggered")
                        print(f"🚨 تم صك {executor.name} تايم أوت لأنه أعطى ديسكونكت لـ {member.name}")
                        break
        except Exception as e:
            print(f"خطأ أثناء فحص السجل: {e}")

# استبدل التوكن الجديد بالتوكن المولّد حديثاً من موقع ديسكورد
bot.run('MTU0MDc3ODY1MDIwMTM2MjQ1NA.GcpnYR.uesJr7u4sIWtJsT1-74FKLnO_LDQ0RAowb8Icc')