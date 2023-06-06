from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from playhouse.postgres_ext import *
app = FastAPI()
import os
import json
from playhouse.shortcuts import model_to_dict, dict_to_model

app.mount("/static", StaticFiles(directory="img"), name="static")

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

db.connect()
db.create_tables([Image], safe=True)

@app.get("/search")
async def search(tags: str="", nsfw: bool=False, unsafe: bool=False, nsfl:bool=False, category: str="meme,image,vex,art,other", lgbt: bool=True, political: bool=True,pos: int=1):
    split_tags = tags.lower().split(",")
    _nsfw = [False]
    _nsfl = [False]
    _unsafe = [False]
    _lgbt = [False]
    _politcal = [False]
    split_category = category.split(",")
    if nsfw:
        _nsfw.append(True)
    if nsfl:
        _nsfl.append(True)
    if unsafe:
        _unsafe.append(True)
    if lgbt:
        _lgbt.append(True)
    if political:
        _politcal.append(True)
    files = Image.select().where(Image.nsfw.in_(_nsfw) & Image.nsfl.in_(_nsfl) & Image.unsafe.in_(_unsafe) & Image.lgbt.in_(_lgbt) & Image.political.in_(_politcal) & Image.category.in_(split_category))
    filtered = list()
    for file in files:
        matches = 0
        for i in file.tags:
            matches += split_tags.count(i)
        filtered.append([file.filename, matches])
    ranked = sorted(filtered, key=lambda x:x[1], reverse=True)
    if pos > 0:
        pos -= 1
    else:
        pos = 0
    response_file = ranked[pos][0]
    return FileResponse(f"img/{response_file}")

@app.get("/random")
async def random(nsfw: bool=False, unsafe: bool=False, nsfl:bool=False, category: str="meme,image,vex,art,other", lgbt: bool=True, political: bool=True, onlynsfw: bool=False):
    if onlynsfw == False:
        _nsfw = [False]
    else:
        _nsfw = []
    _nsfl = [False]
    _unsafe = [False]
    _lgbt = [False]
    _politcal = [False]
    split_category = category.split(",")
    if nsfw:
        _nsfw.append(True)
    if nsfl:
        _nsfl.append(True)
    if unsafe:
        _unsafe.append(True)
    if lgbt:
        _lgbt.append(True)
    if political:
        _politcal.append(True)
    files = Image.select().where(Image.nsfw.in_(_nsfw) & Image.nsfl.in_(_nsfl) & Image.unsafe.in_(_unsafe) & Image.lgbt.in_(_lgbt) & Image.political.in_(_politcal) & Image.category.in_(split_category)
                                 ).order_by(fn.Random()).limit(2)
    response_file = files[0].filename
    return FileResponse(f"img/{response_file}")

@app.get("/json")
async def get_json(nsfw: bool=False, unsafe: bool=False, nsfl:bool=False, category: str="meme,image,vex,art,other", lgbt: bool=True, political: bool=True, onlynsfw: bool=False):
    if onlynsfw == False:
        _nsfw = [False]
    else:
        _nsfw = []
    _nsfl = [False]
    _unsafe = [False]
    _lgbt = [False]
    _politcal = [False]
    split_category = category.split(",")
    if nsfw:
        _nsfw.append(True)
    if nsfl:
        _nsfl.append(True)
    if unsafe:
        _unsafe.append(True)
    if lgbt:
        _lgbt.append(True)
    if political:
        _politcal.append(True)
    files = Image.select().where(Image.nsfw.in_(_nsfw) & Image.nsfl.in_(_nsfl) & Image.unsafe.in_(_unsafe) & Image.lgbt.in_(_lgbt) & Image.political.in_(_politcal) & Image.category.in_(split_category))
    json_data = []
    for file in files:
        json_data.append(model_to_dict(file))
    return json_data


@app.get("/stats")
async def stats(nsfw: bool=False, unsafe: bool=False, nsfl:bool=False, category: str="meme,image,vex,art,other", lgbt: bool=True, political: bool=True, onlynsfw: bool=False):
    if onlynsfw == False:
        _nsfw = [False]
    else:
        _nsfw = []
    _nsfl = [False]
    _unsafe = [False]
    _lgbt = [False]
    _politcal = [False]
    split_category = category.split(",")
    if nsfw:
        _nsfw.append(True)
    if nsfl:
        _nsfl.append(True)
    if unsafe:
        _unsafe.append(True)
    if lgbt:
        _lgbt.append(True)
    if political:
        _politcal.append(True)
    files = Image.select().where(Image.nsfw.in_(_nsfw) & Image.nsfl.in_(_nsfl) & Image.unsafe.in_(_unsafe) & Image.lgbt.in_(_lgbt) & Image.political.in_(_politcal) & Image.category.in_(split_category))
    return {'matching query': files.count()}
