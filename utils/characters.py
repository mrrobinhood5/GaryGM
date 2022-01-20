from __future__ import annotations
from dataclasses import dataclass, field
from disnake import SelectOption, MessageInteraction, ButtonStyle, Role, Embed, Color, TextChannel, Message, Webhook
from disnake.ui import View, Select, Button
from typing import List
from bson import ObjectId

async def webhook_process(channel: TextChannel) -> Webhook:
    webhooks = await channel.webhooks()
    if "Kerna Proxy Service" not in [webhook.name for webhook in webhooks]:
        webhook = await channel.create_webhook(name="Kerna Proxy Service")
    else:
        webhook = [webhook for webhook in webhooks if webhook.name == "Kerna Proxy Service"][0]
    return webhook

@dataclass
class Character:
    player: 'Player'
    name: str
    backstory: str
    avatar: str
    prefix: str
    location: Role
    variants: List['CharacterVariant'] = field(default_factory=list)
    familiars: List['CharacterFamiliar'] = field(default_factory=list)
    approved: bool = False
    alive: bool = True
    keys: List[Role] = None
    rpxp: int = 0
    _id: ObjectId = ObjectId()

    def __repr__(self):
        return f'<Player: {self.player}, Character: {self.name}, Prefix: {self.prefix}, Familiars: {self.familiars}, Variants: {self.variants}'

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



    @property
    def dname(self):
        return self.name + "⚔"
    def update(self, attribute, changes):
        self.__setattr__(attribute, changes)

    @property
    def to_dict(self):
        """ Transform the character object to dict for DB entry"""
        d = {
            "_id": self._id,
            "player": self.player.id,
            "name": self.name,
            "backstory": self.backstory,
            "avatar": self.avatar,
            "prefix": self.prefix,
            "approved": self.approved,
            "alive": self.alive,
            "keys": [k.id for k in self.keys] if self.keys else [],  # role id string
            "location": self.location.id,
            "variants": [v.id for v in self.variants] if self.variants else [],
            "familiars": [f.id for f in self.familiars] if self.familiars else [],
            "rpxp": self.rpxp
        }
        return d

    async def fast_travel(self, destination: Role) -> str:
        """ Complete a fast-travel for this character """
        # change the current characters location to its destination
        original_location = self.location
        self.location = destination

        # remove the location if no one else has it
        if original_location not in [character.location for character in self.player.characters if character.name != self.name]:
            await self.player.member.remove_roles(original_location)

        # add the role you went to
        await self.player.member.add_roles(destination)

        # self.save()  # need a better way of saving the character to DB
        return f"`{self.name}` has traveled to `{destination.name[3:]}`"

    def embed(self) -> Embed:
        """ Returns an embed representation of the character """
        e = Embed(title=self.name, description=self.backstory, color=Color.blue())
        e.add_field(name="Proxy Prefix", value=self.prefix)

        e.add_field(name="Location", value=self.location.name.lstrip('d: '), inline=False)
        e.add_field(name="Keys", value=None if not self.keys else [key.name for key in self.keys], inline=True)

        e.add_field(name="Familiars", value=[familiar.name for familiar in self.familiars] or None, inline=False)
        e.add_field(name="Variants", value=[variant.name for variant in self.variants] or None, inline=True)
        e.set_thumbnail(url=self.avatar)
        return e

    def save(self):
        """ Saves the Character to the cache """
        # bot.db.players.update_one(self.f, {'$set': self.to_dict}, upsert=True)
        pass

    @property
    def f(self) -> dict:
        """ f returns a filter to the database for itself """
        return {"_id": self._id}

    @property
    def district_name(self) -> str:
        """ Returns the cleaned up name for the characters current district """
        return self.location.name[3:]

    @property
    def channels(self) -> List[TextChannel]:
        """ returns a list of channels that the character is able to see """
        # I dont think we can pull up the channels from here
        return [category.channels for category in self.location.guild.categories if category.name.lower() == self.district_name.lower()][0]

    @property
    def id(self):
        return self._id

    def add_key(self, key: Role):
        self.keys.append(key)

    def add_familiar(self, familiar: 'CharacterFamiliar'):
        self.familiars.append(familiar)

    def add_variant(self, variant: 'CharacterVariant'):
        self.variants.append(variant)

    # @property
    # def prefixes(self):
    #     p = []
    #     for familiar in self.familiars:
    #         p.append(familiar.prefix)
    #     for variant in self.variants:
    #         p.append(variant.prefix)
    #     return p

@dataclass
class CharacterFamiliar:
    character: Character
    name: str
    prefix: str
    avatar: str
    _id: ObjectId = ObjectId()
    rpxp: int = 0

    async def say(self, msg):
        await Character.say(self, msg)

    @property
    def dname(self):
        return self.name+"🦊"

    @property
    def id(self):
        return self._id

    @property
    def embed(self) -> Embed:
        """ Returns an embed representation of the Familiar """
        e = Embed(title=self.name, description=f'Belonging to {self.character.name}', color=Color.blue())
        e.add_field(name="Proxy Prefix", value=self.prefix)
        e.set_thumbnail(url=self.avatar)
        return e

    @property
    def to_dict(self):
        """ Transform the familiar object to dict for DB entry"""
        d = {
            "_id": self._id,
            "character": self.character.id,
            "name": self.name,
            "avatar": self.avatar,
            "prefix": self.prefix,
            "rpxp": self.rpxp
        }
        return d

    @property
    def f(self):
        """ f returns a filter to the database for itself """
        return {"_id": self._id}

    @property
    def district_name(self):
        return self.character.district_name

    def __repr__(self):
        return f'<Name: {self.name}, prefix: {self.prefix}, rpxp: {self.rpxp}>'

@dataclass
class CharacterVariant(CharacterFamiliar):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def dname(self):
        return self.name+"😎"

class CharacterDeleteConfirm(Button):
    def __init__(self):
        super().__init__(
            label="Are you Sure?",
            style=ButtonStyle.red
        )

    async def callback(self, inter: MessageInteraction):
        self.view.stop()


class CharacterAttributeDropdown(Select):
    def __init__(self):
        options = [SelectOption(label="Name", description="", value="name"),
                   SelectOption(label="Backstory", description="", value="backstory"),
                   SelectOption(label="Prefix", description="", value="prefix"),
                   SelectOption(label="Avatar", description="", value="avatar")]
        super().__init__(
            placeholder="Choose an attribute",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, inter: MessageInteraction):
        await inter.response.defer()
        # add the attribute - attribute to the view
        self.view.attribute = self.values[0]

        # update the view and return
        await inter.edit_original_message(content=f"What is the new value for `{self.values[0]}`", view=None)
        self.view.stop()


class CharactersDropdown(Select):
    def __init__(self, characters):
        options = []
        for character in characters:
            options.append(SelectOption(label=character.name, description="", value=character.name))
        super().__init__(
            placeholder="Choose a character",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, inter: MessageInteraction):
        await inter.response.defer()
        # add a character attribute to the view
        self.view.character = [x for x in self.view.characters if x.name == self.values[0]][0]

        # clean up the interaction
        self.placeholder = self.values[0]
        self.disabled = True

        # choose what action is gonna happen
        if self.view.action == "edit":
            self.view.add_item(CharacterAttributeDropdown())
        elif self.view.action == "delete":
            self.view.add_item(CharacterDeleteConfirm())

        await inter.edit_original_message(view=self.view)



class CharacterChooseView(View):
    def __init__(self, characters: List[Character], action: str):
        self.characters = characters
        self.action = action
        super().__init__()

        # Adds the dropdown to our view object.
        self.add_item(CharactersDropdown(characters))

