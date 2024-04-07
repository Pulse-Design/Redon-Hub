"""
    File: /bot/cogs/
    Usage: 
"""
from discord.ext.commands import Cog
from discord import app_commands, Interaction
import logging

_log = logging.getLogger(__name__)


class Hola(Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command()
    async def hola(self, interaction: Interaction):
        await interaction.response.send_message("hola")
    @Cog.listener()
    async def on_ready(self):
        _log.info(f"Cog {__name__} ready")


async def setup(bot):
    await bot.add_cog(Hola(bot))
