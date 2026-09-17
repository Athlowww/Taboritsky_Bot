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
import logging
import asyncio

# --- ЗАГРУЗКА КОНФИГА ---
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

with open("dates.json", "r", encoding="utf-8") as f:
    holiday = json.load(f)

# --- ИНТЕНТЫ И БОТ ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="$", intents=intents, case_insensitive=True)

# --- КОНФИГ ---
clock = ["Часы уск"]
MSK = ZoneInfo("Europe/Moscow")
TEXT_CHANNEL_ID = 1538947385097592852
CHANNEL_ID = 1173116313514811422
LOG_CHANNEL_ID = 1548546961035100190
ERROR_CHANNEL_ID = 1548547027053318211
FFMPEG_PATH = r"E:\ffmpeg\bin\ffmpeg.exe"
VIDEO_URL = "https://www.youtube.com/watch?v=audMhJIcN08&list=RDaudMhJIcN08"

# --- ЛОГИРОВАНИЕ ---
logger = logging.getLogger("bot")
logger.setLevel(logging.DEBUG)


class DiscordHandler(logging.Handler):
    def __init__(self, channel_id: int):
        super().__init__()
        self.channel_id = channel_id

    async def send_to_discord(self, message: str):
        channel = bot.get_channel(self.channel_id)
        if channel:
            await channel.send(message)

    def emit(self, record):
        msg = self.format(record)
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(self.send_to_discord(msg))
            else:
                loop.run_until_complete(self.send_to_discord(msg))
        except Exception:
            self.handleError(record)


log_handler = DiscordHandler(LOG_CHANNEL_ID)
log_handler.setLevel(logging.INFO)

error_handler = DiscordHandler(ERROR_CHANNEL_ID)
error_handler.setLevel(logging.ERROR)

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
log_handler.setFormatter(formatter)
error_handler.setFormatter(formatter)

logger.addHandler(log_handler)
logger.addHandler(error_handler)

# --- ХЕЛПЕРЫ ДЛЯ ЛОГОВ ---
async def send_log(text: str):
    channel = bot.get_channel(LOG_CHANNEL_ID)
    if channel:
        await channel.send(text)


async def send_error(text: str):
    channel = bot.get_channel(ERROR_CHANNEL_ID)
    if channel:
        await channel.send(text)


# --- ФУНКЦИИ ---
def holiday_today():
    today = datetime.date.today()
    key = f"{today.day:02d}-{today.month:02d}"
    return holiday.get(key, [])


# --- ЗАДАЧИ ---
@tasks.loop(hours=24)
async def randomdmday():
    guild = list(bot.guilds)[0]  # или bot.get_guild(ID) если сервер один
    members = [m for m in guild.members if not m.bot]
    if not members:
        logger.warning("Нет участников для randomdmday")
        return

    member = secrets.choice(members)
    try:
        await member.send("Ты сын пакостной шалавы!")
        logger.info("ЛС отправлена: %s (%s)", member, member.id)
    except Exception as e:
        logger.error("Ошибка при отправке ЛС %s: %s", member, e)


@tasks.loop(hours=24)
async def check_holiday():
    events = holiday_today()
    if not events:
        return

    channel = bot.get_channel(1297188411458715668)
    if channel is None:
        logger.error("Канал для праздников не найден")
        return

    lines = []
    for e in events:
        name = e["название"]
        year = e["год"]
        desc = e["описание"]
        lines.append(f"**{name}** ({year})\n{desc}")

    text = "Сегодня великий праздник!\n\n" + "\n\n".join(lines)
    try:
        await channel.send(text)
        logger.info("Праздник отправлен в канал %s", channel.id)
    except Exception as e:
        logger.error("Ошибка при отправке праздника: %s", e)



# --- СОБЫТИЯ ---
@bot.event
async def on_ready():
    logger.info("Бот запущен: %s", bot.user)
    print(f"TIK TAK MOTHERFUCKER: {bot.user}")
    if not randomdmday.is_running():
        randomdmday.start()
    if not check_holiday.is_running():
        check_holiday.start()


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.content.lower().startswith("$повтори "):
        text = message.content[8:]
        await message.channel.send(text)
    await bot.process_commands(message)


