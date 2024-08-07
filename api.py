from fastapi import FastAPI, Request, Form
from fastapi.responses import PlainTextResponse
from fastapi.responses import FileResponse, RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from playhouse.postgres_ext import *
from typing import Annotated
app = FastAPI()
import os
import json
from playhouse.shortcuts import model_to_dict, dict_to_model
import random
import time
import requests
from pydantic import BaseModel as otherBaseModel

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
        if matches > 0:
            filtered.append([file.filename, matches])
    if len(filtered) < 1:
        return {'error': 'no matching files'}
    ranked = sorted(filtered, key=lambda x:x[1], reverse=True)
    if pos > 0:
        pos -= 1
    else:
        pos = 0
    if pos+1 > len(filtered):
        return {'error': 'no matching files'}
    response_file = ranked[pos][0]
    return FileResponse(f"img/{response_file}")

@app.get("/random")
async def random_img(tags: str="", nsfw: bool=False, unsafe: bool=False, nsfl:bool=False, category: str="meme,image,vex,art,other", lgbt: bool=True, political: bool=True, onlynsfw: bool=False):
    split_tags = tags.lower().split(",")
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
    filtered = list()
    for file in files:
        matches = 0
        for i in file.tags:
            matches += split_tags.count(i)
        if matches > 0 or tags=="":
            filtered.append([file.filename, matches])
    if len(filtered) < 1:
        return {'error': 'no matching files'}
    random.shuffle(filtered)
    response_file = filtered[0][0]
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


class Login(otherBaseModel):
    auth_bearer: str
    auth_token: str 
    device_name: str
    device_uuid: str 
    email: str
    rdm_endpoint: str


@app.get("/atlas/agent", response_class=PlainTextResponse)
def proxy_agent(request: Request):
    app_ver = request.headers.get('App-Version-Code')
    if app_ver is None:
        app_ver = "22071801"
    proxy_headers = {
        'User-Agent': 'khttp/1.0.0-SNAPSHOT',
        'App-Version-Code': app_ver
    }
    r = requests.get("https://discovery.pokemod.dev/atlas/agent", headers=proxy_headers)
    response_text = r.text
    print(app_ver)
    print(r.raw)
    return response_text

device_tokens = dict()
@app.post("/atlas/auth/device/login")
def fake_login(login: Login):
    snowflake = str(int(time.time()))+str(random.randint(11111,99999))
    device_tokens[snowflake] = {
        "auth_bearer": login.auth_bearer,
        "auth_token": login.auth_token ,
        "device_name": login.device_name,
        "device_uuid": login.device_uuid ,
        "email": login.email,
        "rdm_endpoint": login.rdm_endpoint,
        "snowflake": snowflake
    }
    return {
        "auth_token": snowflake,
        "refresh_token": snowflake,
        "config": {
            "auth_bearer": login.auth_bearer,
            "device_name": login.device_name,
            "rdm_endpoint": login.rdm_endpoint
        }
    }

@app.get("/pokemod_tutorials/ios")
def ios():
    return RedirectResponse("https://www.youtube.com/watch?v=dQw4w9WgXcQ")


@app.get("/products/pride-collection-martingale-necklace")
def necklace():
    return FileResponse("img/necklace.html")
    # with open("img/necklace.html") as f:
    #     content = f.read()
    #     return HTMLResponse(content=content, status_code=200)

@app.post("/trafficlight")
def trafficlight(data: Annotated[str, Form()]):
    data_json = json.loads(data)
    r = requests.post("http://5.78.81.243:3335", json=data_json)
    print(r.status_code, r.text)