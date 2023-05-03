"""
    File: /bot/cogs/product.py
    Usage: Product related commands
"""
from discord import (
    app_commands,
    Interaction,
    Member,
    Embed,
    utils,
    ui,
    TextStyle,
    SelectOption,
    ButtonStyle,
)
from asyncio import TimeoutError
from discord.ext.commands import Cog
from bot.data import (
    get_users,
    get_products,
    get_product_by_name,
    get_product,
    create_product,
    delete_product,
    get_tags,
    Product,
)
from typing import Optional
import logging
import re

_log = logging.getLogger(__name__)


async def promptChooseAttachments(
    self, interaction: Interaction, product: Optional[Product]
):
    attachments = []
    user_messages = []

    # info_message = await interaction.followup.send(
    embed = Embed(
        title="Attachments",
        description="Please enter the attachments to send to owners of this product. Please add each link in a new message. Say `done` when you are finished.",
        colour=interaction.user.colour,
        timestamp=utils.utcnow(),
    ).set_footer(
        text=f"Redon Hub • Say `cancel` to cancel creation • Version {self.bot.version}"
    )
    if product:
        embed.add_field(
            name="Current Attachments",
            value="\n".join(product.attachments),
            inline=False,
        )
    info_message = await interaction.edit_original_response(
        embed=embed,
        view=None,
    )

    while True:
        try:
            message = await self.bot.wait_for("message", timeout=200.0)
        except TimeoutError:
            await info_message.edit(
                embed=Embed(
                    title="Timed Out",
                    description="You took too long to respond",
                    colour=interaction.user.colour,
                    timestamp=utils.utcnow(),
                ).set_footer(text=f"Redon Hub • Version {self.bot.version}"),
            )
            return
        except Exception as e:
            _log.error(e)
            await info_message.edit(
                embed=Embed(
                    title="Error",
                    description="An unknown error has occured during creation.",
                    colour=interaction.user.colour,
                    timestamp=utils.utcnow(),
                ).set_footer(text=f"Redon Hub • Version {self.bot.version}"),
            )
            return

        if message.content.lower() == "cancel":
            for message in user_messages:
                await message.delete()

            await message.delete()

            await info_message.edit(
                embed=Embed(
                    title="Cancelled",
                    description=f"Product creation has been cancelled.",
                    colour=interaction.user.colour,
                    timestamp=utils.utcnow(),
                ).set_footer(text=f"Redon Hub • Version {self.bot.version}"),
            )
            return
        elif message.content.lower() == "done":
            user_messages.append(message)

            break
        else:
            if re.match(
                "http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
                message.content,
            ):
                links = re.findall(
                    "http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
                    message.content,
                )

                for link in links:
                    attachments.append(link)

                user_messages.append(message)

                embed = Embed(
                    title="Attachments",
                    description="Please enter the attachments to send to owners of this product. Please add each link in a new message. Say `done` when you are finished.",
                    colour=interaction.user.colour,
                    timestamp=utils.utcnow(),
                ).set_footer(
                    text=f"Redon Hub • Say `cancel` to cancel creation • Version {self.bot.version}"
                )

                if product:
                    embed.add_field(
                        name="Current Attachments",
                        value="\n".join(product.attachments),
                        inline=False,
                    )

                embed.add_field(name="Attachments", value="\n".join(attachments))

                await info_message.edit(embed=embed)

    for message in user_messages:
        await message.delete()

    # await info_message.delete()

    return attachments


async def promptCreateProductChooseAttachments(self, interaction: Interaction):
    attachments = await promptChooseAttachments(self, interaction)

    try:
        tags = []
        for value in self.values:
            tags.append(int(value))

        product = await create_product(
            name=self.name.value,
            description=self.description.value,
            imageId=self.imageId.value,
            price=int(self.price.value),
            productId=int(self.productId.value),
            stock=int(self.stock.value) or None,
            attachments=attachments,
            tags=tags,
        )
        # await interaction.followup.send(
        await interaction.edit_original_response(
            embed=Embed(
                title="Product Created",
                description=f"Your product has been created!",
                colour=interaction.user.colour,
                timestamp=utils.utcnow(),
            ).set_footer(text=f"Redon Hub • Version {self.bot.version}"),
            view=None,
        )
    except Exception as e:
        _log.error(e)
        # await interaction.followup.send(
        await interaction.edit_original_response(
            embed=Embed(
                title="Error",
                description="An unknown error has occured during creation.",
                colour=interaction.user.colour,
                timestamp=utils.utcnow(),
            ).set_footer(text=f"Redon Hub • Version {self.bot.version}"),
            view=None,
        )


