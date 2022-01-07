# from typing import Union, List
# from disnake import Role, Embed, Color
# from utils.characters import Character, CharacterFamiliar, CharacterVariant
# from utils.player import DungeonMaster
# from main import bot
# from dataclasses import dataclass





# class Approval:
#
#     def __init__(self, msg, payload):
#         self.approver = payload.member.name #
#         self.embed = msg.embeds[0] #
#         self.embed.title = self.embed.title.replace("Started", "Complete")
#         self.player = msg.guild.get_member(int(self.embed.footer.text.split("|")[0]))
#         self.role = msg.guild.get_role(int(self.embed.footer.text.split("|")[1]))
#         self.name = self.embed.fields[0].name
#         self.approval = True if payload.emoji == APPROVAL_REACTION else False
#         self.embed.description += f'\n{"Approved" if self.approval else "Disapproved"} by **{self.approver}**'
#
#     @property
#     def f(self):
#         """ f is used as the db filter """
#         r = {"player": str(self.player.id), "character": self.name}
#         return r
#
#     async def process_character(self):
#         if self.approval:
#             self.embed.color = Color.green()
#             bot.db.players.update_one(self.f, {'$set': {"approved": True}}, upsert=True)
#             await self.player.add_roles(self.role)
#             await self.player.remove_roles(bot.NEW_PLAYER_ROLE)
#         else:
#             self.embed.color = Color.red()
#             await bot.db.players.delete_one(self.f)
#
#     def get_embed(self):
#         return [self.embed]