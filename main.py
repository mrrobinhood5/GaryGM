from __future__ import annotations
from disnake.ext.commands import Bot
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from disnake.ext import commands
from disnake import Game, Status
from config import *

## instance of the bot
bot: Bot = commands.Bot(command_prefix=BOT_PREFIX, intents=INTENTS, test_guilds=TEST_GUILDS)

# instance of the database
client = AsyncIOMotorClient(
    f"mongodb+srv://{DB_USER}:{DB_PASSWORD}@{DB_URL}")

bot.db: AsyncIOMotorDatabase = client.Kerna

bot.players = []
bot.get_player = lambda x: [p for p in bot.players if x.lower() in p.member.name.lower()][0]
bot.pending_approvals = []
bot.character_delete_queue = []
bot.shared_npcs = []

# custom instance of bot
# bot = KernaBot(db, BOT_PREFIX, INTENTS, TEST_GUILDS)

# bot output
@bot.event
async def on_ready():
    print(f'I\'m in as {bot.user} with a "{bot.command_prefix}" prefix')

    activity = Game("D&D 5e | /help for server rules")
    await bot.change_presence(status=Status.online, activity=activity)

# load jishaku
bot.load_extension('jishaku')

# loads the cogs
for cog in cogs:
    bot.load_extension(f'cogs.{cog[:-3]}')

# runs the client
bot.run(BOT_TOKEN)
