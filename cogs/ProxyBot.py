from disnake.ext import commands
from disnake import Message, Webhook, TextChannel


class ProxyBot(commands.Cog, name='ProxyBot'):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, msg: Message):
        """ listener for npc bots """
        # TODO: Clean this shit up, maybe make a proxy-guy object
        me = msg.author.id
        # determine if its a potential prefix
        if ':' in msg.content:
            poss_prefix, content = msg.content.split(':')
            # then check if the message sender has any prefixes saved
            if player := self.bot.prefixes_cache.get(me):
                if character := player.get(poss_prefix):
                    if character.location.name.lstrip("d: ").lower() == msg.channel.category.name.lower():
                        if msg.reference: # means this was a reply
                            m = self.bot.get_message(msg.reference.message_id)
                            pre = f'> {m.content} \n@{m.author.name} - [jump]({m.jump_url})\n'
                            content = pre+content
                        webhook = await self.webhook_process(msg.channel)
                        await msg.delete()
                        if content != '':
                            await webhook.send(content, username=character.character, avatar_url=character.avatar)
                    else:
                        await msg.reply(f'`{character.character}` is not at this location. '
                                        f'Character is currently in `{character.location.name}`', delete_after=10)
                        await msg.delete(delay=10)

    async def webhook_process(self, channel: TextChannel) -> Webhook:
        webhooks = await channel.webhooks()
        if "Kerna Proxy Service" not in [webhook.name for webhook in webhooks]:
            webhook = await channel.create_webhook(name="Kerna Proxy Service")
        else:
            webhook = [webhook for webhook in webhooks if webhook.name == "Kerna Proxy Service"][0]
        return webhook


def setup(bot):
    bot.add_cog(ProxyBot(bot))