async def promptUpdateProductChooseAttachments(
    self, interaction: Interaction, product: Product
):
    attachments = await promptChooseAttachments(self, interaction, product)

    try:
        product.attachments = attachments
        await product.push()
        # await interaction.followup.send(
        await interaction.edit_original_response(
            embed=Embed(
                title="Product Updated",
                description=f"Your product has been updated!",
                colour=interaction.user.colour,
                timestamp=utils.utcnow(),
            ).set_footer(text=f"Redon Hub • Version {self.bot.version}"),
            view=None,
        )
    except Exception as e:
        _log.error(e)
        # await interaction.followup.send(
        await interaction.edit_original_response(
            embed=Embed(
                title="Error",
                description="An unknown error has occured while updating.",
                colour=interaction.user.colour,
                timestamp=utils.utcnow(),
            ).set_footer(text=f"Redon Hub • Version {self.bot.version}"),
            view=None,
        )


class createProductSelectTags(ui.Select):
    def __init__(self, tags, **kwargs):
        options = []
        for kwarg in kwargs:
            setattr(self, kwarg, kwargs[kwarg])

        for tag in tags:
            options.append(SelectOption(label=tag.name, value=tag.id))

        super().__init__(
            placeholder="Select tags for your product",
            min_values=1,
            max_values=len(options),
            options=options,
        )

    async def callback(self, interaction: Interaction):
        await interaction.response.defer()

        await promptCreateProductChooseAttachments(self, interaction)


class createProductSelectTagsNone(ui.Button):
    def __init__(self, **kwargs):
        for kwarg in kwargs:
            setattr(self, kwarg, kwargs[kwarg])

        super().__init__(label="None", style=ButtonStyle.primary)

    async def callback(self, interaction: Interaction):
        await interaction.response.defer()
        self.values = []
        await promptCreateProductChooseAttachments(self, interaction)


class createProductSelectTagsView(ui.View):
    def __init__(self, tags, **kwargs):
        super().__init__()
        self.add_item(createProductSelectTags(tags, **kwargs))
        self.add_item(createProductSelectTagsNone(**kwargs))


class createProduct(ui.Modal, title="Create Product"):
    name = ui.TextInput(label="Product Name")
    description = ui.TextInput(
        label="Product Description", placeholder="Optional", style=TextStyle.paragraph
    )
    price = ui.TextInput(label="Product Price", placeholder="In Robux")
    stock = ui.TextInput(label="Stock", placeholder="Leave blank for unlimited")
    productId = ui.TextInput(
        label="Developer Product ID", placeholder="Example: 1234567890"
    )
    imageId = ui.TextInput(
        label="Image ID",
        placeholder="rbxassetid format. Example: rbxassetid://1234567890",
    )

    def __init__(self, bot, **kwargs):
        self.bot = bot
        super().__init__(**kwargs)

    async def on_submit(self, interaction: Interaction) -> None:
        await interaction.response.send_message(
            embed=Embed(
                title="Select Tags",
                description="Select the tags for your product",
                colour=interaction.user.colour,
                timestamp=utils.utcnow(),
            ).set_footer(text=f"Redon Hub • Version {self.bot.version}"),
            view=createProductSelectTagsView(
                await get_tags(),
                name=self.name,
                description=self.description,
                imageId=self.imageId,
                price=self.price,
                productId=self.productId,
                stock=self.stock,
                bot=self.bot,
            ),
        )


