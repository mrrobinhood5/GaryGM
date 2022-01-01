from disnake.ext.commands import option_enum
from disnake.ext import commands, tasks
from utils.characters import Player


class DatabaseActions(commands.Cog, name='Database Cache'):

    def __init__(self, bot):
        self.bot = bot
        self.db = self.bot.db
        self.character_cache.start()
        self.help_pages_cache.start()
        self.npc_cache.start()
        self.config_variables.start()

    @tasks.loop(hours=12)
    async def config_variables(self):
        self.bot.APPROVAL_CHANNEL = self.bot.guilds[0].get_channel(924062961222447126)
        self.bot.NEW_PLAYER_ROLE = self.bot.guilds[0].get_channel(921113949691334706)
        self.bot.DEFAULT_PC_AVATAR = 'https://i.imgur.com/v47ed3Y.jpg'

    @tasks.loop(seconds=60.0)
    async def character_cache(self):
        """ Runs every minute to maintain a cached list of valid prefixes for Player Characters
        and updates the bot attribute
        format for each cached character is:
        { 'player_id': { 'prefix': ('character', 'avatar', 'location_id')}}
        player_id is member.id as str
        prefix is str
        character is str
        avatar is url
        location_id is role.id as str
        """
        # send updates to DB first, then grab them again
        characters = []
        valid_prefixes = []
        prefixes_cache = {}
        async for character in self.db.players.find({"approved": True}):
            characters.append(Player(character))
        for character in characters:
            valid_prefixes.append(character.prefix)
            if prefixes_cache.get(character.player.id):
                prefixes_cache[character.player.id].update({character.prefix: character})
            else:
                prefixes_cache.update({character.player.id: {character.prefix: character}})
        self.bot.valid_prefixes = valid_prefixes
        self.bot.prefixes_cache = prefixes_cache
        self.bot.character_cache = characters

    @tasks.loop(seconds=600.0)
    async def help_pages_cache(self):
        """ Runs every 10 minutes to maintain a cached list of the help pages"""
        hp = []
        cursor = self.db.help.find()
        async for i in cursor:
            hp.append(i)
        self.bot.help_pages = hp
        self.bot.HelpPageEnum = option_enum([{x['title']: x['title'].lower()} for x in self.bot.help_pages][0])

    @tasks.loop(seconds=600.0)
    async def npc_cache(self):
        """ Runs every 10 minutes to maintained cached list of NPC prefixes """
        npc_cache = []
        cursor = self.db.npcs.find()
        async for i in cursor:
            npc_cache.append({i['prefix']})
        self.bot.npc_cache = npc_cache

    @config_variables.before_loop
    @npc_cache.before_loop
    @help_pages_cache.before_loop
    @character_cache.before_loop
    async def before_db(self):
        """ Keeps the task from running before the bot is ready """
        print('All task is waiting for Bot to go online...')
        await self.bot.wait_until_ready()
        print('DB Caches is now running...')

    def cog_unload(self):
        self.character_cache.cancel()
        self.help_pages_cache.cancel()
        self.npc_cache.cancel()
        self.config_variables.cancel()


def setup(bot):
    bot.add_cog(DatabaseActions(bot))
