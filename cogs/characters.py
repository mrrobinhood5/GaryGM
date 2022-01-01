from disnake.ext import commands
from disnake import ApplicationCommandInteraction, RawReactionActionEvent, PartialEmoji, Member, Message, Role
from utils.characters import Player, EntryPoint, Approval, DEFAULT_PC_AVATAR
from utils.help import Menu
from config import APPROVAL_REACTION, DENIAL_REACTION


class SetupCharacter(commands.Cog, name='Setup Character'):

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command()
    async def character(self, inter: ApplicationCommandInteraction):
        """ Commands dealing with player characters"""
        pass

    # TODO: Add a check for a limit on characters? We havent decided yet I guess
    @character.sub_command()
    async def add(
            self,
            inter: ApplicationCommandInteraction,
            name: str,
            backstory: str,
            prefix: str,
            entry_point: EntryPoint,
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
        # build the dict to generate the Player instance from
        d = {
            'character': name.title(),
            'player': str(inter.author.id),
            'approved': False,
            'avatar': avatar,
            'backstory': backstory,
            'keys': [],
            'location': entry_point,
            'prefix': prefix
        }

        me = Player(d)
        me.save()
        # sends confirmation to player
        await inter.send(embeds=[me.request_approval()], ephemeral=True)
        # sends approval request to APPROVAL_CHANNEL
        await inter.bot.APPROVAL_CHANNEL.send(embeds=[me.request_approval()])

    @character.sub_command()
    async def list(self, inter: ApplicationCommandInteraction):
        """ List all of your approved characters"""
        e = []
        for char in self.bot.character_cache:
            e.append(char.embed())
        e[0].set_footer(text=f"Kerna - Path of the Wicked | Page 1 of {len(e)}")
        await inter.send(embed=e[0], view=Menu(e), ephemeral=True)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: RawReactionActionEvent):
        """ Listens for a thumbs up in the #approvals channel,
        adds their starting role and removes the new player role """
        # match the APPROVAL
        if payload.channel_id == self.bot.APPROVAL_CHANNEL.id and payload.emoji in [APPROVAL_REACTION, DENIAL_REACTION]:
            # fetches the required instances of message, and roles
            msg: Message = self.bot.get_message(payload.message_id)
            # runs the approval through the DB.
            approval = Approval(msg, payload)

            # role: Role = self.bot.guilds[0].get_role(int(approval.role.id))

            # new_player_role: Role = self.bot.guilds[0].get_role(NEW_PLAYER_ROLE)
            # approvee: Member = self.bot.guilds[0].get_member(int(approval.player.id))

            # Changes the embed to approved
            await approval.process_character()
            await msg.edit(embeds=approval.get_embed())
            # Adds the entry point role to the Player
            # await approvee.add_roles(approval.role)
            # Removes the New Player Role if any, otherwise it doesnt do nothing
            # await approvee.remove_roles(self.bot.NEW_PLAYER_ROLE)


def setup(bot):
    bot.add_cog(SetupCharacter(bot))
