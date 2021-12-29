import disnake
from disnake.ext import commands

# Defines a custom Select containing colour options
# that the user can choose. The callback function
# of this class is called when the user changes their choice
class Dropdown(disnake.ui.Select):
    def __init__(self):
        # TODO: grab these from the DB instead of hard code
        # Set the options that will be presented inside the dropdown
        options = [
            disnake.SelectOption(
                label="Docks District", description="If your character is traveling into the city by sea.", emoji="🟥",
                value='922262282539507752'),
            disnake.SelectOption(
                label="North Market Gate", description="Buy things and or another", emoji="🟩",
                value='922262406317633536'),
            disnake.SelectOption(
                label="Slums", description="Make sure you use protection", emoji="🟦",
                value='922262527587532830'),
        ]

        # The placeholder is what will be shown when no option is chosen
        # The min and max values indicate we can only pick one of the three options
        # The options parameter defines the dropdown options. We defined this above
        super().__init__(
            placeholder="Fast travel where?",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: disnake.MessageInteraction):
        # Use the interaction object to send a response message containing
        # the user's favourite colour or choice. The self object refers to the
        # Select object, and the values attribute gets a list of the user's
        # selected options. We only want the first one.
        district_role = interaction.guild.get_role(int(self.values[0]))
        roles_to_remove = [int(x.value) for x in self.options if x.value != self.values[0]]
        for r in roles_to_remove:
            await interaction.author.remove_roles(interaction.guild.get_role(r))
        await interaction.author.add_roles(district_role)
        me = interaction.author.name
        await interaction.response.edit_message(content=f'{me} has traveled to {district_role.name}')


class DropdownView(disnake.ui.View):
    def __init__(self):
        super().__init__()

        # Adds the dropdown to our view object.
        self.add_item(Dropdown())
