# bot/cogs/embed.py
"""
File: /bot/cogs/embed.py
Usage: Embed related commands
"""
from discord.ext import commands
import discord
from discord import app_commands


class EmbedForm(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="embed", description="Make a discord embed"
    )
    async def embed(self, interaction: app_commands.Context):
        # Ask the user for embed details using a form
        await interaction.response.send_message(
            "Please enter the title for your embed:", ephemeral=True)
        title = await interaction.channel.history(limit=1).next()
        title = title.content

        await interaction.response.send_message(
            "Please enter the description for your embed:", ephemeral=True)
        description = await interaction.channel.history(limit=1).next()
        description = description.content

        await interaction.response.send_message(
            "Please enter the color for your embed (e.g., #RRGGBB):", ephemeral=True)
        color = await interaction.channel.history(limit=1).next()
        color = int(color.content, 16)

        # Construct the embed
        embed = discord.Embed(
            title=title, description=description, color=color)

        await interaction.response.send_message(
            "Please mention the channel where you want to send this embed:", ephemeral=True)
        channel = await interaction.channel.history(limit=1).next()
        channel = channel.channel_mentions[0]

        # Send the embed to the specified channel
        sent_message = await channel.send(embed=embed)

        await interaction.response.send_message(
            f"Embed sent to {channel.mention} with ID: {sent_message.id}", ephemeral=True)


def setup(bot):
    bot.add_cog(EmbedForm(bot))