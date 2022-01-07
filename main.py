import disnake
import motor.motor_asyncio
from disnake.ext import commands
from config import *

## instance of the bot
bot = commands.Bot(command_prefix=BOT_PREFIX,
                   intents=INTENTS,
                   test_guilds=TEST_GUILDS)

# instance of the database
db = motor.motor_asyncio.AsyncIOMotorClient(
    f"mongodb+srv://{DB_USER}:{DB_PASSWORD}@{DB_URL}")
bot.__setattr__("db", db.Kerna)
bot.__setattr__("players", [])
bot.__setattr__("pending_approvals", [])
bot.__setattr__("character_delete_queue", [])

# custom instance of bot
# bot = KernaBot(db, BOT_PREFIX, INTENTS, TEST_GUILDS)

# bot output
@bot.event
async def on_ready():
    print(f'I\'m in as {bot.user} with a "{bot.command_prefix}" prefix')
    activity = disnake.Game("D&D 5e | /help for server rules")
    await bot.change_presence(status=disnake.Status.online, activity=activity)

# load jishaku
bot.load_extension('jishaku')

# loads the cogs
for cog in cogs:
    bot.load_extension(f'cogs.{cog[:-3]}')

# runs the client
bot.run(BOT_TOKEN)
