from __future__ import annotations
from disnake.ext import commands
from disnake import Message, Webhook, TextChannel, Member
from utils.player import Player
from utils.characters import Character, CharacterFamiliar, CharacterVariant
from typing import List





class ProxyBot(commands.Cog, name='ProxyBot'):

    def __init__(self, bot):
        self.bot = bot

    def get_player_characters(self, author: Member) -> (Player, List[Character]):
        me: Player = [player for player in self.bot.players if player.member.id == author.id][0]
        characters = [character for character in me.characters if character.approved]
        return me, characters

    @commands.Cog.listener()
    async def on_message(self, msg: Message):
        """ listener for npc bots """

        # TODO: Clean this shit up, maybe make a proxy-guy object
        # TODO: Make it so edits also trigger this
        # determine if its a potential prefix
        if ':' in msg.content and not msg.author.bot:
            prefix = msg.content.split(":")[0].lower().rstrip()
            me, characters = self.get_player_characters(msg.author)
            if prefix in [p[0] for p in me.prefixes]:
                target: Character = [p[1] for p in me.prefixes if prefix == p[0]][0]
            else:
                return
            if target.district_name.lower() == msg.channel.category.name.lower():
                await target.say(msg)
            else:
                await msg.reply(f'`{target.name}` is not at this location. '
                                f'Character is currently in `{target.location.name}`', delete_after=10)
                await msg.delete(delay=10)




            #
            # if "." in prefix: # its a familiar prefix


                # character: Character = [character for character in characters if character.prefix == char_prefix][0]
                # if character.familiars:
                #     familiar: CharacterFamiliar = [familiar for familiar in character.familiars if familiar.prefix == prefix][0]
                # if character.variants:
                #     variant: CharacterVariant = [variant for variant in character.variants if variant.prefix == prefix][0] if character.variants else None
                # target = [familiar or variant]

            #     else:
            #         await msg.reply(f'`{character.name}` is not at this location. '
            #                         f'Character is currently in `{character.location.name}`', delete_after=10)
            #         await msg.delete(delay=10)
            #
            # elif prefix in me.prefixes: #checks for character prefix
            #     character: Character = [character for character in characters if character.prefix == prefix][0]
            #     # this needs to have both districts or keys
            #     if character.district_name.lower() == msg.channel.category.name.lower():
            #         if msg.reference: # this means it was a reply
            #             m = self.bot.get_message(msg.reference.message_id)
            #             pre = f'> {m.content} \n@{m.author.name} - [jump]({m.jump_url})\n'
            #             content = pre + content
            #         webhook = await webhook_process(msg.channel)
            #         await msg.delete()
            #         if content != '':
            #             await webhook.send(content, username=character.name, avatar_url=character.avatar)
            #             character.rpxp += 1
            #     else:
            #         await msg.reply(f'`{character.name}` is not at this location. '
            #                         f'Character is currently in `{character.location.name}`', delete_after=10)
            #         await msg.delete(delay=10)


def setup(bot):
    bot.add_cog(ProxyBot(bot))
