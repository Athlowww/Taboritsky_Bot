import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
from datetime import time
import datetime
from zoneinfo import ZoneInfo
import random
import os

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
FFMPEG_PATH = r"E:\ffmpeg\bin\ffmpeg.exe"

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="$", intents=intents, case_insensitive=True)

clock = ["Часы уск"]
TEXT_CHANNEL_ID = 1538947385097592852
CHANNEL_ID = 1173116313514811422
VIDEO_URL = "https://www.youtube.com/watch?v=audMhJIcN08&list=RDaudMhJIcN08"
MSK = ZoneInfo("Europe/Moscow")



@bot.event
async def on_ready():
    print(f"TIK TAK MOTHERFUCKER: {bot.user}")
    if not daily_video.is_running():
        daily_video.start()


@bot.command()
async def привет(ctx):
    await ctx.send(f"Доброе утро {ctx.author.mention}")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.content.lower().startswith("$повтори "):
        text = message.content[8:]
        await message.channel.send(text)
    await bot.process_commands(message)


@tasks.loop(time=time(hour=0, minute=0, tzinfo=MSK))
async def daily_video():
    channel = bot.get_channel(CHANNEL_ID)
    if channel is None:
        channel = await bot.fetch_channel(CHANNEL_ID)

    await channel.send(VIDEO_URL)


@bot.command()
@commands.has_any_role(1196096320029597817, 1460955546814517462, 1534528542539517982)
async def tiktak(ctx):
    if ctx.author.voice is None:
        await ctx.send("Ты не в войсе.")
        return

    channel = ctx.author.voice.channel
    voice_client = await channel.connect()

    muted_members = []
    for member in channel.members:
        if member.bot:
            continue
        try:
            await member.edit(mute=True)
            muted_members.append(member)
        except:
            pass

    def after_play(error):
        async def _unmute_and_disconnect():
            for member in muted_members:
                try:
                    await member.edit(mute=False)
                except:
                    pass
            await voice_client.disconnect()

        bot.loop.create_task(_unmute_and_disconnect())


    voice_client.play(discord.FFmpegPCMAudio("sound.mp3"), after=after_play)


@bot.command()
@commands.has_any_role(1196096320029597817, 1460955546814517462, 1534528542539517982)
async def tribunal(ctx):
    if ctx.author.voice is None:
        await ctx.send("Ты не в войсе.")
        return

    voice_channel = ctx.author.voice.channel
    voice_client = await voice_channel.connect()

    candidates = [m for m in voice_channel.members if not m.bot]
    if not candidates:
        await ctx.send("В войсе нет людей для изгнания")
        await voice_client.disconnect()
        return

    def kicker(error):
        async def _kick_and_disconnect():
            victim = random.choice(candidates)
            await victim.move_to(None)

            text_channel = bot.get_channel(TEXT_CHANNEL_ID)
            if text_channel is None:
                text_channel = await bot.fetch_channel(TEXT_CHANNEL_ID)

            await text_channel.send(f"{victim.mention} БЫЛ ИЗГНАН ПО ВОЛЕ ВЕЛИКОГО РЕГЕНТА ТАБОРИЦКОГО")

            await voice_client.disconnect()

        bot.loop.create_task(_kick_and_disconnect())

    await voice_client.play(discord.FFmpegPCMAudio("tribunal_sound.mp3"), after=kicker)

@bot.command()
@commands.has_any_role(1196096320029597817, 1460955546814517462, 1534528542539517982)
async def mute(ctx, member: discord.Member, amount: int, unit: str):
    if unit == "m":
        duration = datetime.timedelta(minutes=amount)
    elif unit == "h":
        duration = datetime.timedelta(hours=amount)
    elif unit == "d":
        duration = datetime.timedelta(days=amount)
    else:
        await ctx.send("Используй m, h или d.")
        return

    await member.timeout(duration, reason="Таборицкий решил лишить вас права голоса")

@bot.command()
@commands.has_any_role(1196096320029597817, 1460955546814517462, 1534528542539517982)
async def unmute(ctx, member: discord.Member):
    await member.timeout(None)



bot.run(TOKEN)