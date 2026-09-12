import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
from datetime import time
import datetime
import secrets
from zoneinfo import ZoneInfo
import random
import os
import json

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
FFMPEG_PATH = r"E:\ffmpeg\bin\ffmpeg.exe"
with open("dates.json", "r", encoding="utf-8") as f:
    holiday = json.load(f)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="$", intents=intents, case_insensitive=True)

clock = ["Часы уск"]
TEXT_CHANNEL_ID = 1538947385097592852
CHANNEL_ID = 1173116313514811422
VIDEO_URL = "https://www.youtube.com/watch?v=audMhJIcN08&list=RDaudMhJIcN08"
MSK = ZoneInfo("Europe/Moscow")

def holiday_today() -> str | None:
    today = datetime.date.today()
    key = f"{today.day:02d}-{today.month:02d}"
    return holiday.get(key, [])




@tasks.loop(hours=24)
async def randomdmday(ctx, *, text: str = "Ты сын пакостной шалавы!"):
    guild = ctx.guild
    members = [m for m in guild.members if not m.bot and not m.bot]
    member = secrets.choice(members)
    try:
        await member.send(text)
        await ctx.send(f"{member.mention}, я твою мертвую мать ногами топтал")
    except discord.Forbidden:
        return



@tasks.loop(hours=24)
async def check_holiday(ctx):
    events = holiday_today()
    if not events:
        return

    channel = bot.get_channel(1297188411458715668)
    if channel is None:
        return

    lines = []
    for e in events:
        name = e["название"]
        year = e["год"]
        desc = e["описание"]
        lines.append(f"**{name}** ({year})\n{desc}")

    text = "Сегодня великий праздник!\n\n" + "\n\n".join(lines)
    await channel.send(text)

@bot.event
async def on_ready():
    print(f"TIK TAK MOTHERFUCKER: {bot.user}")
    if not daily_video.is_running():
        daily_video.start()

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.content.lower().startswith("$повтори "):
        text = message.content[8:]
        await message.channel.send(text)
    await bot.process_commands(message)


@bot.command()
async def привет(ctx):
    await ctx.send(f"Доброе утро {ctx.author.mention}")


@tasks.loop(time=time(hour=0, minute=0, tzinfo=MSK))
async def daily_video():
    channel = bot.get_channel(CHANNEL_ID)
    if channel is None:
        channel = await bot.fetch_channel(CHANNEL_ID)

    await channel.send(f"@everyone {VIDEO_URL}")


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



@bot.command()
@commands.has_any_role(1196096320029597817, 1460955546814517462, 1534528542539517982)
async def holokost(ctx):
    member = 722795402465771521
    await member.ban()

@bot.command()
async def izmena(ctx, member: discord.Member):
    yes_or_no = random.randint(1, 2)
    if yes_or_no == 1:
        await ctx.send(f"{ctx.author.mention}Регент решил, что вы пытаетесь его оклеветать, вечером вас отъебут в жопу")
    else:
        await ctx.send(f"{member.mention}Вы изменяете серверу, вечером вас отъебут в жопу")

@bot.command()
async def helpme(ctx):
    embed = discord.Embed(
        title="Список доступных команд для простых смертных:",
        color=discord.Color.dark_red()
    )
    embed.add_field(name="привет", value="Приветствует пользователя, вызвавшего команду")
    embed.add_field(name="повтори", value="Повторяет фразу пользователя")
    embed.add_field(name="izmena", value="Пытается обвинить пользователя в измене")

    await ctx.send(embed=embed)


@bot.command()
async def govno(ctx):
    await ctx.send("https://www.youtube.com/shorts/RRBA2hFtgpQ")

@bot.command()
async def randomdm(ctx, *, text: str = "Ты сын пакостной шалавы!"):
    guild = ctx.guild
    members = [m for m in guild.members if not m.bot and not m.bot]
    member = secrets.choice(members)
    try:
        await member.send(f"{member.mention}, я твою мертвую мать ногами топтал")
    except discord.Forbidden:
        return


bot.run(TOKEN)