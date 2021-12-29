from disnake import ApplicationCommandInteraction
from disnake.ext import commands
from utils.navigator import DropdownView


class NavigatorCommands(commands.Cog, name='Navigator Commands'):

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command()
    async def fast_travel(
            self,
            inter: ApplicationCommandInteraction):
        """Use this to Fast Travel along the city"""
        # TODO: Add a check to see what keys the player has, and enter them.
        # Create the view containing our dropdown
        view = DropdownView()

        # Sending a message containing our view
        await inter.send("Fast Travel to where?", view=view, ephemeral=True)


def setup(bot):
    bot.add_cog(NavigatorCommands(bot))