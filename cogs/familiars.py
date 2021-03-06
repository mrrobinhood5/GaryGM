from disnake.ext import commands
from disnake import ApplicationCommandInteraction, Member
from utils.player import Player
from utils.characters import Character, CharacterFamiliar, CharacterVariant
from utils.characters import CharacterChooseView

from config import DEFAULT_FAM_AVATAR
from typing import List


# TODO add variants and familiars
class FamiliarCommands(commands.Cog, name='Familiar Commands'):

    def __init__(self, bot):
        self.bot = bot

    def get_player_characters(self, author: Member) -> (Player, List[Character]):
        me: Player = [player for player in self.bot.players if player.member.id == author.id][0]
        characters = [character for character in me.characters if character.approved]
        return me, characters

    @commands.slash_command()
    async def familiar(self, inter: ApplicationCommandInteraction):
        pass

    @familiar.sub_command()
    async def add(self,
                  inter: ApplicationCommandInteraction,
                  name: str,
                  prefix: str,
                  avatar: str = DEFAULT_FAM_AVATAR):
        """ Command to add a new familiar

        Parameters
        ----------
        inter: message interaction
        name: Full name of your Familiar
        prefix: prefix to append for RP,
        avatar: URL for the Familiar's avatar
        """
        # Need to know which character this will go to
        me, characters = self.get_player_characters(inter.author)
        view = CharacterChooseView(characters, "familiar")

        await inter.send(content="This will belong to which Character?", view=view, ephemeral=True)
        await view.wait()
        familiar = CharacterFamiliar(character=view.character, name=name.title(), prefix=prefix.rstrip(":"), avatar=avatar)

        view.character.add_familiar(familiar)
        await inter.edit_original_message(content="Added new familiar", view=None, embeds=[familiar.embed])
        await inter.bot.CHANGE_LOG_CHANNEL.send(content=f'`{view.character.name}` added familiar `{familiar.name}`')

    @commands.slash_command()
    async def variant(self, inter: ApplicationCommandInteraction):
        pass

    @variant.sub_command()
    async def add(self,
                  inter: ApplicationCommandInteraction,
                  name: str,
                  prefix: str,
                  avatar: str):
        """ Command to add a new familiar

        Parameters
        ----------
        inter: message interaction
        name: Full name of your Familiar
        prefix: prefix to append for RP,
        avatar: URL for the Familiar's avatar
        """
        # Need to know which character this will go to
        me, characters = self.get_player_characters(inter.author)
        view = CharacterChooseView(characters, "variant")

        await inter.send(content="This is a variant of which Character?", view=view, ephemeral=True)
        await view.wait()
        variant = CharacterVariant(character=view.character, name=name.title(), prefix=prefix.rstrip(":"), avatar=avatar)

        view.character.add_variant(variant)
        await inter.edit_original_message(content="Added new variant", view=None, embeds=[variant.embed])
        await inter.bot.CHANGE_LOG_CHANNEL.send(content=f'`{view.character.name}` added familiar `{variant.name}`')

def setup(bot):
    bot.add_cog(FamiliarCommands(bot))
