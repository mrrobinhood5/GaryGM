from __future__ import annotations
from disnake.ext.commands import option_enum, Bot
from disnake.ext import commands, tasks
from motor.motor_asyncio import AsyncIOMotorDatabase
from utils.player import Player
from utils.npc import Npc
from utils.characters import Character, CharacterFamiliar, CharacterVariant


class DatabaseActions(commands.Cog, name='Database Cache'):
    """ Database cache should only pull once when the bot is started, and push every 5 minutes maybe """

    def __init__(self, bot) -> None:
        self.bot: Bot = bot
        self.db: AsyncIOMotorDatabase = self.bot.db
        self.initial_db_cache_load.start()
        self.db_data_dump.start()
        self.help_pages_cache.start()
        self.npc_cache.start()
        self.config_variables.start()

    @tasks.loop(seconds=2, count=1)
    async def initial_db_cache_load(self):
        """ Will run once and cache the whole db on the bot instance """
        # Load members the bot can see
        all_members = self.bot.get_all_members()
        # go through them all and match them with the database
        for member in all_members:
            # loads any player matching the member id initializes an empty player if a match is found
            db_player = await self.db.players.find_one({"member": member.id})
            if db_player:
                player = Player(_id=db_player["_id"], member=member)

                # fetches all db characters with matching player id, and iterates over them if any are found
                db_characters = self.db.characters.find({"player": db_player["_id"]})
                if db_characters:
                    # goes through each character and initializes it. leaves variants and familiars empty
                    async for c in db_characters:
                        keys = [member.guild.get_role(k) for k in c['keys']] if c['keys'] else []
                        character = Character(_id=c['_id'],
                                              player=player,
                                              name=c['name'],
                                              backstory=c['backstory'],
                                              avatar=c['avatar'],
                                              prefix=c['prefix'],
                                              location=member.guild.get_role(c['location']),
                                              approved=c['approved'],
                                              alive=c['alive'],
                                              keys=keys,
                                              rpxp=c['rpxp']
                                              )
                        if c['variants']:
                            db_variants = self.db.variants.find({"character": c['_id']})
                            async for v in db_variants:
                                variant = CharacterVariant(
                                    _id=v['_id'],
                                    character=character,
                                    name=v['name'],
                                    prefix=v['prefix'],
                                    avatar=v['avatar'],
                                    rpxp=v['rpxp'])
                                character.add_variant(variant)
                        if c['familiars']:
                            db_familiars = self.db.familiars.find({"character": c['_id']})
                            async for f in db_familiars:
                                familiar = CharacterFamiliar(
                                    _id=f['_id'],
                                    character=character,
                                    name=f['name'],
                                    prefix=f['prefix'],
                                    avatar=f['avatar'],
                                    rpxp=f['rpxp'])
                                character.add_familiar(familiar)
                        player.add_character(character)

                db_npcs = self.db.npcs.find({"owner": db_player["_id"]})
                if db_npcs:
                    async for n in db_npcs:
                        npc = Npc(owner=player,
                                  description=n['description'],
                                  avatar=n['avatar'],
                                  name=n['name'],
                                  shared=n['shared'],
                                  prefix=n['prefix'],
                                  _id=n['_id'],
                                  rpxp=n['rpxp'])
                        player.add_npc(npc)
                        self.bot.shared_npcs.append(npc) if n['shared'] else 0
                self.bot.players.append(player)

        #
        #
        # async for db_player in self.db.players.find():
        #     # this should be the only member
        #     member = self.bot.guilds[0].get_member(int(db_player['member']))
        #     current_player = Player(_id=db_player["_id"], member=member)
        #     current_characters = []
        #
        #     for db_character in db_player['characters']:  # gets all the character IDs from db_player
        #         char = await self.db.characters.find_one({"_id": db_character})
        #         temp_char = None
        #         if char:
        #             temp_char = Character(
        #                 _id=char["_id"],
        #                 player=current_player,
        #                 name=char['name'],
        #                 backstory=char['backstory'],
        #                 avatar=char['avatar'],
        #                 prefix=char['prefix'],
        #                 location=self.bot.guilds[0].get_role(int(char['location'])),
        #                 variants=[],
        #                 familiars=[],
        #                 approved=char['approved'],  # load these objects
        #                 alive=char['alive'],
        #                 keys=[self.bot.guilds[0].get_role(int(key)) for key in char['keys']],
        #                 rpxp=char['rpxp']
        #             )
        #             for db_familiar in char['familiars']:  # gets all the familiar IDs from db_char
        #                 familiar = await self.db.familiars.find_one({"_id": db_familiar})
        #                 if familiar:
        #                     temp_familiar = CharacterFamiliar(
        #                         character=temp_char,
        #                         name=familiar['name'],
        #                         prefix=familiar['prefix'],
        #                         avatar=familiar['avatar'],
        #                         _id=familiar['_id']
        #                     )
        #                     temp_char.add_familiar(temp_familiar)
        #             for db_variant in char['variants']:  # gets all the familiar IDs from db_char
        #                 variant = await self.db.variants.find_one({"_id": db_variant})
        #                 if variant:
        #                     temp_variant = CharacterVariant(
        #                         character=temp_char,
        #                         name=variant['name'],
        #                         prefix=variant['prefix'],
        #                         avatar=variant['avatar'],
        #                         _id=variant['_id']
        #                     )
        #                     temp_char.add_variant(temp_variant)
        #         current_characters.append(temp_char)
        #     current_player.characters = current_characters
        #     self.bot.players.append(current_player)

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
                if character.familiars:
                    for familiar in character.familiars:
                        self.bot.db.familiars.update_one(familiar.f, {'$set': familiar.to_dict}, upsert=True)
                if character.variants:
                    for variant in character.variants:
                        self.bot.db.variants.update_one(variant.f, {'$set': variant.to_dict}, upsert=True)
            for npc in player.npcs:
                self.bot.db.npcs.update_one(npc.f, {'$set': npc.to_dict()}, upsert=True)


    @tasks.loop(hours=12)
    async def config_variables(self):
        self.bot.APPROVAL_CHANNEL = self.bot.guilds[0].get_channel(924062961222447126)
        self.bot.NEW_PLAYER_ROLE = self.bot.guilds[0].get_role(921113949691334706)
        self.bot.QUEST_DM_ROLES = [self.bot.guilds[0].get_role(925450330777473064),
                                   self.bot.guilds[0].get_role(923051032202846218)]
        self.bot.ALL_DM_ROLES = [
            self.bot.guilds[0].get_role(925450330777473064),
            self.bot.guilds[0].get_role(923051032202846218),
            self.bot.guilds[0].get_role(925449950614130760),
            self.bot.guilds[0].get_role(925450189278433360)
        ]
        self.bot.DEFAULT_PC_AVATAR = 'https://i.imgur.com/v47ed3Y.jpg'
        self.bot.CHANGE_LOG_CHANNEL = self.bot.guilds[0].get_channel(930985964472500315)



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
        # npcs = []
        # cursor = self.db.npcs.find()
        # all_members = self.bot.get_all_members()
        # async for each_npc in cursor:
        #     owner = [member for member in all_members if member.id == each_npc['owner']]
        #     npc = Npc(owner=owner,
        #               name=each_npc['name'],
        #               prefix=each_npc['prefix'],
        #               avatar=each_npc['avatar'],
        #               _id=each_npc['_ic'],
        #               rpxp=each_npc['rpxp'],
        #               users=[player for player in self.bot.players if player.id == each_npc])
        # self.bot.npcs = npc_cache

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
