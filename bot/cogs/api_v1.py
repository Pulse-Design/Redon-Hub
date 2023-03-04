"""
    File: /bot/cogs/api.py
    Usage: Responsible for the creation of the API
"""
from discord.ext.commands import Cog
from discord import app_commands, Interaction
from fastapi import FastAPI, HTTPException, Depends, WebSocket
from fastapi.security import OAuth2PasswordBearer
from starlette.responses import RedirectResponse
from bot import config
from bot.data import (
    get_user,
    get_users,
    get_user_by_discord_id,
    create_user,
    get_products,
    get_product_by_name,
    get_product,
    create_product,
    delete_product,
    get_tags,
    get_tag,
    create_tag,
    delete_tag,
)
from pydantic import BaseModel
from typing import Union
from datetime import datetime
import uvicorn
import logging
import random
import string

_log = logging.getLogger(__name__)
app = FastAPI()
app.logger = _log
cog = None
X_API_KEY = OAuth2PasswordBearer(config.API.Key)
verificationKeys = {}


def api_auth(x_api_key: str = Depends(X_API_KEY)):
    if x_api_key != config.API.Key:
        raise HTTPException(status_code=401, detail="Invalid API Key.")

    return x_api_key


# Schemas


class UserDisplay(BaseModel):
    id: int
    createdAt: datetime
    discordId: int
    verifiedAt: datetime
    purchases: list[int]


class TagDisplay(BaseModel):
    id: int
    name: str
    color: list[int]
    textColor: list[int]


class Tag(BaseModel):
    name: Union[str, None] = None
    color: Union[list, None] = None
    textColor: Union[list, None] = None


class ProductDisplay(BaseModel):
    id: int
    createdAt: datetime
    name: str
    description: str
    price: int
    productId: int
    attachments: list[str]
    tags: list[int]
    purchases: int
    owners: int


class Product(BaseModel):
    name: Union[str, None] = None
    description: Union[str, None] = None
    price: Union[float, None] = None
    productId: Union[float, None] = None
    attachments: Union[int, None] = None
    tags: Union[int, None] = None


@app.get("/")
async def root():
    return {"message": "Online", "Version": cog.bot.version}


## Websocket
@app.websocket("/v1/socket")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    if websocket.headers.get("Authorization") != f"Bearer {config.API.Key}":
        await websocket.close(code=1008)
        return
    while True:
        data = await websocket.receive_json()
        if data.get("type") == "verify_user":
            _log.info(f"Got Verification Request for {data.get('data')}")

            try:
                user = await get_user(data.get("data"))
            except Exception as e:
                user = None

            if not user or user.discordId == 0:
                key = "".join(random.choices(string.ascii_letters + string.digits, k=5))
                verificationKeys[key] = data.get("data")
                await websocket.send_json({"data": key})
            else:
                await websocket.send_json({"data": "user_verified"})


## Users
@app.get("/v1")
async def v1root():
    return RedirectResponse(url="/")


