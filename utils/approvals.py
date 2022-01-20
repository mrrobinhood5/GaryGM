from __future__ import annotations
from typing import List
from disnake import Embed, Color, RawReactionActionEvent
from utils.characters import Character
# from utils.player import DungeonMaster
from dataclasses import dataclass
from config import APPROVAL_REACTION


@dataclass
class Approval:
    character: Character
    embed_to_approve: Embed = None
    approver = None
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
