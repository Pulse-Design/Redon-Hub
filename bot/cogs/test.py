from discord.ext.commands import Cog, command
from discord import Interaction
from discord.embeds import Embed
import logging

_log = logging.getLogger(__name__)

class CustomEmbed(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command()
    async def embed(self, interaction: Interaction):
        # Ask user for input
        await interaction.response.send_message("Let's create a custom embed!")

        # Wait for user's response
        def check(m):
            return m.author == interaction.user and m.channel == interaction.channel

        try:
            response_message = await self.bot.wait_for("message", check=check, timeout=60.0)
        except TimeoutError:
            await interaction.response.send_message("Embed creation timed out.")
            return

        # Get user input and construct the embed
        embed = Embed(title=response_message.content)

        await interaction.response.send_message("Enter the description:")
        try:
            description_message = await self.bot.wait_for("message", check=check, timeout=60.0)
        except TimeoutError:
            await interaction.response.send_message("Embed creation timed out.")
            return

        embed.description = description_message.content

        await interaction.response.send_message("Add fields (name:value, separate fields with semicolon ';'):")
        try:
            fields_message = await self.bot.wait_for("message", check=check, timeout=60.0)
        except TimeoutError:
            await interaction.response.send_message("Embed creation timed out.")
            return

        fields = fields_message.content.split(';')
        for field in fields:
            name, value = field.split(':')
            embed.add_field(name=name.strip(), value=value.strip(), inline=False)

        # Send the embed
        await interaction.response.send_message(embed=embed)

    @Cog.listener()
    async def on_ready(self):
        _log.info(f"Cog {__name__} ready")

async def setup(bot):
    bot.add_cog(CustomEmbed(bot))
