from playhouse.postgres_ext import *
import discord
from discord import app_commands
import os
import time
from typing import List
import tokens
import random

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


db = PostgresqlExtDatabase('files', user=os.environ['DB_USER'], password=os.environ['DB_PASS'], host=os.environ['DB_HOST'], port=os.environ['DB_PORT'])
class BaseModel(Model):
    class Meta:
        database = db

class Image(BaseModel):
    guid = BigIntegerField()
    tags = JSONField()
    filename = TextField()
    nsfw = BooleanField(null=True)
    nsfl = BooleanField(null=True)
    political = BooleanField(null=True)
    lgbt = BooleanField(null=True)
    unsafe = BooleanField(null=True)
    type = TextField()
    category = TextField(null=True)


@tree.command(name="saveimg", description="save an image to the database")
async def saveimg(interaction, file: discord.Attachment, tags: str, category: str, nsfw: bool=False, political: bool=False, lgbt: bool=False, unsafe: bool=False, nsfl: bool=False, noindex: bool=False):
    global upload_ticker
    timestamp = str(time.time()).split(".")[0]
    snowflake_append = random.randint(10000,99999)
    filetype = file.filename.split(".")[-1].lower()
    saved_name = f"{timestamp}{snowflake_append}.{filetype}"
    await file.save(f"img/{saved_name}")
    split_tags = tags.split(" ")
    if noindex is not True:
        Image.create(guid=timestamp, tags=split_tags, filename=saved_name, nsfw=nsfw, nsfl=nsfl, political=political, lgbt=lgbt, unsafe=unsafe, type=filetype, category=category)
    await interaction.response.send_message(f"{saved_name} saved")

@tree.command(name="remove_by_filename", description="remove an image from the database by its filename")
async def removeimg(interaction, filename: str):
    try:
        q = Image.delete().where(Image.filename == filename)
        q.execute()
        if os.path.exists(f"img/{filename}"):
            os.remove(f"img/{filename}")
        await interaction.response.send_message(f"{filename} deleted")
    except Exception as e:
        await interaction.response.send_message(e)

@tree.command(name="named_file_upload", description="add a file to the mirrors but with a specific filename")
async def fileupload(interaction, file: discord.Attachment, filename: str):
    if os.path.exists(f"img/{filename}"):
        os.remove(f"img/{filename}")
    await file.save(f"img/{filename}")
    await interaction.response.send_message(f"{filename} added")


@saveimg.autocomplete("category")
async def saveimg_autocomplete(interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
    categories = ["meme", "image", "vex", "art", "other"]
    return [
        app_commands.Choice(name=category, value=category)
        for category in categories if current.lower() in category.lower()
    ]

@client.event
async def on_ready():
    await tree.sync()
    print("Ready!")

if __name__ == "__main__":
    db.connect()
    db.create_tables([Image], safe=True)
    client.run(tokens.bot_token)