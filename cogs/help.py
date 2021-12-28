from disnake.ext import commands
from disnake import ApplicationCommandInteraction, Member
from utils.help import Menu, create_help_pages, Agreement


class Help(commands.Cog, name='Help'):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def omj(self, ctx, member: Member):
        """Quick Reference Welcome"""

        # Creates the embeds as a list.
        embeds = create_help_pages()

        # Sets the footer of the first embed.
        embeds[0].set_footer(text=f"Kerna - Path of the Wicked | Page 1 of {len(embeds)}")
        embeds[0].set_thumbnail(url="https://i.imgur.com/0102Ab8.png")
        # Sends first embed with the buttons, it also passes the embeds list into the View class.
        # await inter.send(embed=embeds[0], view=Menu(embeds), ephemeral=True)
        if not member.dm_channel:
            await member.create_dm()

        await member.dm_channel.send(embeds=[embeds[0]], view=Menu(embeds))
        await member.dm_channel.send(content="Once you have read all the rules click below", view=Agreement(ctx.guild))


    @commands.slash_command()
    async def help(self,
                   inter: ApplicationCommandInteraction):
        """Quick Reference Help"""
        # Creates the embeds as a list.
        embeds = create_help_pages()

        # Sets the footer of the first embed.
        embeds[0].set_footer(text=f"Kerna - Path of the Wicked | Page 1 of {len(embeds)}")


        await inter.send(embed=embeds[0], view=Menu(embeds), ephemeral=True)


def setup(bot):
    bot.add_cog(Help(bot))

