from discord.ext import commands
import discord
from discord import app_commands

async def setup(bot):
    await bot.add_cog(EmbedForm(bot))

class EmbedForm(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.pending_embeds = {}

    @app_commands.command(
        name="embed", description="Make a discord embed"
    )
    async def embed(self, ctx):
        # Ask the user for embed details using a form
        await ctx.send("Please enter the title for your embed:")
        title = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author)

        await ctx.send("Please enter the description for your embed:")
        description = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author)

        await ctx.send("Please enter the color for your embed (e.g., #RRGGBB):")
        color = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author)

        # Construct the embed
        embed = discord.Embed(title=title.content, description=description.content, color=int(color.content, 16))

        await ctx.send("Please mention the channel where you want to send this embed:")
        channel = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author and m.channel_mentions)

        # Send the embed to the specified channel
        target_channel = channel.channel_mentions[0]
        sent_message = await target_channel.send(embed=embed)

        await ctx.send(f"Embed sent to {target_channel.mention} with ID: {sent_message.id}")

def setup(bot):
    bot.add_cog(EmbedForm(bot))
