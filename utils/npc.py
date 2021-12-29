import disnake
from disnake import ApplicationCommandInteraction, Embed

# TODO: Move this to bot attrs
DEFAULT_NPC_AVATAR = 'https://i.imgur.com/ET6JF3H.png'


class Npc:

    def __init__(self, inter: ApplicationCommandInteraction, d: dict = {}):
        for k, v in d.items():
            self.__setattr__(k, v)
        self.db = inter.bot.db
        self.__post_init__()

    def __post_init__(self):
        """ post init processing """
        self.name = self.name.title()
        self.roles = []

    @property
    def f(self):
        """ build the filter for the db """
        r = {"name": self.name}
        return r

    def save(self):
        """ save it to the db """
        self.db.npc.update_one(self.f, {'$set': self.to_dict()}, upsert=True)


    def to_dict(self):
        """ build a dict to save to db """
        d = {
            "name": self.name,
            "prefix": self.prefix,
            "avatar": self.avatar,
            "owner": str(self.owner.id),
            "roles": self.roles
        }
        return d

    def embed(self):
        e = Embed(
            title='NPC Card',
            color=disnake.Color.yellow())
        e.add_field(name=self.name, value='Description here? Maybe')
        e.add_field(name="Owner", value=self.owner.name)
        e.add_field(name="Authorized", value=f'{self.roles}')
        e.set_thumbnail(url=self.avatar)
        return e
