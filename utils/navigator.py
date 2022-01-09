from disnake import SelectOption, MessageInteraction, Role
from disnake.ui import Select, View
from utils.kerna_classes import Character
from typing import List


# Defines a custom Select containing colour options
# that the user can choose. The callback function
# of this class is called when the user changes their choice
class DistrictsDropdown(Select):
    def __init__(self, districts):
        options = []
        for district in districts:
            options.append(SelectOption(label=district.name, description="", value=district.id))

        super().__init__(placeholder="Choose a location", min_values=1, max_values=1, options=options)

    async def callback(self, inter: MessageInteraction):
        self.disabled = True

        # get the role object of where your are going to
        destination = inter.guild.get_role(int(self.values[0]))

        # msg = f"`{self.view.character.name}` has traveled to `{district_role.name.lstrip('d: ')}`"
        # change the players location and save it to db
        msg = await self.view.character.fast_travel(destination)
        # the ephemeral message
        await inter.response.edit_message(content=msg, view=self.view)
        # the tracker message
        await inter.guild.get_channel(inter.channel_id).send(msg)

        self.view.stop()


class CharactersDropdown(Select):
    def __init__(self, characters):
        options = []
        for character in characters:
            options.append(SelectOption(label=character.name, description="", value=character.name))

        super().__init__(
            placeholder="Choose a character",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, inter: MessageInteraction):
        await inter.response.defer()
        self.placeholder = self.values[0]
        self.disabled = True

        # store the chosen character
        self.view.character = [x for x in self.view.characters if x.name == self.values[0]][0]

        # check to see if tha character is even in this district
        if inter.channel not in self.view.character.channels:
            await inter.edit_original_message(content=f'`{self.values[0]}` is not in this disctrict', view=None)
            self.view.stop()
            return
        # else:
        #     await inter.edit_original_message(content="Character IS supposed to be here")

        # remove your players district from the list
        self.view.districts = [x for x in self.view.districts if x.name != self.view.character.location.name]

        self.view.add_item(DistrictsDropdown(self.view.districts))

        await inter.edit_original_message(view=self.view)


class FastTravelView(View):
    def __init__(self, districts: List[Role], characters: List[Character]):
        self.characters = characters
        self.districts = districts
        super().__init__()

        # Adds the dropdown to our view object.
        self.add_item(CharactersDropdown(characters))
