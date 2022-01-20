from disnake import ApplicationCommandInteraction, Member
from utils.player import Player
from utils.characters import Character
from typing import List
from disnake.ext import commands
from utils.navigator import FastTravelView


class NavigatorCommands(commands.Cog, name='Navigator Commands'):

    def __init__(self, bot):
        self.bot = bot

    def get_player_characters(self, author: Member) -> (Player, List[Character]):
        me: Player = [player for player in self.bot.players if player.member.id == author.id][0]
        characters = [character for character in me.characters if character.approved]
        return me, characters

    @commands.slash_command()
    async def fast_travel(
            self,
            inter: ApplicationCommandInteraction):
        """Use this to Fast Travel along the city"""
        # TODO: Add a check to see what keys the player has, and enter them.

        # and a list of approved characters you own
        me, characters = self.get_player_characters(inter.author)
        if not characters:
            await inter.send("**You currently have no characters use `/character add` or wait for an approval. "
                             "Characters take 1 minute from approvals to be ready**", ephemeral=True)

        # get the current districts from the server to list as options
        districts = [r for r in inter.guild.roles if r.name.startswith("d:")]

        # Create the view containing our dropdown
        view = FastTravelView(districts, characters)

        # Sending a message containing our view
        await inter.send("Fast Travel to where?", view=view, ephemeral=True)
        # await inter.response.defer()

def setup(bot):
    bot.add_cog(NavigatorCommands(bot))