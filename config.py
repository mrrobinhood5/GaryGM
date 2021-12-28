import os
from disnake import Intents

# discord CONSTANTS
BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_PREFIX = "."
TEST_GUILDS = [920857756146221096]
BOT_AUTHOR_ID = "623277032930803742"
INTENTS = Intents(
    guilds=True, members=True, messages=True, reactions=True,
    bans=False, emojis=False, integrations=False, webhooks=True, invites=False, voice_states=False, presences=False,
    typing=False)

# mongo CONSTANTS
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_URL = os.getenv("DB_URL")

# cogs
cogs = os.listdir("./cogs")
cogs.remove("__pycache__") if "__pycache__" in cogs else 0

# GAME CONSTANTS
APPROVAL_CHANNEL = 924062961222447126
NEW_PLAYER_ROLE = 921113949691334706
APPROVAL_REACTION = "👍"