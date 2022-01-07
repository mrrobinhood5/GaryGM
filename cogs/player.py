from disnake import Member
from disnake.ext import commands
from utils.kerna_classes import Player


class PlayerCommands(commands.Cog, name='Player commands'):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: Member):
        """ Will need to make a Player object and store it in cache. """
        new_player = Player(member=member)
        self.bot.players.append(new_player)


def setup(bot):
    bot.add_cog(PlayerCommands(bot))
