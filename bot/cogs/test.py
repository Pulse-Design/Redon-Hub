from discord.ext.commands import Cog, command
from discord import Interaction, Embed
import logging

_log = logging.getLogger(__name__)

class PredefinedEmbed(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command()
    async def embed(self, interaction: Interaction):
        # Create a predefined embed
        embed = Embed(
            title="Predefined Embed",
            description="This is a predefined embed message.",
            color=0x7289DA  # Discord color (blurple)
        )

        embed.add_field(name="Field 1", value="This is field 1", inline=False)
        embed.add_field(name="Field 2", value="This is field 2", inline=False)
        embed.set_footer(text="Sent by Bot")

        # Send the predefined embed
        await interaction.response.send_message(embed=embed)

    @Cog.listener()
    async def on_ready(self):
        _log.info(f"Cog {__name__} ready")

async def setup(bot):
    bot.add_cog(PredefinedEmbed(bot))
