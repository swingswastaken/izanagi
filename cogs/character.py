import discord
from discord import app_commands
from discord.ext import commands

from services.characters import submit_character_service
from services.characters import approve_character_service
from services.characters import reject_character_service

class CharacterApprovalView(discord.ui.View):
    def __init__(self, pending_id: int):
        super().__init__(timeout=None)
        self.pending_id = pending_id

    async def disable_buttons(self, interaction: discord.Interaction):
        for item in self.children:
            item.disabled = True
        await interaction.message.edit(view=self)

    @discord.ui.button(label="Approve", style=discord.ButtonStyle.success)
    async def approve(self, interaction: discord.Interaction, button: discord.ui.Button):

        success, result = approve_character_service(self.pending_id)

        if not success:
            await interaction.response.send_message(result, ephemeral=True)
            return

        await self.disable_buttons(interaction)

        await interaction.response.send_message("Character approved.", ephemeral=True)

    @discord.ui.button(label="Reject", style=discord.ButtonStyle.danger)
    async def reject(self, interaction: discord.Interaction, button: discord.ui.Button):

        success, result = reject_character_service(self.pending_id)

        if not success:
            await interaction.response.send_message(result, ephemeral=True)
            return

        await self.disable_buttons(interaction)

        await interaction.response.send_message("Character rejected.", ephemeral=True)

class Step2TriggerView(discord.ui.View):
    def __init__(self, bot, partial_data):
        super().__init__(timeout=60)
        self.bot = bot
        self.partial_data = partial_data

    @discord.ui.button(label="Enter Background Info", style=discord.ButtonStyle.primary)
    async def trigger_step2(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(CharacterCreateModalStep2(self.bot, self.partial_data))

class CharacterCreateModalStep2(discord.ui.Modal, title="Create Character (2/2)"):

    appearance = discord.ui.TextInput(label="Appearance", style=discord.TextStyle.paragraph, max_length=1000)
    personality = discord.ui.TextInput(label="Personality", style=discord.TextStyle.paragraph, max_length=1000)
    backstory = discord.ui.TextInput(label="Backstory", style=discord.TextStyle.paragraph, max_length=2000)

    def __init__(self, bot, partial_data):
        super().__init__()
        self.bot = bot
        self.partial_data = partial_data

    async def on_submit(self, interaction: discord.Interaction):

        success, result = submit_character_service(
            user_id=str(interaction.user.id),
            name=self.partial_data["name"],
            race=self.partial_data["race"],
            age=int(self.partial_data["age"]),
            gender=self.partial_data["gender"],
            appearance=self.appearance.value,
            personality=self.personality.value,
            backstory=self.backstory.value,
            image_url=self.partial_data["image_url"],
        )

        if not success:
            await interaction.response.send_message(result, ephemeral=True)
            return

        await interaction.response.send_message(
            f"Character **{result['name']}** submitted for review.",
            ephemeral=True
        )

class CharacterCreateModalStep1(discord.ui.Modal, title="Create Character (1/2)"):

    name = discord.ui.TextInput(label="Name", max_length=20)
    race = discord.ui.TextInput(label="Race", max_length=20)
    age = discord.ui.TextInput(label="Age", max_length=5)
    gender = discord.ui.TextInput(label="Gender", max_length=20)
    image_url = discord.ui.TextInput(label="Image URL", required=False)

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction):
        # Save the partial data in a temporary storage (a dict in your Cog)
        # For this example, we just send a message with a button
        
        data = {
            "name": self.name.value,
            "race": self.race.value,
            "age": self.age.value,
            "gender": self.gender.value,
            "image_url": self.image_url.value or "",
        }

        # Send a followup message with a button to open the 2nd Modal
        # We need a View that contains a button to trigger Step 2
        view = Step2TriggerView(self.bot, data)
        await interaction.response.send_message(
            "Basic info saved! Click the button below to finish your character.", 
            view=view, 
            ephemeral=True
        )

class Character(commands.GroupCog, name="character"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="create", description="Create a new character.")
    async def create(self, interaction: discord.Interaction):
        await interaction.response.send_modal(CharacterCreateModalStep1(self.bot))

async def setup(bot: commands.Bot):
    await bot.add_cog(Character(bot))