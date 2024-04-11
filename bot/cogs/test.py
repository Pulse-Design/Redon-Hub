from discord.ext.commands import Bot, Cog, Context, command
from discord import SlashContext, cog_ext
from discord import create_option
from discord import Embed

class PredefinedEmbed(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @cog_ext.cog_slash(
        name="embed",
        description="Send a predefined embed message",
        options=[
            create_option(
                name="channel",
                description="Channel to send the embed",
                option_type=7,  # Type 7 represents a channel option
                required=False
            )
        ]
    )
    async def send_embed(self, ctx: SlashContext, channel=None):
        # Create a predefined embed
        embed = Embed(
            title="Predefined Embed",
            description="This is a predefined embed message.",
            color=0x7289DA  # Discord color (blurple)
        )

        embed.add_field(name="Field 1", value="This is field 1", inline=False)
        embed.add_field(name="Field 2", value="This is field 2", inline=False)
        embed.set_footer(text="Sent by Bot")

        # Determine where to send the embed
        if channel:
            target_channel = self.bot.get_channel(channel)
        else:
            target_channel = ctx.channel

        # Send the predefined embed to the target channel
        await target_channel.send(embed=embed)

async def setup(bot: Bot):
    await bot.add_cog(PredefinedEmbed(bot))