@app.get("/v1/users", dependencies=[Depends(api_auth)])
async def users_get() -> dict[int, UserDisplay]:
    try:
        users = await get_users()
    except Exception as e:
        _log.error(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")

    results = {}
    for user in users:
        results[user.id] = UserDisplay(**user.dict())

    return results


@app.get("/v1/users/{user_id}", dependencies=[Depends(api_auth)])
async def users_get_user(user_id: int, discordId: bool = False) -> UserDisplay:
    try:
        if discordId:
            user = await get_user_by_discord_id(user_id)
        else:
            user = await get_user(user_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail="User Not Found")

    return UserDisplay(**user.dict())


@app.post("/v1/users/{user_id}/verify", dependencies=[Depends(api_auth)])
async def users_post_verify(user_id: int) -> dict:
    try:
        user = await get_user(user_id)
    except Exception as e:
        user = None

    if not user or user.discordId == 0:
        key = "".join(random.choices(string.ascii_letters + string.digits, k=5))
        verificationKeys[key] = user_id
        return {"message": "Verification Key Created", "data": key}
    else:
        return {"message": "User Already Verified"}


## Products
@app.get("/v1/products", dependencies=[Depends(api_auth)])
async def products_get() -> dict[int, ProductDisplay]:
    try:
        products = await get_products()
    except Exception as e:
        _log.error(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")

    results = {}
    for product in products:
        results[product.id] = ProductDisplay(**product.dict())

    return results


@app.get("/v1/products/{product_id}", dependencies=[Depends(api_auth)])
async def products_get_product(product_id: Union[int, str]) -> ProductDisplay:
    if type(product_id) == str:
        try:
            product_info = await get_product_by_name(product_id)
            product_id = product_info.id
        except Exception as e:
            raise HTTPException(status_code=404, detail="Product Not Found (By Name)")

    try:
        product = await get_product(product_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail="Product Not Found")

    return ProductDisplay(**product.dict())


@app.post("/v1/products", dependencies=[Depends(api_auth)])
async def products_post(product: Product) -> ProductDisplay:
    try:
        product = await create_product(
            product.name,
            product.description,
            product.price,
            product.productId,
            product.attachments,
            product.tags,
        )
    except Exception as e:
        _log.error(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")

    return ProductDisplay(**product.dict())


@app.patch("/v1/products/{product_id}", dependencies=[Depends(api_auth)])
async def products_patch(
    product_id: Union[int, str], product: Product
) -> ProductDisplay:
    if type(product_id) == str:
        try:
            product_info = await get_product_by_name(product_id)
            product_id = product_info.id
        except Exception as e:
            raise HTTPException(status_code=404, detail="Product Not Found")

    try:
        updated_product = product.dict(exclude_unset=True)
        product = await get_product(product_id)

        print(updated_product)
        for key, value in updated_product.items():
            setattr(product, key, value)

        await product.push()
    except Exception as e:
        _log.error(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")

    return ProductDisplay(**product.dict())


@app.delete("/v1/products/{product_id}", dependencies=[Depends(api_auth)])
async def products_delete(product_id: Union[int, str]) -> dict:
    if type(product_id) == str:
        try:
            product_info = await get_product_by_name(product_id)
            product_id = product_info.id
        except Exception as e:
            raise HTTPException(status_code=404, detail="Product Not Found")

    try:
        await delete_product(product_id)
    except Exception as e:
        _log.error(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")

    return {"message": "Product Deleted"}


## Tags
@app.get("/v1/tags", dependencies=[Depends(api_auth)])
async def tags_get() -> dict[int, TagDisplay]:
    try:
        tags = await get_tags()
    except Exception as e:
        _log.error(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")

    results = {}
    for tag in tags:
        results[tag.id] = TagDisplay(**tag.dict())

    return results


@app.get("/v1/tags/{tag_id}", dependencies=[Depends(api_auth)])
async def tags_get_tag(tag_id: int) -> TagDisplay:
    try:
        tag = await get_tag(tag_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail="Tag Not Found")

    return TagDisplay(**tag.dict())


@app.post("/v1/tags", dependencies=[Depends(api_auth)])
async def tags_post(tag: Tag) -> TagDisplay:
    try:
        tag = await create_tag(tag.name, tag.color, tag.textColor)
    except Exception as e:
        _log.error(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")

    return TagDisplay(**tag.dict())


@app.patch("/v1/tags/{tag_id}", dependencies=[Depends(api_auth)])
async def tags_patch(tag_id: int, tag: Tag) -> TagDisplay:
    try:
        updated_tag = tag.dict(exclude_unset=True)
        tag = await get_tag(tag_id)

        for key, value in updated_tag.items():
            setattr(tag, key, value)

        await tag.push()
    except Exception as e:
        _log.error(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")

    return TagDisplay(**tag.dict())


@app.delete("/v1/tags/{tag_id}", dependencies=[Depends(api_auth)])
async def tags_delete(tag_id: int) -> dict:
    try:
        await delete_tag(tag_id)
    except Exception as e:
        _log.error(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")

    return {"message": "Tag Deleted"}


server = uvicorn.Server(
    uvicorn.Config(
        app,
        host=config.API.IP,
        port=config.API.Port,
        loop="none",
    )
)


class API(Cog):
    def __init__(self, bot):
        self.bot = bot

    def overwrite_uvicorn_logger(self):
        for name in logging.root.manager.loggerDict.keys():
            if name.startswith("uvicorn"):
                logging.getLogger(name).handlers = []
                logging.getLogger(name).propagate = True

    verifyGroup = app_commands.Group(
        name="verify", description="Commands regarding verification"
    )

    @verifyGroup.command(name="link")
    async def verify_link(self, interaction: Interaction, key: str):
        await interaction.response.defer(ephemeral=True, thinking=True)

        if key in verificationKeys:
            try:
                user = await get_user(verificationKeys[key])
            except Exception as e:
                user = None

            if user:
                user.discordId = interaction.user.id
                await user.push()
                await interaction.followup.send("User verified!", ephemeral=True)
            else:
                user = await create_user(verificationKeys[key])
                user.discordId = interaction.user.id
                await user.push()
                await interaction.followup.send("User verified!", ephemeral=True)
        else:
            await interaction.followup.send("Invalid key.", ephemeral=True)

    @verifyGroup.command(name="unlink")
    async def verify_unlink(self, interaction: Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)

        try:
            user = await get_user_by_discord_id(interaction.user.id)
        except Exception as e:
            user = None

        if user and user.discordId != 0:
            user.discordId = 0
            await user.push()
            await interaction.followup.send("User unverified!", ephemeral=True)
        else:
            await interaction.followup.send("User not verified.", ephemeral=True)

    @Cog.listener()
    async def on_ready(self):
        global cog
        cog = self
        self.bot.loop.create_task(server.serve())
        self.overwrite_uvicorn_logger()
        _log.info(f"Cog {__name__} ready")


async def setup(bot):
    await bot.add_cog(API(bot))
