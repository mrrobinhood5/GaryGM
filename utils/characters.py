from disnake import Embed, Role, Color, Member
from disnake.ext.commands import option_enum
from main import bot
from config import APPROVAL_REACTION
from typing import List

# TODO: Add entry points to the Database
EntryPoint = option_enum({"Docks": "922262282539507752", "Gate": "922262406317633536", "Slums": "922262527587532830"})
# TODO: add this option to the bot or the DB
DEFAULT_PC_AVATAR = 'https://i.imgur.com/v47ed3Y.jpg'


class Player:

    def __init__(self, d: dict):
        # load stuff from dict, this goes to the db
        for k, v in d.items():
            self.__setattr__(k, v)

        # temp data for the embeds
        # self.db = bot.db
        self.player: Member = bot.guilds[0].get_member(int(self.player))
        # location data
        self.keys: List[Role] = [bot.guilds[0].get_role(int(key)) for key in self.keys]
        self.location: Role = bot.guilds[0].get_role(int(self.location))

    async def fast_travel(self, role: Role):
        """ change the player to a new location from fast travel """
        # Need to check if there are others characters still using that role
        await self.player.add_roles(role)
        if not [x for x in bot.character_cache if x.player.id == self.player.id and x.location == self.location]:
            await self.player.remove_roles(self.location)
        self.location = role
        self.save()

    def save(self):
        """ Save the info to DB"""
        bot.db.players.update_one(self.f, {'$set': self.to_dict}, upsert=True)

    @property
    def f(self):
        """ f is used as the db filter """
        r = {"player": str(self.player.id), "character": self.character}
        return r

    @property
    def player_name(self):
        return self.player.name

    @property
    def channels(self):
        district_name = self.location.name.lstrip("d: ")
        return [x.channels for x in bot.guilds[0].categories if x.name.lower() == district_name.lower()][0]

    @property
    def to_dict(self):
        """ Transform the object to dict for DB entry"""
        r = {
            "player": str(self.player.id),
            "character": self.character,
            "backstory": self.backstory,
            "avatar": self.avatar,
            "prefix": self.prefix,
            "approved": self.approved,
            "keys": [str(x.id) for x in self.keys],
            "location": str(self.location.id) # is a role
        }
        return r

    def request_approval(self):
        """ Build the Embed to request approval character."""
        e = Embed(
            title="Player Approval Started",
            description=f"Submitted by **{self.player_name}**",
            color=Color.blue())
        e.add_field(name=self.character, value=self.backstory, inline=False),
        e.add_field(name="Start Point", value=self.location.name)
        e.add_field(name="Proxy Prefix", value=self.prefix)
        e.add_field(name="DM Actions",
                    value="DM will review your backstory and your `!vsheet` that should be posted in <#924069254637158441>",
                    inline=False)
        e.set_thumbnail(url=self.avatar)
        e.set_footer(text=f'{self.player.id}|{self.location.id}')
        return e

    def embed(self):
        """ Build the Embed to show the character in lists."""
        e = Embed(
            title=self.character,
            description=self.backstory,
            color=Color.yellow())
        e.add_field(name="Location", value=self.location.name)
        e.add_field(name="Keys", value=self.keys)
        e.add_field(name="Proxy Prefix", value=self.prefix)
        e.add_field(name="More info?", value="I dunno what other info should be relevant", inline=False)
        e.set_thumbnail(url=self.avatar)
        return e


class Approval:

    def __init__(self, msg, payload):
        self.approver = payload.member.name
        self.embed = msg.embeds[0]
        self.embed.title = self.embed.title.replace("Started", "Complete")
        self.player = msg.guild.get_member(int(self.embed.footer.text.split("|")[0]))
        self.role = msg.guild.get_role(int(self.embed.footer.text.split("|")[1]))
        self.name = self.embed.fields[0].name
        self.approval = True if payload.emoji == APPROVAL_REACTION else False
        self.embed.description += f'\n{"Approved" if self.approval else "Disapproved"} by **{self.approver}**'

    @property
    def f(self):
        """ f is used as the db filter """
        r = {"player": str(self.player.id), "character": self.name}
        return r

    async def process_character(self):
        if self.approval:
            self.embed.color = Color.green()
            bot.db.players.update_one(self.f, {'$set': {"approved": True}}, upsert=True)
            await self.player.add_roles(self.role)
            await self.player.remove_roles(bot.NEW_PLAYER_ROLE)
        else:
            self.embed.color = Color.red()
            await bot.db.players.delete_one(self.f)

    def get_embed(self):
        return [self.embed]
