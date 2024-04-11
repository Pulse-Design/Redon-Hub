from discord.ext.commands import Cog, command
from discord import Embed
from discord import cog_ext, SlashContext
import logging

_log = logging.getLogger(__name__)


class EmbedCog(Cog):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(name="embed", description="Create and send a custom embed.")
    async def create_embed(self, ctx: SlashContext):
        # Respond to the slash command with a message to start building the embed
        await ctx.send("Let's create a custom embed!")

        # Collect user input to build the embed
        await ctx.send("Enter the title for the embed:")
        title_msg = await self.bot.wait_for("message", check=lambda m: m.author == ctx.author, timeout=60)
        title = title_msg.content

        await ctx.send("Enter the description for the embed:")
        desc_msg = await self.bot.wait_for("message", check=lambda m: m.author == ctx.author, timeout=60)
        description = desc_msg.content

        # Create the embed
        embed = Embed(title=title, description=description)

        # Send the embed
        await ctx.send(embed=embed)

    @Cog.listener()
    async def on_ready(self):
        _log.info(f"Cog {__name__} ready")


def setup(bot):
    bot.add_cog(EmbedCog(bot))
