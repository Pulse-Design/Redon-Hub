"""
File: /bot/cogs/hola.py
Description: Link to Pulse Design's Cashapp
Usage: This cog provides a command to send a Cashapp link for Pulse Design.

Commands:
    /cashapp - Sends a message with a link to open Pulse Design's Cashapp.
"""

from discord.ext.commands import Cog
from discord.app_commands import command, Interaction
import logging

_log = logging.getLogger(__name__)

class Hola(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command()
    async def cashapp(self, interaction: Interaction):
        """Sends a link to open Pulse Design's Cashapp."""
        await interaction.response.send_message("Click here to open Pulse Design's Cashapp: [Click Here](https://pulsedesignhub.web.app/cashapp/)")

    @Cog.listener()
    async def on_ready(self):
        _log.info(f"Cog {__name__} ready")

def setup(bot):
    bot.add_cog(Hola(bot))
