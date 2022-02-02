from disnake.ext import commands
from disnake import Member, ApplicationCommandInteraction
from utils.player import Player
from utils.characters import Character
from typing import List
from utils.dm import DMGiveKeys


def is_quest_dm():
    async def predicate(ctx):
        return any([any([r == y for r in ctx.bot.QUEST_DM_ROLES]) for y in ctx.author.roles])
    return commands.check(predicate)


class DungeonMasterCommands(commands.Cog, name='DungeonMaster Commands'):

    def __init__(self, bot):
        self.bot = bot

    def get_player_characters(self, author: Member) -> (Player, List[Character]):
        me: Player = [player for player in self.bot.players if player.member.id == author.id][0]
        characters = [character for character in me.characters if character.approved]
        return me, characters

    @commands.slash_command()
    async def dm(self, inter: ApplicationCommandInteraction):
        """ Commands for DMs """
        pass

    @is_quest_dm()
    @dm.sub_command()
    async def give_key(self, inter: ApplicationCommandInteraction, player: Member):
        """ Gives a key to a Character """
        # get a player and characters from a Member
        if player.bot:
            await inter.send(content="**BRUH..** ||That's a bot, not a player||", ephemeral=True)
            return
        me, characters = self.get_player_characters(player)
        if not characters:
            await inter.send("**Player has no APPROVED characters.**", ephemeral=True)

        # Send a view to choose a character, then a list of available keys
        keys = [role for role in inter.guild.roles if role.name.startswith("k: ")]
        view = DMGiveKeys(characters, keys)

        await inter.send(content="Choose a Character to give keys to: ", view=view, ephemeral=True)

        await view.wait()

        view.character.add_key(view.key)


def setup(bot):
    bot.add_cog(DungeonMasterCommands(bot))
