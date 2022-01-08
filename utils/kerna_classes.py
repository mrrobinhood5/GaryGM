from dataclasses import dataclass, field
from disnake import Embed, Member, Role, TextChannel, Color, Enum, RawReactionActionEvent
from typing import List, Union
from bson.objectid import ObjectId
from utils.npc import Npc
from datetime import datetime
from config import APPROVAL_REACTION, DENIAL_REACTION


@dataclass
class Character:
    player: Union['Player', Member]
    name: str
    backstory: str
    avatar: str
    prefix: str
    location: Role
    variants: List['CharacterVariant'] = None
    familiars: List['CharacterFamiliar'] = None
    approved: bool = False
    alive: bool = True
    keys: List[Role] = None
    rpxp: int = 0
    _id: ObjectId = ObjectId()

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
            "keys": [str(x.id) for x in self.keys] if self.keys else [],  # role id string
            "location": str(self.location.id),  # role id string
            "variants": [v.to_dict() for v in self.variants] if self.variants else [],
            "familiars": [f.to_dict() for f in self.familiars] if self.familiars else [],
            "rpxp": self.rpxp
        }
        return d

    async def fast_travel(self, role: Role) -> str:
        """ Complete a fast-travel for this character """
        # add the role you went to
        await self.player.add_roles(role)

        # remove the location if no one else has it
        if not [character for character in self.player.characters if character.location == role]:
        # if not [x for x in bot.character_cache if x.player.id == self.player.id and x.location == self.location]:
            await self.player.remove_roles(self.location)
        self.location = role
        # self.save()  # need a better way of saving the character to DB
        return f"`{self.name}` has traveled to `{role.name.lstrip('d: ')}`"

    def embed(self) -> Embed:
        """ Returns an embed representation of the character """
        e = Embed(title=self.name, description=self.backstory, color=Color.blue())
        e.add_field(name="Proxy Prefix", value=self.prefix)

        e.add_field(name="Location", value=self.location.name.lstrip('d: '), inline=False)
        e.add_field(name="Keys", value=self.keys)

        e.add_field(name="Familiars", value=self.familiars or None, inline=False)
        e.add_field(name="Variants", value=self.variants or None)
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
        return self.location.name.lstrip("d: ")

    @property
    def channels(self) -> List[TextChannel]:
        """ returns a list of channels that the character is able to see """
        # I dont think we can pull up the channels from here
        return [category.channels for category in self.location.guild.categories if category.name.lower() == self.location.name.lstrip("d: ").lower()][0]

    @property
    def id(self):
        return self._id

class CharacterExtension:
    character: Character
    name: str
    avatar: str
    prefix: str  # variant prefixes will be prefixed by main character prefix. e.g. rob.undead

    def to_dict(self) -> dict:
        """ Returns a dict representation of a CharacterExtension """
        d = {
            "character": self.character.name,
            "name": self.name,
            "avatar": self.avatar,
            "prefix": self.prefix
        }
        return d


class CharacterFamiliar(CharacterExtension):

    @property
    def prefix(self) -> str:
        return f'{super().character.prefix}.{self.prefix}'


class CharacterVariant(CharacterExtension):

    @property
    def prefix(self) -> str:
        return f'{super().character.prefix}.{self.prefix}'


# Quests
class Quest:
    name: str
    description: str
    active: bool
    participants: List[Character]
    dm: 'DungeonMaster'
    disposition: str


class Bounty(Quest):
    completed: List[Character]


class MainQuest(Quest):
    start_time: datetime
    wait_list: List[Character]


@dataclass()
class Player:
    member: Member
    characters: List[Character] = field(default_factory=list)
    _id: ObjectId = ObjectId()

    def add_character(self, character: Character):
        """ Add a Character object to a Player instance """
        self.characters.append(character)

    def delete_character(self, character: Character):
        """ Remove a Character object from a Player instance """
        return self.characters.pop(self.characters.index(character))

    @property
    def districts(self) -> List[str]:
        """ Returns a list of district names """
        d = []
        for character in self.characters:
            d.append(character.location.name.lstrip("d: "))
        return d

    @property
    def character_list(self) -> List[Embed]:
        """ Lists all your characters """
        character_list = []
        return character_list
        pass

    def update_character(self):
        """ I don't know how to implement updates yet """
        pass

    @property
    def f(self):
        """ the find filter specific to this object """
        return {"_id": self._id}

    @property
    def to_dict(self):
        """ sends the dict representation for the db save"""
        d = {
            "member": str(self.member.id),
            "characters": [character.id for character in self.characters]
        }
        return d

    @property
    def id(self):
        return self._id

# DM
class DungeonMasterType(Enum):
    NPC_DM = 1
    HUNT_DM = 2
    BOUNTY_DM = 3
    QUEST_DM = 4
    LORE_DM = 5


class DungeonMaster():
    type: DungeonMasterType
    dm_prefix: str
    dmxp: int
    npcs: List[Npc] = []
    quests: List[Quest] = []
    bounties: List[Bounty] = []
    dm_private_channel: TextChannel


@dataclass
class Approval:
    character: Character
    embed_to_approve: Embed = None
    approver: DungeonMaster = None
    approved: bool = False
    # approval_id: str = embed_to_approve.footer.text

    def __post_init__(self) -> None:
        """ Build the Embed to request approval character."""
        e = Embed(title="Approval Started",
                  description=f"Submitted by **{self.character.player.name}**", color=Color.blue())
        e.add_field(name=self.character.name, value=self.character.backstory, inline=False),
        e.add_field(name="Start Point", value=self.character.location.name)
        e.add_field(name="Proxy Prefix", value=self.character.prefix)
        e.add_field(name="DM Actions",
                    value="DM will review your backstory and your `!vsheet` "
                          "that should be posted in <#924069254637158441>",
                    inline=False)
        e.set_thumbnail(url=self.character.avatar)
        # bot.pending_approvals.append(self)
        e.set_footer(text=f'{self.character.name}|{self.character.player.id}')
        self.embed_to_approve = e
        # return self.embed_to_approve

    @property
    def f(self):
        """ returns the filter dict to find it in the database """
        return {"character": self.character.name}

    @property
    def to_dict(self):
        """ sends its dict representation for saving into db """
        d = {
            "character": self.character.name,
            "embed_to_approve": self.embed_to_approve.to_dict(),
            "approved": self.approved
        }
        return d

    @property
    def embed(self) -> List[Embed]:
        return [self.embed_to_approve]

    def process_approval(self, payload: RawReactionActionEvent):
        if payload.emoji == APPROVAL_REACTION:
            self.embed_to_approve.title = self.embed_to_approve.title.replace("Started", "Complete")
            self.embed_to_approve.description += f"\nApproved by **{payload.member.name}**"
            self.embed_to_approve.colour = Color.green()
            self.character.approved = True
            self.approved = True
        else:
            self.embed_to_approve.title = self.embed_to_approve.title.replace("Started", "Complete")
            self.embed_to_approve.description += f"\nDenied by **{payload.member.name}**"
            self.embed_to_approve.colour = Color.red()
