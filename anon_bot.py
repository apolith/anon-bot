import discord
from discord.ext import commands
from discord import app_commands
import os
from datetime import datetime

# ──────────────────────────────────────────────
#  НАСТРОЙКИ — измени эти значения
# ──────────────────────────────────────────────
BOT_TOKEN = "BOT_TOKEN"
ANON_CHANNEL_ID = int(os.getenv("ANON_CHANNEL_ID"))
# ──────────────────────────────────────────────

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ Бот запущен как {bot.user}")
    print(f"📢 Анонимный канал: {ANON_CHANNEL_ID}")


# ── Слэш-команда /anon ──────────────────────────────────────────────────────
@bot.tree.command(name="anon", description="Отправить анонимное сообщение в публичный канал")
@app_commands.describe(message="Твоё анонимное сообщение")
async def anon(interaction: discord.Interaction, message: str):
    """
    Пользователь вызывает /anon <текст> в личке или любом канале.
    Бот публикует сообщение в ANON_CHANNEL_ID без имени автора.
    """

    # Базовая фильтрация: не пускаем пустые / слишком длинные сообщения
    message = message.strip()
    if not message:
        await interaction.response.send_message("❌ Сообщение не может быть пустым.", ephemeral=True)
        return
    if len(message) > 2000:
        await interaction.response.send_message("❌ Сообщение слишком длинное (максимум 2000 символов).", ephemeral=True)
        return

    anon_channel = bot.get_channel(ANON_CHANNEL_ID)
    if anon_channel is None:
        await interaction.response.send_message("❌ Канал не найден. Проверь ANON_CHANNEL_ID.", ephemeral=True)
        return

    # Красивый embed без любого упоминания автора
    embed = discord.Embed(
        description=message,
        color=discord.Color.blurple(),
        timestamp=datetime.utcnow(),
    )
    embed.set_author(name="🎭 Анонимное сообщение")
    embed.set_footer(text="Отправь своё — /anon <сообщение>")

    await anon_channel.send(embed=embed)

    # Отвечаем только отправителю (ephemeral = видит только он)
    await interaction.response.send_message("✅ Твоё сообщение анонимно опубликовано!", ephemeral=True)


# ── Префиксная команда !anon (запасной вариант) ────────────────────────────
@bot.command(name="anon")
async def anon_prefix(ctx: commands.Context, *, message: str = ""):
    """
    !anon <текст>
    Работает в личке (DM) или в любом канале сервера.
    """
    # Удаляем сообщение пользователя, чтобы не светить его имя
    try:
        await ctx.message.delete()
    except discord.Forbidden:
        pass  # нет прав на удаление — ничего страшного

    message = message.strip()
    if not message:
        await ctx.send("❌ Укажи текст: `!anon твоё сообщение`", delete_after=5)
        return
    if len(message) > 2000:
        await ctx.send("❌ Сообщение слишком длинное.", delete_after=5)
        return

    anon_channel = bot.get_channel(ANON_CHANNEL_ID)
    if anon_channel is None:
        await ctx.send("❌ Канал не найден.", delete_after=5)
        return

    embed = discord.Embed(
        description=message,
        color=discord.Color.blurple(),
        timestamp=datetime.utcnow(),
    )
    embed.set_author(name="🎭 Анонимное сообщение")
    embed.set_footer(text="Отправь своё — /anon <сообщение> или !anon <сообщение>")

    await anon_channel.send(embed=embed)

    # Уведомляем отправителя в личку
    try:
        await ctx.author.send("✅ Твоё сообщение анонимно опубликовано!")
    except discord.Forbidden:
        pass  # личка закрыта


# ── Запуск ──────────────────────────────────────────────────────────────────
bot.run(BOT_TOKEN)
