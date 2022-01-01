import disnake
from typing import List
from disnake import Color, Embed, Guild, ButtonStyle, MessageInteraction


class Menu(disnake.ui.View):
    def __init__(self, embeds: List[disnake.Embed]):
        super().__init__(timeout=None)

        # Sets the embed list variable.
        self.embeds = embeds

        # Current embed number.
        self.embed_count = 0

    @disnake.ui.button(label="Previous page", emoji="◀️", style=ButtonStyle.blurple)
    async def next_page(self, button: disnake.ui.Button, interaction: MessageInteraction):
        if self.embed_count == 0:  # If current embed is the first embed then, do not do anything.
            pass
        else:  # If current embed is not the first embed then, sends the preview embed.
            self.embed_count -= 1

            # Gets the embed object.
            embed = self.embeds[self.embed_count]

            # Sets the footer of the embed with current page and then sends it.
            embed.set_footer(text=f"Kerna - Path of the Wicked | Page {self.embed_count + 1} of {len(self.embeds)}")
            await interaction.response.edit_message(embed=embed)

    @disnake.ui.button(label="Next page", emoji="▶️", style=ButtonStyle.blurple)
    async def last_page(self, button: disnake.ui.Button, interaction: MessageInteraction):
        if self.embed_count == (
                len(self.embeds) - 1
        ):  # If current embed is the last embed then, do not do anything.
            pass
        else:  # If current embed is not the last embed then, sends the next embed.
            self.embed_count += 1

            # Gets the embed object.
            embed = self.embeds[self.embed_count]

            # Sets the footer of the embed with current page and then sends it.
            embed.set_footer(text=f"Kerna - Path of the Wicked | Page {self.embed_count + 1} of {len(self.embeds)}")
            await interaction.response.edit_message(embed=embed)


class Agreement(disnake.ui.View):
    def __init__(self, guild: Guild):
        self.guild = guild
        super().__init__(timeout=None)

    @disnake.ui.button(label="I Agree", style=ButtonStyle.green)
    async def agree(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        me = self.guild.get_member(inter.author.id)
        # TODO: Add New Player Role to bot
        role = self.guild.get_role(921113949691334706)
        await me.add_roles(role)
        await inter.response.edit_message(
            content="**You now have view access to the server until you create a Character.**", view=None)

    @disnake.ui.button(label="No, Thank you", style=ButtonStyle.red)
    async def disagree(self, button: disnake.ui.Button, inter: MessageInteraction):
        await inter.response.edit_message(
            content="**We're sorry you feel this way. Maybe we can talk it out in <#920857756649545770> :)**",
            view=None)


# TODO: Move the help pages to DB and make a way to add/edit
def create_help_pages(inter):
    embeds = []
    help_pages = inter.bot.help_pages

    for entry in help_pages:
        embed = Embed(title=entry['title'], description=entry['description'], color=Color.random())
        embed.set_thumbnail(url=entry['thumbnail'])
        for field in entry['fields']:
            embed.add_field(name=field[0], value=field[1], inline=False)
        embeds.append(embed)
    return embeds



