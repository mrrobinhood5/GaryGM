from __future__ import annotations
from dataclasses import dataclass, field
from disnake import Embed, Member, Role, TextChannel, Color, Enum, RawReactionActionEvent
from typing import List, Union
from bson.objectid import ObjectId
from utils.npc import Npc
from datetime import datetime
from config import APPROVAL_REACTION, DENIAL_REACTION
from utils.characters import Character




class CharacterVariant:

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
        """ Returns a list of district names that your characters are in """
        d = []
        for character in self.characters:
            d.append(character.location.name.lstrip("d: "))
        return d

    @property
    def character_list(self) -> List[Embed]:
        """ Lists all your characters """
        # how is this different player.characters?
        character_list = []
        return character_list
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

    @property
    def character_count(self):
        return len(self.characters)

    @property
    def prefixes(self):
        return [character.prefix for character in self.characters]




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
                  description=f"Submitted by **{self.character.player.member.name}**", color=Color.blue())
        e.add_field(name=self.character.name, value=self.character.backstory, inline=False),
        e.add_field(name="Start Point", value=self.character.location.name)
        e.add_field(name="Proxy Prefix", value=self.character.prefix)
        e.add_field(name="DM Actions",
                    value="DM will review your backstory and your `!vsheet` "
                          "that should be posted in <#924069254637158441>",
                    inline=False)
        e.set_thumbnail(url=self.character.avatar)
        e.set_footer(text=f'{self.character.name}|{self.character.player.member.id}|Character Count: {self.character.player.character_count}')
        self.embed_to_approve = e

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
