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

class CharacterCreateModal(discord.ui.Modal, title="Create Character"):

    name = discord.ui.TextInput(label="Name", max_length=20)
    race = discord.ui.TextInput(label="Race", max_length=20)
    age = discord.ui.TextInput(label="Age", max_length=5)
    gender = discord.ui.TextInput(label="Gender", max_length=20)
    appearance = discord.ui.TextInput(label="Appearance", style=discord.TextStyle.paragraph, max_length=1000)
    personality = discord.ui.TextInput(label="Personality", style=discord.TextStyle.paragraph, max_length=1000)
    backstory = discord.ui.TextInput(label="Backstory", style=discord.TextStyle.paragraph, max_length=2000)
    image_url = discord.ui.TextInput(label="Image URL", required=False)

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction):

        success, result = submit_character_service(
            user_id=str(interaction.user.id),
            name=self.name.value,
            race=self.race.value,
            age=int(self.age.value),
            gender=self.gender.value,
            appearance=self.appearance.value,
            personality=self.personality.value,
            backstory=self.backstory.value,
            image_url=self.image_url.value or "",
        )

        if not success:
            await interaction.response.send_message(result, ephemeral=True)
            return

        embed = discord.Embed(
            title=f"Character Submission: {result['name']}",
            color=discord.Color.orange()
        )

        embed.add_field(name="User", value=f"<@{result['user_id']}>", inline=False)
        embed.add_field(name="Race", value=result["race"], inline=True)
        embed.add_field(name="Age", value=result["age"], inline=True)
        embed.add_field(name="Gender", value=result["gender"], inline=True)

        embed.add_field(name="Appearance", value=result["appearance"], inline=False)
        embed.add_field(name="Personality", value=result["personality"], inline=False)
        embed.add_field(name="Backstory", value=result["backstory"], inline=False)

        if result.get("image_url"):
            embed.set_image(url=result["image_url"])

        channel = await self.bot.fetch_channel(1522281815031808364)
        view = CharacterApprovalView(result["pending_id"])
        await channel.send(embed=embed, view=view)

        await interaction.response.send_message(
            f"Character **{result['name']}** submitted for review.",
            ephemeral=True
        )


class Character(commands.GroupCog, name="character"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="create")
    async def create(self, interaction: discord.Interaction):
        await interaction.response.send_modal(CharacterCreateModal(self.bot))

async def setup(bot: commands.Bot):
    await bot.add_cog(Character(bot))