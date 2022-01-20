from __future__ import annotations
from dataclasses import dataclass, field
from disnake import Embed, Member, Role, TextChannel, Color, Enum, RawReactionActionEvent
from typing import List, Union
from bson.objectid import ObjectId
from utils.npc import Npc
from datetime import datetime
from config import APPROVAL_REACTION, DENIAL_REACTION
from utils.characters import Character




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




# DM



class DungeonMaster():
    type: DungeonMasterType
    dm_prefix: str
    dmxp: int
    npcs: List[Npc] = []
    quests: List[Quest] = []
    bounties: List[Bounty] = []
    dm_private_channel: TextChannel


