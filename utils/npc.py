from __future__ import annotations
import disnake
from disnake import Embed
from utils.player import Player
from bson import ObjectId
from typing import List
from dataclasses import dataclass, field


# TODO: Move this to bot attrs
DEFAULT_NPC_AVATAR = 'https://i.imgur.com/ET6JF3H.png'


@dataclass
class Npc:
    owner: Player
    name: str
    prefix: str
    avatar: str = DEFAULT_NPC_AVATAR
    _id: ObjectId = ObjectId()
    rpxp: int = 0
    users: List[Player] = field(default_factory=list)

    def __post_init__(self):
        """ post init processing """
        self.name = self.name.title()

    @property
    def f(self):
        """ build the filter for the db """
        r = {"_id": self._id}
        return r

    def to_dict(self):
        """ build a dict to save to db """
        d = {
            "_id": self._id,
            "name": self.name,
            "prefix": self.prefix,
            "avatar": self.avatar,
            "owner": self.owner.id,
            "users": [u.id for u in self.users],
            "rpxp": self.rpxp
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
