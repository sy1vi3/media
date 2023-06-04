from playhouse.postgres_ext import *
import discord
from discord import app_commands
import os
import time
from typing import List

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
async def saveimg(interaction, file: discord.Attachment, tags: str, category: str, nsfw: bool=False, political: bool=False, lgbt: bool=False, unsafe: bool=False, nsfl: bool=False):
    timestamp = str(time.time()).split(".")[0]
    filetype = file.filename.split(".")[-1].lower()
    saved_name = f"{timestamp}.{filetype}"
    await file.save(f"img/{saved_name}")
    split_tags = tags.split(" ")
    Image.create(guid=timestamp, tags=split_tags, filename=saved_name, nsfw=nsfw, nsfl=nsfl, political=political, lgbt=lgbt, unsafe=unsafe, type=filetype, category=category)
    await interaction.response.send_message(f"{saved_name} saved")


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
    client.run(os.environ['FORESTRY_TOKEN'])