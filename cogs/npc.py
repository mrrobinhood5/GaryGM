from disnake.ext import commands
from disnake import ApplicationCommandInteraction, Member
from utils.npc import DEFAULT_NPC_AVATAR, Npc


class NpcCommands(commands.Cog, name='NPCs'):

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command()
    async def npc(self, inter: ApplicationCommandInteraction):
        """ Commands for creation and maintenance of NPCs"""
        pass

    @npc.sub_command()
    async def new(self,
                  inter: ApplicationCommandInteraction,
                  name: str,
                  prefix: str,
                  avatar: str = DEFAULT_NPC_AVATAR):
        """ Add a new NPC

        Parameters
        ----------
        inter: message interaction
        name: Full name of the NPC
        prefix: the prefix of the NPC
        avatar: the URL of the picture
        """

        d = {
            'name': name.title(),
            'prefix': prefix,
            'avatar': avatar,
            'owner': inter.author
        }

        me = Npc(inter, d)
        me.save()
        await inter.send(embeds=[me.embed()], ephemeral=True)
        pass

    @npc.sub_command()
    async def list(self, inter:ApplicationCommandInteraction):
        """ List NPCs you can command"""
        pass

    @npc.sub_command()
    async def share(self, inter: ApplicationCommandInteraction, member: Member):
        """ Authorize another DM to this NPC"""
        pass


def setup(bot):
    bot.add_cog(NpcCommands(bot))
