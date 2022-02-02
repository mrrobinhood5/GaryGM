from __future__ import annotations
import disnake
from disnake import Embed
# from utils.player import Player
from bson import ObjectId
from typing import List
from dataclasses import dataclass, field


# TODO: Move this to bot attrs
DEFAULT_NPC_AVATAR = 'https://i.imgur.com/ET6JF3H.png'


@dataclass()
class Npc:
    owner: 'Player'
    name: str
    prefix: str
    shared: bool
    description: str
    avatar: str = DEFAULT_NPC_AVATAR
    _id: ObjectId = ObjectId()
    rpxp: int = 0

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
            "rpxp": self.rpxp,
            "shared": self.shared,
            "description": self.description
        }
        return d

    @property
    def embed(self) -> Embed:
        e = Embed(
            title='NPC Card',
            color=disnake.Color.yellow())
        e.add_field(name=self.name, value=f'Description: {self.description}')
        e.add_field(name="Owner", value=self.owner.member.name)
        e.add_field(name="Shared?", value=f'{self.shared}')
        # e.add_field(name="Authorized", value=f'{[user.member.name for user in self.users]}')
        e.set_thumbnail(url=self.avatar)
        return e

    # def add_authorized(self, player: Player):
    #     self.users.append(player)