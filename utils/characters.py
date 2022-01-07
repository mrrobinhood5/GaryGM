from disnake import SelectOption, MessageInteraction, ButtonStyle
from disnake.ui import View, Select, Button
from utils.kerna_classes import Character
from typing import List

class CharacterDeleteConfirm(Button):
    def __init__(self):
        super().__init__(
            label="Are you Sure?",
            style=ButtonStyle.red
        )

    async def callback(self, inter: MessageInteraction):
        self.view.stop()

class CharacterAttributeDropdown(Select):
    def __init__(self):
        options = [SelectOption(label="Name", description="", value="name"),
                   SelectOption(label="Backstory", description="", value="backstory"),
                   SelectOption(label="Prefix", description="", value="prefix"),
                   SelectOption(label="Avatar", description="", value="avatar")]
        super().__init__(
            placeholder="Choose an attribute",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, inter: MessageInteraction):
        await inter.response.defer()
        # add the attribute - attribute to the view
        self.view.attribute = self.values[0]

        # update the view and return
        await inter.edit_original_message(content=f"What is the new value for `{self.values[0]}`", view=None)
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
        # add a character attribute to the view
        self.view.character = [x for x in self.view.characters if x.name == self.values[0]][0]

        # clean up the interaction
        self.placeholder = self.values[0]
        self.disabled = True

        # choose what action is gonna happen
        if self.view.action == "edit":
            self.view.add_item(CharacterAttributeDropdown())
        elif self.view.action == "delete":
            self.view.add_item(CharacterDeleteConfirm())

        await inter.edit_original_message(view=self.view)


class CharacterChooseView(View):
    def __init__(self, characters: List[Character], action: str):
        self.characters = characters
        self.action = action
        super().__init__()

        # Adds the dropdown to our view object.
        self.add_item(CharactersDropdown(characters))

