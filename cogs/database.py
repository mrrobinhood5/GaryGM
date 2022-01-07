from disnake.ext.commands import option_enum
from disnake.ext import commands, tasks
from bson.objectid import ObjectId
from utils.kerna_classes import Player, Character, Approval


class DatabaseActions(commands.Cog, name='Database Cache'):
    """ Database cache should only pull once when the bot is started, and push every 5 minutes maybe """

    def __init__(self, bot):
        self.bot = bot
        self.db = self.bot.db
        self.initial_db_cache_load.start()
        self.db_data_dump.start()
        self.help_pages_cache.start()
        self.npc_cache.start()
        self.config_variables.start()

    @tasks.loop(minutes=1)
    async def db_data_dump(self):
        # process the delete_queue
        for character in self.bot.character_delete_queue:
            await self.db.characters.delete_one(character.f)
        self.bot.character_delete_queue = []

        # players and characters
        for player in self.bot.players:
            self.bot.db.players.update_one(player.f, {'$set': player.to_dict}, upsert=True)
            for character in player.characters:
                self.bot.db.characters.update_one(character.f, {'$set': character.to_dict}, upsert=True)

    @tasks.loop(hours=12)
    async def config_variables(self):
        self.bot.APPROVAL_CHANNEL = self.bot.guilds[0].get_channel(924062961222447126)
        self.bot.NEW_PLAYER_ROLE = self.bot.guilds[0].get_role(921113949691334706)
        self.bot.DEFAULT_PC_AVATAR = 'https://i.imgur.com/v47ed3Y.jpg'

    @tasks.loop(seconds=2, count=1)
    async def initial_db_cache_load(self):
        """ Will run once and cache the whole db on the bot instance
        """
        # Load the players first, and its characters
        async for player in self.db.players.find():
            m = self.bot.guilds[0].get_member(int(player['member']))
            c = []
            async for character in self.db.characters.find({"player": str(m.id)}):
                c.append(Character(
                    _id=character["_id"],
                    player=m,
                    name=character['name'],
                    backstory=character['backstory'],
                    avatar=character['avatar'],
                    prefix=character['prefix'],
                    location=self.bot.guilds[0].get_role(int(character['location'])),
                    variants=character['variants'],
                    familiars=character['familiars'], # load these objects
                    approved=character['approved'], # load these objects
                    alive=character['alive'],
                    keys=character['keys'], # this needs to be expanded to roles
                    rpxp=character['rpxp']
                ))
            self.bot.players.append(Player(_id=player["_id"], member=m, characters=c))

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
    @initial_db_cache_load.before_loop
    @db_data_dump.before_loop
    async def before_db(self):
        """ Keeps the task from running before the bot is ready """
        print('All task is waiting for Bot to go online...')
        await self.bot.wait_until_ready()
        print('DB Caches is now running...')

    def cog_unload(self):
        self.initial_db_cache_load.cancel()
        self.help_pages_cache.cancel()
        self.npc_cache.cancel()
        self.config_variables.cancel()
        self.db_data_dump.cancel()


def setup(bot):
    bot.add_cog(DatabaseActions(bot))
