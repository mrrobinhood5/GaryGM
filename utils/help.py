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
        role = self.guild.get_role(921113949691334706)
        await me.add_roles(role)
        await inter.response.edit_message(
            content="**You now have view access to the server until you create a Character.**", view=None)

    @disnake.ui.button(label="No, Thank you", style=ButtonStyle.red)
    async def disagree(self, button: disnake.ui.Button, inter: MessageInteraction):
        await inter.response.edit_message(
            content="**We're sorry you feel this way. Maybe we can talk it out in <#920857756649545770> :)**",
            view=None)


def create_help_pages():
    # get them from the database
    embeds = []
    db = [{"title": "Server Rules",
           "description": "Rules for everyone on the server.",
           "thumbnail": "https://i.imgur.com/0102Ab8.png",
           "footer": "Kerna - Path of the Wicked",
           "fields": [("Be Respectful", "Treat other members how you wish to be treated. The one golder rule."),
                      ("Griefing and Harassment",
                       "Griefing is the act of chronically causing consternation to other members and distrubing their immersion.\nBoth apply in and out of character"),
                      ("Racism, Bigotry, Discrimination",
                       "No discriminating against real world races, genders, sexuality, conditions, or social status. This will be an instant ban."),
                      ("Enjoy Yourself!", "The purpose of this server is to play D&D with others and have fun.")]},
          {"title": "Game Rules",
           "description": "Rules specific to the game",
           "thumbnail": "https://i.imgur.com/0102Ab8.png",
           "fields": [("Sources", "We only use official 5e sources. No Homebrew or Playtest materials"),
                      ("Sheets", "We use Avrae which takes DnD Beyond, GSheetv2, or Dicecloud"),
                      ("Starting a Character",
                       "Your first character will be level 3 or below, unlock a second character at level 5 (can start at level 5), but your backstory should match your level.\nUse point-buy or standard array for your stats, and fixed HP progression"),
                      ("RAW", "Unless otherwise stated by a DM on quest, we follow RAW as close as possible"),
                      ("DM", "As in a real table, DM has final say so on adjudication.")]},
          {"title": "Quickstart",
           "description": "A quick step by step",
           "thumbnail": "https://i.imgur.com/0102Ab8.png",
           "fields": [("First things Fist", "Stop by and say hello to everyone in <#920857756649545770>"),
                      ("Load and Configure",
                       "Channel <#922721043917987930> is used to load and configure. `!initial` command will have a step by step"),
                      ("~TupperBot and RP alias~",
                       "Channel <#923433287890919424> is used to load and configure your Tupper bot for RPing. `tul!help` has more info"),
                      ("Character Setup", "Submit your backstory, character name and image to `/character add`"),
                      ("Points of Entry", "You can start RP in either the #north-gate or the #docks"),
                      ("Fast Travel",
                       "You can only see channel categories where you have characters. You can always `/fast_travel`")]}]
    for entry in db:
        embed = Embed(title=entry['title'], description=entry['description'], color=Color.random())
        embed.set_thumbnail(url=entry['thumbnail'])
        for field in entry['fields']:
            embed.add_field(name=field[0], value=field[1], inline=False)
        embeds.append(embed)
    return embeds