class deleteProductSelect(ui.Select):
    def __init__(self, products, **kwargs):
        options = []
        for kwarg in kwargs:
            setattr(self, kwarg, kwargs[kwarg])

        for product in products:
            options.append(SelectOption(label=product.name, value=product.id))

        super().__init__(
            placeholder="Select product",
            min_values=1,
            max_values=len(options),
            options=options,
        )

    async def callback(self, interaction: Interaction):
        for product in self.values:
            product_name = product
            try:
                product_data = await get_product(int(product))
                product_name = product_data.name
            except Exception as e:
                _log.error(e)

            try:
                await delete_product(int(product))
                await interaction.response.send_message(
                    embed=Embed(
                        title="Product Deleted",
                        description=f"{product_name} has been deleted!",
                        colour=interaction.user.colour,
                        timestamp=utils.utcnow(),
                    ).set_footer(text=f"Redon Hub • Version {self.bot.version}"),
                )
            except Exception as e:
                _log.error(e)
                await interaction.response.send_message(
                    embed=Embed(
                        title="Error",
                        description=f"An unknown error has occured during deletion of {product_name}.\nHowever, it is possible the products was still deleted, you can check this using `/products`.",
                        colour=interaction.user.colour,
                        timestamp=utils.utcnow(),
                    ).set_footer(text=f"Redon Hub • Version {self.bot.version}"),
                )
                return


class deleteProductView(ui.View):
    def __init__(self, products, **kwargs):
        super().__init__()
        self.add_item(deleteProductSelect(products, **kwargs))


async def sendUpdatedProductFiles(self, product: Product):
    users = await get_users()

    for user in users:
        if product.id in user.purchases:
            try:
                user = await self.bot.fetch_user(user.discordId)

                if user.dm_channel is None:
                    await user.create_dm()

                await user.dm_channel.send(
                    embed=Embed(
                        title="Product Updated",
                        description=f"A product you have purchased has been updated! You can find the information link below.",
                        colour=user.colour,
                        timestamp=utils.utcnow(),
                    )
                    .set_footer(text=f"Redon Hub • Version {self.bot.version}")
                    .add_field(name="Product", value=product.name, inline=True)
                    .add_field(
                        name="Attachments",
                        value="\n".join(product.attachments) or "None",
                        inline=False,
                    )
                )
            except Exception as e:
                pass


class updateProductSelectTags(ui.Select):
    def __init__(self, tags, bot, product: Product):
        self.bot = bot
        self.product = product

        options = []

        for tag in tags:
            default = False
            if tag.id in product.tags:
                default = True
            options.append(SelectOption(label=tag.name, value=tag.id, default=default))

        super().__init__(
            placeholder="Select tags for your product",
            min_values=1,
            max_values=len(options),
            options=options,
        )

    async def callback(self, interaction: Interaction):
        await interaction.response.defer()

        try:
            tags = []
            for value in self.values:
                tags.append(int(value))

            self.product.tags = tags

            await self.product.push()

            await interaction.edit_original_response(
                embed=Embed(
                    title="Product Updated",
                    description=f"Your product has been updated!",
                    colour=interaction.user.colour,
                    timestamp=utils.utcnow(),
                ).set_footer(text=f"Redon Hub • Version {self.bot.version}"),
                view=None,
            )
        except Exception as e:
            _log.error(e)
            # await interaction.followup.send(
            await interaction.edit_original_response(
                embed=Embed(
                    title="Error",
                    description="An unknown error has occured while updating.",
                    colour=interaction.user.colour,
                    timestamp=utils.utcnow(),
                ).set_footer(text=f"Redon Hub • Version {self.bot.version}"),
                view=None,
            )


class updateProductSelectTagsNone(ui.Button):
    def __init__(self, bot, product: Product):
        self.bot = bot
        self.product = product
        super().__init__(label="None", style=ButtonStyle.primary)

    async def callback(self, interaction: Interaction):
        await interaction.response.defer()

        try:
            self.product.tags = []

            await self.product.push()

            await interaction.edit_original_response(
                embed=Embed(
                    title="Product Updated",
                    description=f"Your product has been updated!",
                    colour=interaction.user.colour,
                    timestamp=utils.utcnow(),
                ).set_footer(text=f"Redon Hub • Version {self.bot.version}"),
                view=None,
            )
        except Exception as e:
            _log.error(e)
            # await interaction.followup.send(
            await interaction.edit_original_response(
                embed=Embed(
                    title="Error",
                    description="An unknown error has occured while updating.",
                    colour=interaction.user.colour,
                    timestamp=utils.utcnow(),
                ).set_footer(text=f"Redon Hub • Version {self.bot.version}"),
                view=None,
            )


