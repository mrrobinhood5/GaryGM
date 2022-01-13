from disnake import SelectOption, MessageInteraction, Role
from disnake.ui import Select, View
from utils.kerna_classes import Character
from typing import List


class KeysDrowndown(Select):
    def __init__(self, keys):
        options = []
        for key in keys:
            options.append(SelectOption(label=key.name, description="", value=key.id))

        super().__init__(placeholder="Choose a Key", min_values=1, max_values=1, options=options)

    async def callback(self, inter: MessageInteraction):
        self.disabled = True

        # get the role object of where your are going to
        key = inter.guild.get_role(int(self.values[0]))
        self.view.key = key

        await inter.response.edit_message(content=f"The Key: `{key.name}`, has been given to {self.view.character.name}", view=self.view)
        # the tracker message
        await inter.guild.get_channel(inter.channel_id).send(f'`{self.view.character.name}` has received the `{key.name}` key')
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
        self.view.add_item(KeysDrowndown(self.view.keys))

        await inter.edit_original_message(view=self.view)


class DMGiveKeys(View):
    def __init__(self, characters: List[Character], keys: List[Role]):
        self.characters = characters
        self.keys = keys
        super().__init__()

        # Adds the dropdown to our view object.
        self.add_item(CharactersDropdown(characters))
