import disnake
from disnake import Embed, ApplicationCommandInteraction
from disnake.ext.commands import option_enum

# TODO: Add entry points to the Database
EntryPoint = option_enum({"Docks": "922262282539507752", "Gate": "922262406317633536", "Slums": "922262527587532830"})
# TODO: add this option to the bot or the DB
DEFAULT_PC_AVATAR = 'https://i.imgur.com/v47ed3Y.jpg'

class Player:

    def __init__(self, inter: ApplicationCommandInteraction, d: dict = {}):
        # load stuff from dict, this goes to the db
        for k, v in d.items():
            self.__setattr__(k, v)

        # temp data for the embeds
        self.db = inter.bot.db
        self.player_name = inter.author.name

        # location data
        self.keys = [inter.guild.get_role(int(key)) for key in self.keys]
        self.location = inter.guild.get_role(int(self.location))


    def save(self):
        """ Save the info to DB"""
        self.db.players.update_one(self.f, {'$set': self.to_dict}, upsert=True)

    @property
    def f(self):
        """ f is used as the db filter """
        r = {"player": self.player, "character": self.character}
        return r

    @property
    def to_dict(self):
        """ Transform the object to dict for DB entry"""
        r = {
            "player": self.player,
            "character": self.character,
            "backstory": self.backstory,
            "avatar": self.avatar,
            "prefix": self.prefix,
            "approved": self.approved,
            "keys": self.keys,
            "location": str(self.location.id)
            }
        return r

    def request_approval(self):
        """ Build the Embed to request approval character."""
        e = Embed(
            title="Player Approval Started",
            description=f"Submitted by **{self.player_name}**",
            color=disnake.Color.red())
        e.add_field(name=self.character, value=self.backstory, inline=False),
        e.add_field(name="Start Point", value=self.location.name)
        e.add_field(name="Proxy Prefix", value=self.prefix)
        e.add_field(name="DM Actions", value="DM will review your backstory and your `!vsheet` that should be posted in <#924069254637158441>", inline=False)
        e.set_thumbnail(url=self.avatar)
        e.set_footer(text=f'{self.player}|{self.location.id}')
        return e

    def embed(self):
        """ Build the Embed to show the character in lists."""
        e = Embed(
            title=self.character,
            description=self.backstory,
            color=disnake.Color.yellow())
        e.add_field(name="Location", value=self.location.name)
        e.add_field(name="Keys", value=self.keys)
        e.add_field(name="Proxy Prefix", value=self.prefix)
        e.add_field(name="More info?", value="I dunno what other info should be relevant", inline=False)
        e.set_thumbnail(url=self.avatar)
        return e



class Approval:

    def __init__(self, db, msg, payload):
        self.db = db
        # self.db = self.bot.db
        self.approver = payload.member.name
        self.embed = msg.embeds[0]
        self.embed.description += f'\nApproved by **{self.approver}**'
        self.embed.title = self.embed.title.replace("Started", "Complete")
        self.embed.color = disnake.Color.green()
        self.player_id = self.embed.footer.text.split("|")[0]
        self.role_id = self.embed.footer.text.split("|")[1]
        self.name = self.embed.fields[0].name
        self.approve_character()

    @property
    def f(self):
        """ f is used as the db filter """
        r = {"player": self.player_id, "character": self.name}
        return r

    # @property
    # def role_id(self):
    #     return int(self.role_id)
    #
    # @property
    # def player_id(self):
    #     return int(self.player_id)

    def approve_character(self):
        self.db.players.update_one(self.f, {'$set': {"approved": True}}, upsert=True)

    def get_embed(self):
        return [self.embed]



