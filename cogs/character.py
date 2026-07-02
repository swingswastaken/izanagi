import discord
from discord import app_commands
from discord.ext import commands

from services.characters import submit_character_service
from services.characters import approve_character_service
from services.characters import reject_character_service
from services.characters import get_user_characters_service
from services.characters import get_character_service

class CharacterApprovalView(discord.ui.View):
    def __init__(self, pending_id: int):
        super().__init__(timeout=None)
        self.pending_id = pending_id

    async def disable_buttons(self):
        for item in self.children:
            item.disabled = True

    @discord.ui.button(label="Approve", style=discord.ButtonStyle.success)
    async def approve(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            success, result = approve_character_service(self.pending_id)

            if not success:
                await interaction.response.send_message(result, ephemeral=True)
                return

            await self.disable_buttons()
            await interaction.response.edit_message(view=self)
            await interaction.followup.send(
                "Character approved.",
                ephemeral=True
            )

        except Exception as e:
            print(f"APPROVE ERROR: {e}")
            raise

    @discord.ui.button(label="Reject", style=discord.ButtonStyle.danger)
    async def reject(self, interaction: discord.Interaction, button: discord.ui.Button):

        success, result = reject_character_service(self.pending_id)

        if not success:
            await interaction.response.send_message(result, ephemeral=True)
            return

        await self.disable_buttons()
        await interaction.response.edit_message(view=self)
        await interaction.followup.send(
            "Character rejected.",
            ephemeral=True
        )

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
        try:
            # 1. Perform your service logic
            success, result = submit_character_service(
                user_id=str(interaction.user.id),
                username=interaction.user.name,
                name=self.partial_data["name"],
                race=self.partial_data["race"],
                age=int(self.partial_data["age"]), # Ensure this is a valid number
                gender=self.partial_data["gender"],
                appearance=self.appearance.value,
                personality=self.personality.value,
                backstory=self.backstory.value,
                image_url=self.partial_data["image_url"],
            )

            if not success:
                await interaction.response.send_message(result, ephemeral=True)
                return

            # 2. Logic to send the approval embed
            channel = await self.bot.fetch_channel(1522281815031808364)
            embed = discord.Embed(title=f"Character Submission: {result['name']}", color=discord.Color.orange())
            embed.add_field(name="User", value=f"<@{result['user_id']}>", inline=False)
            embed.add_field(name="Race", value=result["race"], inline=True)
            embed.add_field(name="Age", value=result["age"], inline=True)
            embed.add_field(name="Gender", value=result["gender"], inline=True)

            embed.add_field(name="Appearance", value=result["appearance"], inline=False)
            embed.add_field(name="Personality", value=result["personality"], inline=False)
            embed.add_field(name="Backstory", value=result["backstory"], inline=False)

            if result.get("image_url"):
                embed.set_image(url=result["image_url"])

            view = CharacterApprovalView(result["pending_id"])
            await channel.send(embed=embed, view=view)

            # 3. Respond to the interaction
            await interaction.response.send_message(
                f"Character **{result['name']}** submitted for review.",
                ephemeral=True
            )
            
        except Exception as e:
            # THIS IS THE CRITICAL LINE
            print(f"DEBUG ERROR: {e}") 
            # This will show you exactly what is failing in your terminal
            await interaction.response.send_message(f"An unexpected error occurred: {e}", ephemeral=True)

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

def build_character_embed(character):
        embed = discord.Embed(
            title=character["name"],
            color=discord.Color.blue()
        )

        embed.add_field(name="Race", value=character["race"], inline=True)
        embed.add_field(name="Age", value=character["age"], inline=True)
        embed.add_field(name="Gender", value=character["gender"], inline=True)

        embed.add_field(name="Rank", value=character["rank"], inline=True)
        embed.add_field(name="XP", value=character["xp"], inline=True)

        embed.add_field(
            name="Appearance",
            value=character["appearance"],
            inline=False
        )

        embed.add_field(
            name="Personality",
            value=character["personality"],
            inline=False
        )

        embed.add_field(
            name="Backstory",
            value=character["backstory"],
            inline=False
        )

        if character.get("image_url"):
            embed.set_image(url=character["image_url"])

        return embed

class CharacterSelect(discord.ui.Select):
    def __init__(self, bot, characters):
        self.bot = bot

        options = [
            discord.SelectOption(
                label=character["name"],
                value=str(character["character_id"])
            )
            for character in characters
        ]

        super().__init__(
            placeholder="Choose a character...",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        character_id = int(self.values[0])

        character = get_character_service(character_id)

        if not character:
            await interaction.response.send_message(
                "Character not found.",
                ephemeral=False
            )
            return

        embed = build_character_embed(character)

        await interaction.response.edit_message(
            content=None,
            embed=embed,
            view=None
        )

class CharacterSelectView(discord.ui.View):
    def __init__(self, bot, characters):
        super().__init__(timeout=60)

        self.add_item(
            CharacterSelect(bot, characters)
        )

class Character(commands.GroupCog, name="character"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="create", description="Create a new character.")
    async def create(self, interaction: discord.Interaction):
        await interaction.response.send_modal(CharacterCreateModalStep1(self.bot))

    @app_commands.command(
    name="view",
    description="View one of a user's characters."
    )
    async def view(
        self,
        interaction: discord.Interaction,
        member: discord.Member | None = None,
    ):
        # If nobody is selected, default to yourself
        target = member or interaction.user

        characters = get_user_characters_service(str(target.id))

        if not characters:
            await interaction.response.send_message(
                f"{target.display_name} doesn't have any characters.",
                ephemeral=True
            )
            return

        if len(characters) == 1:
            embed = build_character_embed(characters[0])

            await interaction.response.send_message(
                embed=embed,
                ephemeral=False
            )
            return

        await interaction.response.send_message(
            f"Choose one of {target.display_name}'s characters.",
            view=CharacterSelectView(self.bot, characters),
            ephemeral=True
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Character(bot))