class updateProductSelectTagsCancel(ui.Button):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(label="Cancel", style=ButtonStyle.danger)

    async def callback(self, interaction: Interaction):
        await interaction.response.defer()

        await interaction.edit_original_response(
            embed=Embed(
                title="Product Update Cancelled",
                description=f"Your product update has been cancelled!",
                colour=interaction.user.colour,
                timestamp=utils.utcnow(),
            ).set_footer(text=f"Redon Hub • Version {self.bot.version}"),
            view=None,
        )


class updateProductSelectTagsView(ui.View):
    def __init__(self, tags, bot, product: Product):
        super().__init__()
        self.add_item(updateProductSelectTags(tags, bot, product))
        self.add_item(updateProductSelectTagsNone(bot, product))
        self.add_item(updateProductSelectTagsCancel(bot))


class updateProduct(ui.Modal, title="Update Product"):
    def __init__(self, bot, product: Product):
        self.bot = bot
        self.product = product
        super().__init__()

        self.add_item(ui.TextInput(label="Product Name", default=product.name))
        self.add_item(
            ui.TextInput(
                label="Product Description",
                placeholder="Optional",
                style=TextStyle.paragraph,
                default=product.description,
            )
        )
        self.add_item(
            ui.TextInput(
                label="Product Price", placeholder="In Robux", default=product.price
            )
        )
        self.add_item(
            ui.TextInput(
                label="Stock",
                placeholder="Leave blank for unlimited",
                default=product.stock,
            )
        )
        self.add_item(ui.TextInput(label="Developer Product ID", default=product.price))
        self.add_item(
            ui.TextInput(
                label="Image ID",
                placeholder="rbxassetid format. Example: rbxassetid://1234567890",
                default=product.imageId,
            )
        )

    async def on_submit(self, interaction: Interaction) -> None:
        try:
            for item in self.children:
                if item.label == "Product Name":
                    self.product.name = item.value
                elif item.label == "Product Description":
                    self.product.description = item.value
                elif item.label == "Product Price":
                    self.product.price = int(item.value)
                elif item.label == "Stock":
                    self.product.stock = int(item.value) or None
                elif item.label == "Developer Product ID":
                    self.product.productId = int(item.value)
                elif item.label == "Image ID":
                    self.product.imageId = item.value

            await self.product.push()

            await interaction.response.edit_message(
                embed=Embed(
                    title="Product Updated",
                    description=f"Your product has been updated!",
                    colour=interaction.user.colour,
                    timestamp=utils.utcnow(),
                ).set_footer(text=f"Redon Hub • Version {self.bot.version}"),
                view=None,
            )
        except Exception as e:
            _log.error(e)
            # await interaction.followup.send(
            await interaction.response.edit_message(
                embed=Embed(
                    title="Error",
                    description="An unknown error has occured while updating.",
                    colour=interaction.user.colour,
                    timestamp=utils.utcnow(),
                ).set_footer(text=f"Redon Hub • Version {self.bot.version}"),
                view=None,
            )


class updateProductView(ui.View):
    def __init__(self, product: Product, **kwargs):
        self.product = product
        self.bot = kwargs.get("bot")
        super().__init__()

    @ui.button(label="Update Other Values", style=ButtonStyle.success)
    async def update_product(self, interaction: Interaction, _):
        await interaction.response.send_modal(updateProduct(self.bot, self.product))

    @ui.button(label="Update Tags", style=ButtonStyle.primary)
    async def update_tags(self, interaction: Interaction, _):
        await interaction.response.defer()

        await interaction.edit_original_response(
            embed=Embed(
                title="Select Tags",
                description="Select the tags for your product",
                colour=interaction.user.colour,
                timestamp=utils.utcnow(),
            ).set_footer(text=f"Redon Hub • Version {self.bot.version}"),
            view=updateProductSelectTagsView(
                await get_tags(),
                self.bot,
                self.product,
            ),
        )

    @ui.button(label="Update Attachments", style=ButtonStyle.danger)
    async def update_attachments(self, interaction: Interaction, _):
        await interaction.response.defer()

        await promptUpdateProductChooseAttachments(self, interaction, self.product)


