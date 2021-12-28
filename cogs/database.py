
from disnake.ext import commands, tasks


class DatabaseActions(commands.Cog, name='Database Cache'):

    def __init__(self, bot):
        self.bot = bot
        self.db = self.bot.db
        self.db_cache.start()

    @tasks.loop(seconds=60.0)
    async def db_cache(self):
        valid_prefixes = {}
        async for i in self.db.players.find({"approved": True}):
            if i['player'] in valid_prefixes.keys():
                valid_prefixes[i['player']].update({i['prefix']: (i['character'], i['avatar'], i['location'])})
            else:
                valid_prefixes.update({i['player']: {i['prefix']: (i['character'], i['avatar'], i['location'])}})
        self.bot.pc_prefixes = valid_prefixes

    @db_cache.before_loop
    async def before_db(self):
        print('DB Cache task is waiting for Bot to go online...')
        await self.bot.wait_until_ready()
        print('DB Caches is now running...')

    def cog_unload(self):
        self.db_cache.cancel()


def setup(bot):
    bot.add_cog(DatabaseActions(bot))
