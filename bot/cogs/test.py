"""
    File: /bot/cogs/
    Usage: 
"""
from discord.ext.commands import Cog, command
from discord.app_commands import Choice, Choices
from random import randint
from discord import Interaction
import logging

_log = logging.getLogger(__name__)


class Template(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        _log.info(f"Cog {__name__} ready")

    @command(name="random", description="Get a random number")
    async def random_command(self, interaction: Interaction, min_: int = 0, max_: int = 100):
        """
        Generate a random number between min_ and max_.
        """

        await interaction.response.send_message(f"Your number is: {randint(min_, max_)}")


async def setup(bot):
    await bot.add_cog(Template(bot))
