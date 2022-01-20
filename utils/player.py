from __future__ import annotations
from dataclasses import dataclass, field
from bson import ObjectId
from disnake import Member, Embed
from typing import List
from utils.characters import Character
from utils.dungeon_master import DungeonMasterType



@dataclass
class Player:
    member: Member
    characters: List[Character] = field(default_factory=list)
    _id: ObjectId = ObjectId()
    dm_type: DungeonMasterType = 0

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
            "member": self.member.id,
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
        p = []
        for character in self.characters:
            p.append((character.prefix.lower(), character))
            for familiar in character.familiars:
                p.append((familiar.prefix.lower(), familiar))
            for variant in character.variants:
                p.append((variant.prefix.lower(), variant))
        return p

    def __repr__(self):
        return f'<Member: {self.member.name}, Characters: {[c.name for c in self.characters]}'

    def get_character(self, char):
        return [c for c in self.characters if char.lower() in c.name.lower()][0]


