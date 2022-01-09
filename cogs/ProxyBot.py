from disnake.ext import commands
from disnake import Message, Webhook, TextChannel, Member
from utils.kerna_classes import Player, Character
from typing import List


async def webhook_process(channel: TextChannel) -> Webhook:
    webhooks = await channel.webhooks()
    if "Kerna Proxy Service" not in [webhook.name for webhook in webhooks]:
        webhook = await channel.create_webhook(name="Kerna Proxy Service")
    else:
        webhook = [webhook for webhook in webhooks if webhook.name == "Kerna Proxy Service"][0]
    return webhook


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
            prefix = msg.content.split(":")[0]
            content = msg.content[msg.content.index(":") + 1:]
            me, characters = self.get_player_characters(msg.author)
            if prefix in me.prefixes:
                character: Character = [character for character in characters if character.prefix == prefix][0]
                if character.location.name.lstrip("d: ").lower() == msg.channel.category.name.lower():
                    if msg.reference: # this means it was a reply
                        m = self.bot.get_message(msg.reference.message_id)
                        pre = f'> {m.content} \n@{m.author.name} - [jump]({m.jump_url})\n'
                        content = pre + content
                    webhook = await webhook_process(msg.channel)
                    await msg.delete()
                    if content != '':
                        await webhook.send(content, username=character.name, avatar_url=character.avatar)
                else:
                    await msg.reply(f'`{character.name}` is not at this location. '
                                    f'Character is currently in `{character.location.name}`', delete_after=10)
                    await msg.delete(delay=10)


def setup(bot):
    bot.add_cog(ProxyBot(bot))
