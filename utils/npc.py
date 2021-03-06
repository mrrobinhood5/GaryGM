from __future__ import annotations
import disnake
from disnake import Embed, Message
# from utils.player import Player
from utils.characters import webhook_process
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
            title=self.name,
            color=disnake.Color.yellow())
        e.add_field(name="Description", value=f'{"None" if not self.description else self.description}', inline=False)
        e.add_field(name="Prefix", value=self.prefix)
        e.add_field(name="Owner", value=self.owner.member.name)
        e.add_field(name="Shared?", value=f'{"True" if self.shared else "False"}')
        # e.add_field(name="Authorized", value=f'{[user.member.name for user in self.users]}')
        e.set_thumbnail(url=self.avatar)
        return e

    @property
    def dname(self):
        return self.name + " - 🤝" if self.shared else self.name + " - 😑"

    async def say(self, msg: Message):
        content = msg.content[msg.content.index(":") + 1:]
        if msg.reference:  # this means it was a reply
            m: Message = msg.reference.cached_message
            pre = f'> {m.content} \n@{m.author.name} - [jump]({m.jump_url})\n'
            content = pre + content
        webhook = await webhook_process(msg.channel)
        await msg.delete()
        if msg.content != '':
            await webhook.send(content, username=self.dname, avatar_url=self.avatar)
            self.rpxp += 1

    def update(self, attribute, changes):
        self.__setattr__(attribute, changes)

    # def add_authorized(self, player: Player):
    #     self.users.append(player)