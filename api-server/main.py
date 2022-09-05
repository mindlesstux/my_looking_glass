from fastapi import FastAPI, Query, Path, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Union
from uuid import UUID
import glob
import os
import json
import uuid
import uvicorn

# A bit of a hack but works just in case running manually to develop/debug
config={}
config['RESULT_PATH'] = os.getenv('RESULT_PATH',default="/app/result_files")
config['BIN_PATH'] = os.getenv('BIN_PATH',default="/app/bin")
config['WEBGUI_PATH'] = os.getenv('WEBGUI_PATH',default='./webinterface')
config['HEALTH_CRON'] = os.getenv('HEALTH_CRON',default=15)
path_static = "%s/static" % (config['WEBGUI_PATH'])
path_templates = "%s/templates" % (config['WEBGUI_PATH'])
templates = Jinja2Templates(directory=path_templates)

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
    version="10001",
    contact={
        "name": "MindlessTux",
        "url": "https://github.com/mindlesstux/my_looking_glass",
    },
    openapi_tags=tags_metadata
)

# ================================================================================================================================================================
# /result
# ================================================================================================================================================================

@app.get(
    "/result", 
    tags=["Tests In Development"],
    summary="Fetch a result json",
    description="Fetches a result json file.",
    )
async def result(
        uuidid: UUID
    ):
    data = {}
    for file in glob.glob('%s/*%s.json' % (config['RESULT_PATH'], uuidid)):
        f = open(file)
        data = json.loads(f.read())
        f.close()
    
    return data

# ================================================================================================================================================================
# /run/ping
# ================================================================================================================================================================

@app.get(
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

app.mount("/static", StaticFiles(directory=path_static), name="static")

# ================================================================================================================================================================
# /
# ================================================================================================================================================================

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def read_item(request: Request):
    return templates.TemplateResponse("start.html", {"request": request, "config_webgui_path": config['WEBGUI_PATH'], "raw_config": config})

# ================================================================================================================================================================
# /healthcheck
# ================================================================================================================================================================

@app.get("/healthcheck", response_class=HTMLResponse, include_in_schema=False)
async def read_item(request: Request):
    return templates.TemplateResponse("healthcheck.html", {"request": request})

# ================================================================================================================================================================
# Main entry point
# ================================================================================================================================================================

if __name__ == '__main__':
    print(json.dumps(config))
    uvicorn.run(app, port=9180, host='0.0.0.0')
