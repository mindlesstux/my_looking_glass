from fastapi import FastAPI, Query, Path, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Optional, Union
from uuid import UUID
import datetime
import glob
import os
import json
import uuid
#from sympy import limit
import uvicorn

# A bit of a hack but works just in case running manually to develop/debug
config={}
config['RESULT_PATH'] = os.getenv('RESULT_PATH',default="./result_files")
config['BIN_PATH'] = os.getenv('BIN_PATH',default="./bin")
config['WEBGUI_PATH'] = os.getenv('WEBGUI_PATH',default='./webinterface')
config['HEALTH_CRON'] = int(os.getenv('HEALTH_CRON',default=15))
config['HEALTH_CRON_COUNT'] = int(0)
config['SHOW_DEBUG_THINGS'] = False
config['path_static'] = "%s/static" % (config['WEBGUI_PATH'])
config['path_templates'] = "%s/templates" % (config['WEBGUI_PATH'])
templates = Jinja2Templates(directory=config['path_templates'] )

# ================================================================================================================================================================
# This is for the fastapi docs pages
# ================================================================================================================================================================

description = """
This is a simple attempt at building a looking glass that uses remote linux (for now) to execute some basic tests.
"""

tags_metadata = [
    {
        "name": "Tests",
        "description": "Tests that can be queue'ed up/executed, and get back the results file to query for.",
    },
    {
        "name": "Tests In Development",
        "description": "Tests that are being developed, and could change at any time",
    },
    {
        "name": "Tests In Planning",
        "description": "Tests that are planned to be developed in the future",
    },
]

app = FastAPI(
    title="My Looking Glass",
    description=description,
    version="10002",
    contact={
        "name": "MindlessTux",
        "url": "https://github.com/mindlesstux/my_looking_glass",
    },
    openapi_tags=tags_metadata
)

# ================================================================================================================================================================
# Random functions used later
# ================================================================================================================================================================

def indexExists(list,index):
    if 0 <= index < len(list):
        return True
    else:
        return False

# ================================================================================================================================================================
# /result
# ================================================================================================================================================================

@app.get(
    "/result", 
    tags=["Tests In Development"],
    summary="Fetch a result json via GUI",
    description="Fetches a result json file via GUI.",
    response_class=HTMLResponse,
    )
async def result(
        request: Request,
        fetch_uuid: Union[UUID, None] = None,
    ):
    data = None
    files = None
    if fetch_uuid is not None:
        for file in glob.glob('%s/*%s.json' % (config['RESULT_PATH'], fetch_uuid)):
            f = open(file)
            data = json.loads(f.read())
            f.close()
    else:
        files = {}
        file_list = sorted(glob.iglob('%s/*.json' % (config['RESULT_PATH'])), key=os.path.getctime, reverse=True)
        for x in range(0, 9):
            if indexExists(file_list, x):
                path = file_list[x]
                basename = os.path.basename(path)
                filesize = os.stat(path)
                m_time = os.path.getmtime(path)
                dt_m = datetime.datetime.fromtimestamp(m_time)
                c_time = os.path.getctime(path)
                dt_c = datetime.datetime.fromtimestamp(c_time)
                files[basename] = {}
                files[basename]['dt_c'] = dt_c
                files[basename]['dt_m'] = dt_m
                files[basename]['filesize_bytes'] = filesize.st_size
                files[basename]['uuid'] = str(str(basename).split(sep="_")[1]).split(sep=".")[0]

    return templates.TemplateResponse("result.html", {"request": request, "config": config, "segment": 'result', "uuid": fetch_uuid, "data": data, "recent_files": files })

# ================================================================================================================================================================
# /result/raw
# ================================================================================================================================================================

@app.get(
    "/result/raw", 
    tags=["Tests In Development"],
    summary="Fetch a raw result json",
    description="Fetches a raw result json file.",
    )
async def result_raw(
        fetch_uuid: UUID,
    ):
    data = {}
    for file in glob.glob('%s/*%s.json' % (config['RESULT_PATH'], fetch_uuid)):
        f = open(file)
        data = json.loads(f.read())
        f.close()
    
    return data

@app.post(
    "/result/raw", 
    tags=["Tests In Development"],
    summary="Fetch a raw result json",
    description="Fetches a raw result json file.",
    )
async def result_raw(
        fetch_uuid: UUID,
    ):
    data = {}
    for file in glob.glob('%s/*%s.json' % (config['RESULT_PATH'], fetch_uuid)):
        f = open(file)
        data = json.loads(f.read())
        f.close()
    
    return data

# ================================================================================================================================================================
# /run/ping
# ================================================================================================================================================================