@bot.event
async def on_command_error(ctx, error):
    logger.error("Ошибка в команде %s: %s", ctx.command, error)


# --- КОМАНДЫ ---
@bot.command()
async def привет(ctx):
    await ctx.send(f"Доброе утро {ctx.author.mention}")
    logger.info("Команда 'привет' вызвана пользователем %s", ctx.author)


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
        except Exception as e:
            logger.error("Не удалось замутить %s: %s", member, e)

    def after_play(error):
        async def _unmute_and_disconnect():
            for member in muted_members:
                try:
                    await member.edit(mute=False)
                except Exception as e:
                    logger.error("Не удалось размутить %s: %s", member, e)
            await voice_client.disconnect()

        bot.loop.create_task(_unmute_and_disconnect())

    voice_client.play(discord.FFmpegPCMAudio("sound.mp3"), after=after_play)
    logger.info("Команда 'tiktak' вызвана пользователем %s в канале %s", ctx.author, channel)


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
            victim = secrets.choice(candidates)
            await victim.move_to(None)

            text_channel = bot.get_channel(TEXT_CHANNEL_ID)
            if text_channel is None:
                text_channel = await bot.fetch_channel(TEXT_CHANNEL_ID)

            await text_channel.send(f"{victim.mention} БЫЛ ИЗГНАН ПО ВОЛЕ ВЕЛИКОГО РЕГЕНТА ТАБОРИЦКОГО")
            logger.info("Пользователь %s изгнан командой 'tribunal'", victim)

            await voice_client.disconnect()

        bot.loop.create_task(_kick_and_disconnect())

    await voice_client.play(discord.FFmpegPCMAudio("tribunal_sound.mp3"), after=kicker)
    logger.info("Команда 'tribunal' вызвана пользователем %s в канале %s", ctx.author, voice_channel)


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
    logger.info("Пользователь %s замьючен на %s %s пользователем %s", member, amount, unit, ctx.author)


@bot.command()
@commands.has_any_role(1196096320029597817, 1460955546814517462, 1534528542539517982)
async def unmute(ctx, member: discord.Member):
    await member.timeout(None)
    logger.info("Пользователь %s размьючен пользователем %s", member, ctx.author)


@bot.command()
@commands.has_any_role(1196096320029597817, 1460955546814517462, 1534528542539517982)
async def holokost(ctx):
    member = 722795402465771521
    await member.ban()
    logger.warning("Пользователь с ID 722795402465771521 забанен командой 'holokost'")


@bot.command()
async def izmena(ctx, member: discord.Member):
    yes_or_no = random.randint(1, 2)
    if yes_or_no == 1:
        await ctx.send(f"{ctx.author.mention} Регент решил, что вы пытаетесь его оклеветать, вечером вас отъебут в жопу")
    else:
        await ctx.send(f"{member.mention} Вы изменяете серверу, вечером вас отъебут в жопу")
    logger.info("Команда 'izmena' вызвана пользователем %s для %s", ctx.author, member)


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
    logger.info("Команда 'helpme' вызвана пользователем %s", ctx.author)


@bot.command()
async def govno(ctx):
    await ctx.send("https://www.youtube.com/shorts/RRBA2hFtgpQ")


@bot.command()
async def randomdm(ctx, *, text: str = "Ты сын пакостной шалавы!"):
    guild = ctx.guild
    members = [m for m in guild.members if not m.bot]
    if not members:
        await ctx.send("Нет участников.")
        return

    member = secrets.choice(members)
    try:
        await member.send(f"{member.mention}, я твою мертвую мать ногами топтал")
        logger.info("randomdm: ЛС отправлена %s", member)
    except discord.Forbidden:
        logger.warning("randomdm: ЛС закрыты у %s", member)
        await ctx.send("У пользователя закрыты ЛС.")


# --- ЗАПУСК ---
bot.run(TOKEN)