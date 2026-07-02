import discord
from discord import app_commands
from discord.ext import commands


class Character(commands.GroupCog, name="character"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="create", description="Create a new character.")
    async def create(
        self,
        interaction: discord.Interaction
    ):
        await interaction.response.send_message(
            "Character creation coming soon!",
            ephemeral=True
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Character(bot))