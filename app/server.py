from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from io import BytesIO
import uvicorn, asyncio, aiohttp, requests

from fastai import *
from fastai.vision import *

export_file_url = 'https://drive.google.com/uc?export=download&id=1O-Y6qvMZXybgA_TnM9yD134WLCOnf57Z'
export_file_name = 'export.pkl'
path = Path(__file__).parent/'models'

app = FastAPI()
app.mount('/app/static', StaticFiles(directory='./app/static'), name="static")
templates = Jinja2Templates(directory="./app/templates")
learner = None


async def download_file(url, dest):
    if dest.exists(): return
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        async with session.get(url) as response:
            data = await response.read()
            with open(dest, 'wb') as f: f.write(data)


@app.on_event('startup')
async def setup_learner():
    global learner
    print('Setup')
    await download_file(export_file_url, path/export_file_name)
    try:
        learner = load_learner(path, export_file_name)
    except RuntimeError as e:
        if len(e.args) > 0:
            print(e)
    print('Finish setting up learner')


@app.get('/')
async def root(request: Request):
    return templates.TemplateResponse("index.html", {'request':request})


@app.post('/analyze')
async def analyze(request: Request):
    data = await request.form()
    if data['file'] == 'undefined':
        return {'result': 'undefined'}

    img_bytes = await (data['file'].read())
    img = open_image(BytesIO(img_bytes))
    prediction = learner.predict(img)
    return {'result': str(prediction[0])}


if __name__ == '__main__':
    if 'serve' in sys.argv: uvicorn.run(app=app, host='0.0.0.0', port=5042)
