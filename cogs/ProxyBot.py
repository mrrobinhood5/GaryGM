from disnake.ext import commands
from disnake import Message


class ProxyBot(commands.Cog, name='ProxyBot'):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, msg: Message):
        """ listener for npc bots """
        # TODO: Clean this shit up, maybe make a proxy-guy object
        pid = str(msg.author.id)
        # determine if its a potential prefix
        if ':' not in msg.content:
            return
        # then check if the message sender has any prefixes saved
        if pid in self.bot.pc_prefixes.keys():
            # then check if the prefix is valid
            if msg.content[:msg.content.index(':')] in self.bot.pc_prefixes[pid].keys():
                # if it's on the list, start checks to see if you are in the location of the NPC you are trying to use
                p, m = msg.content.split(':')
                n, a, l = self.bot.pc_prefixes[pid][p]
                current_location = msg.guild.get_role(int(l)).name
                # compare the current category name to the location name
                if msg.channel.category.name != current_location:
                    await msg.reply(f'`{n}` is not at this location. Character is currently in `{current_location}`', delete_after=10)
                    await msg.delete(delay=10)
                    return
                c = msg.channel

                # valid everything, check for webhook and install
                webhooks = await c.webhooks()
                if "Kerna Proxy Service" not in [w.name for w in webhooks]:
                    webhook = await c.create_webhook(name="Kerna Proxy Service")
                else:
                    webhook = [w for w in webhooks if w.name == "Kerna Proxy Service"][0]

                # relay the message
                await msg.delete()
                if m != '':
                    await webhook.send(m, username=n, avatar_url=a)


def setup(bot):
    bot.add_cog(ProxyBot(bot))
