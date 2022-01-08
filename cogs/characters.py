from disnake.ext import commands
from disnake import ApplicationCommandInteraction, RawReactionActionEvent, Message, Member
from utils.kerna_classes import Character, Approval, Player
from utils.characters import CharacterChooseView
from utils.help import Menu
from config import ENTRY_POINTS, APPROVAL_REACTION, DENIAL_REACTION, DEFAULT_PC_AVATAR
from typing import List



class SetupCharacter(commands.Cog, name='Setup Character'):

    def __init__(self, bot):
        self.bot = bot

    def get_player_characters(self, author: Member) -> (Player, List[Character]):
        me: Player = [player for player in self.bot.players if player.member.id == author.id][0]
        characters = [character for character in me.characters if character.approved]
        return me, characters

    @commands.slash_command()
    async def character(self, inter: ApplicationCommandInteraction):
        """ Commands dealing with player characters"""
        # this check is for the message listener to make sure the same person responds
        self.m_check = lambda m: inter.author == m.author
        pass

    # TODO: Add a check for a limit on characters? We haven't decided yet I guess
    @character.sub_command()
    async def add(
            self,
            inter: ApplicationCommandInteraction,
            name: str,
            backstory: str,
            prefix: str,
            entry_point: ENTRY_POINTS,
            avatar: str = DEFAULT_PC_AVATAR):
        """ Command to register a new Player Character

        Parameters
        ----------
        inter: message interaction
        name: Full name of your character
        backstory: Your tragic backstory
        prefix: this is what you will use to talk as your character, Tupperbox style.
        entry_point: The point where you will start your RP, depends on your backstory
        avatar: URL to an image you want to use as the player avatar
        """
        # Get the player object from the cache
        player = [player for player in self.bot.players if player.member.id == inter.author.id][0]
        entry_point = inter.guild.get_role(int(entry_point))

        # Make a character object and add it to the player object
        new_char = Character(player=inter.author,
                             name=name.title(),
                             backstory=backstory,
                             avatar=avatar,
                             prefix=prefix,
                             location=entry_point,
                             )
        player.add_character(new_char)

        # Create a new approval and save it to the queue
        new_approval = Approval(character=new_char)
        self.bot.pending_approvals.append(new_approval)

        # sends confirmation to the player and approval embed to the approval channel
        await inter.send(embeds=new_approval.embed, ephemeral=True)
        await inter.bot.APPROVAL_CHANNEL.send(embeds=new_approval.embed)

    @character.sub_command()
    async def list(self, inter: ApplicationCommandInteraction):
        """ List all of your approved characters"""
        e = []

        me, characters = self.get_player_characters(inter.author)

        if not characters:
            await inter.send("**You currently have no characters use `/character add` or wait for an approval. "
                             "Characters take 1 minute from approvals to be ready**", ephemeral=True)
            return
        # pull all the embeds from each character and send them back
        for character in characters:
            e.append(character.embed()) if character.approved else 0
        e[0].set_footer(text=f"Kerna - Path of the Wicked | Page 1 of {len(e)}")
        await inter.send(embed=e[0], view=Menu(e), ephemeral=True)

    @character.sub_command()
    async def edit(self,
                   inter: ApplicationCommandInteraction):
        """ Edit a part of your approved character """
        # get a list of your characters
        me, characters = self.get_player_characters(inter.author)
        if not characters:
            await inter.send("**You currently have no characters use `/character add` or wait for an approval. "
                             "Characters take 1 minute from approvals to be ready**", ephemeral=True)
            return

        # calls the View to display the selections
        view = CharacterChooseView(characters, "edit")
        await inter.send(content="Character Editor", view=view, ephemeral=True)
        await view.wait()

        # awaits for the new values
        msg: Message = await self.bot.wait_for('message', check=self.m_check)
        await msg.delete()

        # makes the changes
        view.character.update(view.attribute, msg.content)

        await inter.edit_original_message(view=None, embeds=[view.character.embed()])

    @character.sub_command()
    async def delete(self, inter: ApplicationCommandInteraction):
        """ Delete a character """
        # get a list of your characters
        me, characters = self.get_player_characters(inter.author)

        if not characters:
            await inter.send("**You currently have no characters use `/character add` or wait for an approval. "
                             "Characters take 1 minute from approvals to be ready**", ephemeral=True)
            return

        # calls the View to display the selections
        view = CharacterChooseView(characters, "delete")
        await inter.send(content="Delete a Character", view=view, ephemeral=True)
        await view.wait()

        # makes the changes, moves character to delete queue and removes that location
        self.bot.character_delete_queue.append(me.delete_character(self.view.character))
        if view.character.location not in [character.location for character in me.characters]:
            await me.member.remove_roles(view.character.location)
        await inter.edit_original_message(content=f'`{view.character.name}` has been deleted!', view=None)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: RawReactionActionEvent):
        """ Listens for a thumbs up in the #approvals channel,
        adds their starting role and removes the new player role """
        # checks to make sure that only thumbs up or down in the correct channel
        if payload.channel_id == self.bot.APPROVAL_CHANNEL.id and payload.emoji in [APPROVAL_REACTION, DENIAL_REACTION]:
            msg: Message = self.bot.get_message(payload.message_id)

            # the approvee is the character who submitted for approval
            approvee = msg.embeds[0].footer.text.split("|")[0]

            # pulls the approval from the queue
            approval = [approval for approval in self.bot.pending_approvals if approval.character.name == approvee][0]
            approval.process_approval(payload)

            # remove it from the queue
            self.bot.pending_approvals.pop(self.bot.pending_approvals.index(approval))
            if approval.approved:
                await approval.character.player.add_roles(approval.character.location)
                await approval.character.player.remove_roles(self.bot.NEW_PLAYER_ROLE)
            else:
                self.bot.character_delete_queue.append(approval.character)


            await msg.edit(embeds=approval.embed)


def setup(bot):
    bot.add_cog(SetupCharacter(bot))
