from __future__ import annotations
from disnake.ext import commands
from disnake.ext.commands import option_enum
from disnake import ApplicationCommandInteraction, Member, Message
from utils.npc import DEFAULT_NPC_AVATAR, Npc
from utils.player import Player
from utils.help import Menu
from utils.characters import CharacterChooseView

SHARED = option_enum({"Yes": 1, "No": 0})


def is_a_dm():
    async def predicate(ctx):
        return any([any([r == y for r in ctx.bot.ALL_DM_ROLES]) for y in ctx.author.roles])

    return commands.check(predicate)


class NpcCommands(commands.Cog, name='NPCs'):

    def __init__(self, bot):
        self.bot = bot


    def get_player(self, author: Member) -> Player:
        me: Player = [player for player in self.bot.players if player.member.id == author.id][0]
        return me

    @commands.slash_command()
    async def npc(self, inter: ApplicationCommandInteraction):
        """ Commands for creation and maintenance of NPCs"""
        self.m_check = lambda m: inter.author == m.author
        pass

    @is_a_dm()
    @npc.sub_command()
    async def new(self,
                  inter: ApplicationCommandInteraction,
                  name: str,
                  prefix: str,
                  shared: SHARED,
                  description: str = '',
                  avatar: str = DEFAULT_NPC_AVATAR):
        """ Add a new NPC

        Parameters
        ----------
        inter: message interaction
        name: Full name of the NPC
        prefix: the prefix of the NPC
        description: Optional description of the NPC. Good idea if its shared
        avatar: the URL of the picture
        shared: Will this be a shared NPC for NPC DM
        """
        me = self.get_player(inter.author)
        d = {
            'name': name,
            'prefix': prefix,
            'avatar': avatar,
            'owner': me,
            'shared': shared,
            'description': description
        }
        npc = Npc(**d)
        if npc.shared:
            self.bot.shared_npcs.append(npc)
        else:
            me.add_npc(npc)
        await inter.bot.CHANGE_LOG_CHANNEL.send(
            content=f'`{inter.author.name} created the `{npc.name}` NPC')
        await inter.send(embeds=[npc.embed], ephemeral=True)

    @npc.sub_command()
    async def list(self, inter: ApplicationCommandInteraction):
        """ List all of your NPCs """
        e = []

        me = self.get_player(inter.author)

        if not me.npcs:
            await inter.send("**You currently have no NPCs use `/npc add`"
                             "NPCs take 1 minute to be ready", ephemeral=True)
            return
        # pull all the embeds from each character and send them back
        for npc in me.npcs:
            e.append(npc.embed)
        e[0].set_footer(text=f"Kerna - Path of the Wicked | Page 1 of {len(e)}")
        await inter.send(embed=e[0], view=Menu(e), ephemeral=True)

    @npc.sub_command()
    async def edit(self,
                   inter: ApplicationCommandInteraction):
        """ Edit a part of your npc """
        # get a list of your characters
        npcs = self.get_player(inter.author).npcs
        if not npcs:
            await inter.send("**You currently have no npcs use `/npc add`"
                             "NPCs take 1 minute to be ready**", ephemeral=True)
            return

        # calls the View to display the selections
        view = CharacterChooseView(npcs, "edit")
        await inter.send(content="NPC Editor", view=view, ephemeral=True)
        await view.wait()

        # awaits for the new values
        msg: Message = await self.bot.wait_for('message', check=self.m_check)
        await msg.delete()

        # makes the changes
        view.character.update(view.attribute, msg.content)
        await inter.edit_original_message(view=None, embeds=[view.character.embed])
        await inter.bot.CHANGE_LOG_CHANNEL.send(content=f'`{view.character.name}` changed `{view.attribute}` to `{msg.content}`')

    @npc.sub_command()
    async def delete(self, inter: ApplicationCommandInteraction):
        """ Delete an NPC """
        # get a list of your characters
        me = self.get_player(inter.author)
        npcs = me.npcs

        if not npcs:
            await inter.send("**You currently have no NPCS use `/npc add` or wait for an approval. "
                             "NPCs take 1 minute to be ready**", ephemeral=True)
            return

        # calls the View to display the selections
        view = CharacterChooseView(npcs, "delete")
        await inter.send(content="Delete an NPC", view=view, ephemeral=True)
        await view.wait()

        # makes the changes, moves character to delete queue and removes that location
        self.bot.character_delete_queue.append(me.delete_npc(view.character))
        await inter.edit_original_message(content=f'`{view.character.name}` has been deleted!', view=None)
        await inter.bot.CHANGE_LOG_CHANNEL.send(content=f'`NPC: {view.character.name}` has been deleted')

def setup(bot):
    bot.add_cog(NpcCommands(bot))
