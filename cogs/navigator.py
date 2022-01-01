from disnake import ApplicationCommandInteraction
from disnake.ext import commands
from utils.navigator import FastTravelView


class NavigatorCommands(commands.Cog, name='Navigator Commands'):

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command()
    async def fast_travel(
            self,
            inter: ApplicationCommandInteraction):
        """Use this to Fast Travel along the city"""
        # TODO: Add a check to see what keys the player has, and enter them.

        # and a list of approved characters you own
        me = str(inter.author.name)
        PCs = [char for char in inter.bot.character_cache if char.player.name == me and char.approved]
        if not PCs:
            await inter.send("**You currently have no characters use `/character add` or wait for an approval. "
                             "Characters take 1 minute from approvals to be ready**", ephemeral=True)

        # get the current districts from the server to list as options
        districts = [(r.name.strip("d: "), str(r.id)) for r in inter.guild.roles if r.name.startswith("d:")]

        # Create the view containing our dropdown
        view = FastTravelView(districts, PCs)

        # Sending a message containing our view
        await inter.send("Fast Travel to where?", view=view, ephemeral=True)


def setup(bot):
    bot.add_cog(NavigatorCommands(bot))