class ProductCog(Cog):
    def __init__(self, bot):
        self.bot = bot

    product_commands = app_commands.Group(
        name="products", description="Product Commands"
    )

    product_admin = app_commands.Group(
        name="admin",
        description="Product Admin Commands",
        parent=product_commands,
        default_permissions=None,
    )

    @product_commands.command(
        name="view", description="View all the products this server has"
    )
    async def get_products_command(self, interaction: Interaction):
        await interaction.response.defer()

        products = await get_products()

        await interaction.followup.send(
            embed=Embed(
                title="Products",
                description=f"Here is all the products I was able to find! To get more information on a individual product run `/product (product)`",
                colour=interaction.user.colour,
                timestamp=utils.utcnow(),
            )
            .set_footer(text=f"Redon Hub • Version {self.bot.version}")
            .add_field(
                name="Products",
                value="\n".join([product.name for product in products]) or "None",
            )
        )

    @product_commands.command(
        name="get", description="Get information on a specific product"
    )
    async def get_product_info_command(
        self, interaction: Interaction, product_name: str
    ):
        try:
            product = await get_product_by_name(product_name)
        except Exception:
            product = None

        if product:
            await interaction.response.send_message(
                embed=Embed(
                    title=product.name,
                    description=f"Here is all the info I was able to get on `{product.name}`!",
                    colour=interaction.user.colour,
                    timestamp=utils.utcnow(),
                )
                .set_footer(text=f"Redon Hub • Version {self.bot.version}")
                .add_field(name="Price", value=product.price, inline=True)
                .add_field(name="Description", value=product.description, inline=False)
            )
        else:
            await interaction.response.send_message(
                embed=Embed(
                    title="Not Found",
                    description=f"I was unable to find any information on `{product_name}`.",
                    colour=interaction.user.colour,
                    timestamp=utils.utcnow(),
                ).set_footer(text=f"Redon Hub • Version {self.bot.version}")
            )

    @get_product_info_command.autocomplete("product_name")
    async def get_product_info_command_autocomplete(
        self, interaction: Interaction, current_product_name: str
    ):
        try:
            products = await get_products()
        except Exception:
            products = []

        return [
            app_commands.Choice(name=product.name, value=product.name)
            for product in products
            if current_product_name.lower() in product.name.lower()
        ]

    @product_admin.command(name="create", description="Create a new product")
    async def create_product_command(self, interaction: Interaction):
        await interaction.response.send_modal(createProduct(bot=self.bot))

    @product_admin.command(name="delete", description="Delete a product")
    async def delete_product_command(self, interaction: Interaction):
        await interaction.response.defer()

        products = await get_products()

        await interaction.followup.send(
            embed=Embed(
                title="Delete Product",
                description="Select the product you want to delete",
                colour=interaction.user.colour,
                timestamp=utils.utcnow(),
            ).set_footer(text=f"Redon Hub • Version {self.bot.version}"),
            view=deleteProductView(products, bot=self.bot),
        )

    @product_admin.command(name="update", description="Update a product")
    async def update_product_command(self, interaction: Interaction, product_name: str):
        await interaction.response.defer()

        try:
            product = await get_product_by_name(product_name)
        except Exception:
            product = None

        if product:
            await interaction.followup.send(
                embed=Embed(
                    title=product.name,
                    description=f"Please select what you want to update for `{product.name}`!",
                    colour=interaction.user.colour,
                    timestamp=utils.utcnow(),
                ).set_footer(text=f"Redon Hub • Version {self.bot.version}"),
                view=updateProductView(product, bot=self.bot),
            )
        else:
            await interaction.followup.send(
                embed=Embed(
                    title="Not Found",
                    description=f"I was unable to find any product to update with the name `{product_name}`.",
                    colour=interaction.user.colour,
                    timestamp=utils.utcnow(),
                ).set_footer(text=f"Redon Hub • Version {self.bot.version}")
            )

    @update_product_command.autocomplete("product_name")
    async def update_product_command_autocomplete(
        self, interaction: Interaction, current_product_name: str
    ):
        try:
            products = await get_products()
        except Exception:
            products = []

        return [
            app_commands.Choice(name=product.name, value=product.name)
            for product in products
            if current_product_name.lower() in product.name.lower()
        ]

    @Cog.listener()
    async def on_ready(self):
        _log.info(f"Cog {__name__} ready")


async def setup(bot):
    await bot.add_cog(ProductCog(bot))
