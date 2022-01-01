from disnake import SelectOption, MessageInteraction, Member
from disnake.ui import Select, View, select
from typing import List


# Defines a custom Select containing colour options
# that the user can choose. The callback function
# of this class is called when the user changes their choice
class DistrictsDropdown(Select):
    def __init__(self, districts):
        options = []
        for district in districts:
            options.append(SelectOption(label=district[0], description="", value=district[1]))

        super().__init__(placeholder="Choose a location", min_values=1, max_values=1, options=options)

    async def callback(self, inter: MessageInteraction):
        self.disabled = True
        district_role = inter.guild.get_role(int(self.values[0]))
        m = f"`{self.view.character.character}` has traveled to `{district_role.name.lstrip('d: ')}`"
        # change the players location and save it to db
        await self.view.character.fast_travel(district_role)
        # the ephemeral message
        await inter.response.edit_message(content=m, view=self.view)
        # the tracker message
        await inter.guild.get_channel(inter.channel_id).send(m)


class CharactersDropdown(Select):
    def __init__(self, characters):
        options = []
        for character in characters:
            options.append(SelectOption(label=character.character, description="", value=character.character))

        super().__init__(
            placeholder="Choose a character",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, inter: MessageInteraction):
        await inter.response.defer()
        self.view.character = [x for x in self.view.characters if x.character == self.values[0]][0]
        if inter.channel not in [x for x in self.view.character.channels]:
            await inter.edit_original_message(content=f'`{self.values[0]}` is not in this disctrict')
            return

        self.placeholder = self.values[0]
        self.disabled = True
        # remove your players district from the list
        self.view.districts = [x for x in self.view.districts if x[1] != str(self.view.character.location.id)]
        self.view.add_item(DistrictsDropdown(self.view.districts))

        await inter.edit_original_message(view=self.view)


class FastTravelView(View):
    def __init__(self, districts: List[tuple], PCs: List[Member]):
        self.characters = PCs
        self.districts = districts
        super().__init__()

        # Adds the dropdown to our view object.
        self.add_item(CharactersDropdown(PCs))
