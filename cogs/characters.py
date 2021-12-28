from disnake.ext import commands
from disnake import ApplicationCommandInteraction, RawReactionActionEvent, PartialEmoji, Member, Message, Role
from utils.characters import Player, EntryPoint, Approval
from utils.help import Menu
from config import APPROVAL_CHANNEL, APPROVAL_REACTION, NEW_PLAYER_ROLE


class SetupCharacter(commands.Cog, name='Setup Character'):

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command()
    async def character(self, inter: ApplicationCommandInteraction):
        """ Commands dealing with player characters"""
        pass

    @character.sub_command()
    async def add(
            self,
            inter: ApplicationCommandInteraction,
            name: str,
            backstory: str,
            prefix: str,
            entry_point: EntryPoint,
            avatar: str = None):
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
            'avatar': 'https://i.imgur.com/v47ed3Y.jpg',
            'backstory': backstory,
            'keys': [],
            'location': entry_point,
            'prefix': prefix
        }

        me = Player(inter, d)
        me.save()
        await inter.send(embeds=[me.request_approval()], ephemeral=True)
        await inter.guild.get_channel(APPROVAL_CHANNEL).send(embeds=[me.request_approval()])

    @character.sub_command()
    async def list(self, inter: ApplicationCommandInteraction):
        """ List all of your approved characters"""
        f = {"player": str(inter.author.id)}
        e = []
        characters = self.bot.db.players.find(f)
        async for char in characters:
            p = Player(inter, char)
            e.append(p.embed())
        e[0].set_footer(text=f"Kerna - Path of the Wicked | Page 1 of {len(e)}")
        await inter.send(embed=e[0], view=Menu(e), ephemeral=True)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: RawReactionActionEvent):
        """ Listens for a thumbs up in the #approvals channel,
        adds their starting role and removes the new player role """
        if payload.channel_id == APPROVAL_CHANNEL and payload.emoji == PartialEmoji(name=APPROVAL_REACTION):
            # fetches ass the required instances of message, and roles
            msg: Message = self.bot.get_message(payload.message_id)
            # runs the approval through the DB.
            approval = Approval(self.bot.db, msg, payload)

            role: Role = self.bot.guilds[0].get_role(int(approval.role_id))
            new_player_role: Role = self.bot.guilds[0].get_role(NEW_PLAYER_ROLE)
            approvee: Member = self.bot.guilds[0].get_member(int(approval.player_id))

            # Changes the embed to approved
            await msg.edit(embeds=approval.get_embed())
            await approvee.add_roles(role)
            await approvee.remove_roles(new_player_role)


def setup(bot):
    bot.add_cog(SetupCharacter(bot))
