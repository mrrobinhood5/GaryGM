from disnake.ext import commands
from disnake import ApplicationCommandInteraction, CategoryChannel, Embed
from typing import List


class Search(commands.Cog, name='ChannelSearch'):

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command()
    async def search(
            self,
            inter: ApplicationCommandInteraction,
            keyword: str):
        """Search for keywords in channel descriptions"""

        t = Embed(title="Channel Search", description=f"using keyword `{keyword}`")

        for channel in inter.guild.channels:
            if type(channel) != CategoryChannel:
                if channel.topic:
                    if keyword.lower() in channel.topic.lower():
                        t.add_field(name=f'{channel.category.name.title()}',
                                    value=f'*{channel.mention}*\n'
                                          f'{channel.topic}')
        await inter.send(embeds=[t], ephemeral=True)


def setup(bot):
    bot.add_cog(Search(bot))