@app.get(
    "/run/ping", 
    response_class=HTMLResponse,
    include_in_schema=False)
async def read_item(request: Request):
    return templates.TemplateResponse("tool-ping-get.html", {"request": request, "config": config, "segment": 'tool-ping'})


@app.post(
    "/run/ping", 
    tags=["Tests In Development"],
    summary="Run a ping test",
    description="Run a simple ping test.",
    )
async def run_ping(
        dst_location: Union[str, None] = Query(
            title="Destination Location",
            description="The target location that the test will be running to."
        ),
        src_location: Union[str, None] = Query(
            default="localhost",
            title="Source Location",
            description="The location that will be SSH'ed into and the test run from.", 
        ),
        ipv4: Union[bool, None] = Query(default=False, title="Force IPv4", description='Force the --ipv4 flag passed to the ping command.'),
        ipv6: Union[bool, None] = Query(default=False, title="Force IPv6", description='Force the --ipv6 flag passed to the ping command.'),
        count: Union[int, None] = Query(default=10, ge=1, le=100, description='The number of pings to run')
    ):
    uuid_str = str(uuid.uuid1())
    cmd = "python3 %s/lg_cmd_ping.py --uuid=%s %s %s > /dev/null 2>&1" % (config['BIN_PATH'], uuid_str, src_location, dst_location)
    stream = os.popen(cmd)
    return "{uidid: %s, url: '/result?uuidid=%s'}" % (uuid_str, uuid_str)

# ================================================================================================================================================================
# /run/mtr
# ================================================================================================================================================================

@app.get(
    "/run/mtr", 
    tags=["Tests In Planning"],
    )
async def run_mtr():
    return False

# ================================================================================================================================================================
# /run/whois
# ================================================================================================================================================================

@app.get(
    "/run/whois", 
    tags=["Tests In Planning"],
    )
async def run_whois():
    return False

# ================================================================================================================================================================
# /run/curl
# ================================================================================================================================================================

@app.get(
    "/run/curl", 
    tags=["Tests In Planning"],
    )
async def run_curl():
    return False

# ================================================================================================================================================================
# /run/openssl
# ================================================================================================================================================================

@app.get(
    "/run/openssl", 
    tags=["Tests In Planning"],
    )
async def run_openssl():
    return False

# ================================================================================================================================================================
# /run/nmap
# ================================================================================================================================================================

@app.get(
    "/run/nmap", 
    tags=["Tests In Planning"],
    )
async def run_nmap():
    return False

# ================================================================================================================================================================
# /run/snmp
# ================================================================================================================================================================

@app.get(
    "/run/snmp", 
    tags=["Tests In Planning"],
    )
async def run_snmp():
    return False

# ================================================================================================================================================================
# /static
# ================================================================================================================================================================

app.mount("/static", StaticFiles(directory=config['path_static']), name="static")

# ================================================================================================================================================================
# /
# ================================================================================================================================================================

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def read_item(request: Request):
    return templates.TemplateResponse("start.html", {"request": request, "config": config, "segment": 'index'})


# ================================================================================================================================================================
# /flipDebug
# ================================================================================================================================================================

@app.get("/flipDebug", response_class=HTMLResponse, include_in_schema=False)
async def read_item(request: Request):
    if config['SHOW_DEBUG_THINGS'] == False:
        config['SHOW_DEBUG_THINGS'] = True
    else:
        config['SHOW_DEBUG_THINGS'] = False
    return RedirectResponse("/")


# ================================================================================================================================================================
# /healthcheck
# ================================================================================================================================================================

@app.get("/healthcheck", response_class=HTMLResponse, include_in_schema=False)
async def read_item(request: Request):
    config['HEALTH_CRON_COUNT'] = config['HEALTH_CRON_COUNT'] + 1
    if config['HEALTH_CRON_COUNT'] >= config['HEALTH_CRON']:
        # TODO: handle some cron tasks
        config['HEALTH_CRON_COUNT'] = 0
    return templates.TemplateResponse("healthcheck.html", {"request": request, "config": config, "segment": 'debug-healthcheck'})

# ================================================================================================================================================================
# /debug
# ================================================================================================================================================================

@app.get("/debug", response_class=HTMLResponse, include_in_schema=False)
async def read_item(request: Request):

    return templates.TemplateResponse("debug.html", {"request": request, "config": config, "segment": 'debug-stuff'})

# ================================================================================================================================================================
# Main entry point
# ================================================================================================================================================================

if __name__ == '__main__':
    uvicorn.run(app, port=9180, host='0.0.0.0')
