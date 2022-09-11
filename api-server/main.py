#from email.mime import base
from enum import Enum
from fastapi import FastAPI, Query, Path, Request
from fastapi.logger import logger
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional, Union
from uuid import UUID
import datetime
import glob
import logging
import os
import json
import uuid
#from sympy import limit
import uvicorn

# A bit of a hack but works just in case running manually to develop/debug
config={}
config['BASE_PATH'] = os.getenv('BASE_PATH', default="/app/")
config['RESULT_PATH'] = os.getenv('RESULT_PATH', default="%s/result_files" % (config['BASE_PATH']))
config['BIN_PATH'] = os.getenv('BIN_PATH', default="%s/bin" % (config['BASE_PATH']))
config['WEBGUI_PATH'] = os.getenv('WEBGUI_PATH', default="%s/webinterface" % (config['BASE_PATH']))
config['CONFIGJSON_PATH'] = os.getenv('CONFIGJSON_PATH', default="%s/config.json" % (config['BASE_PATH']))
config['path_static'] = "%s/static" % (config['WEBGUI_PATH'])
config['path_templates'] = "%s/templates" % (config['WEBGUI_PATH'])

config['HEALTH_CRON'] = int(os.getenv('HEALTH_CRON',default=15))
config['HEALTH_CRON_COUNT'] = int(0)
config['SHOW_DEBUG_THINGS'] = False
config['CAPABILITIES_DEFAULT'] = bool(os.getenv('CAPABILITIES_DEFAULT',default=False))

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
gunicorn_logger = logging.getLogger('gunicorn.error')
logger.handlers = gunicorn_logger.handlers
if __name__ != "main":
    logger.setLevel(gunicorn_logger.level)
else:
    logger.setLevel(logging.DEBUG)


# ================================================================================================================================================================
# Random functions used later
# ================================================================================================================================================================

def indexExists(list,index):
    if 0 <= index < len(list):
        return True
    else:
        return False

# Load the config.json
srv_config = {}
with open(config['CONFIGJSON_PATH']) as json_file:
    srv_config = json.load(json_file)

# Generate an ENUM based out of config.json
srv_enum_values = {}
srv_enum_firstvalue = ""
for k in srv_config['ssh_hosts'].keys():
    srv_enum_values[str(k)]=str(k)
    if srv_enum_firstvalue == "":
        srv_enum_firstvalue = k
SrcLocationEnum = Enum("TypeEnum", srv_enum_values)

# ================================================================================================================================================================
# /result
# ================================================================================================================================================================

@app.get(
    "/result", 
    tags=["Tests In Development"],
    summary="Fetch a result json via GUI",
    description="Fetches a result json file via GUI.",
    response_class=HTMLResponse,
    include_in_schema=False
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

                tmp_file_data = {}
                for tmp_file in glob.glob(path):
                    f = open(tmp_file)
                    tmp_file_data = json.loads(f.read())
                    f.close()

                files[basename] = {}
                files[basename]['dt_c'] = dt_c
                files[basename]['dt_m'] = dt_m
                files[basename]['filesize_bytes'] = filesize.st_size
                files[basename]['uuid'] = str(str(basename).split(sep="_")[1]).split(sep=".")[0]
                if 'complete' in tmp_file_data:
                    files[basename]['process_complete'] = tmp_file_data['complete']
                else:
                    files[basename]['process_complete'] = None
                if 'status' in tmp_file_data:
                    files[basename]['status'] = tmp_file_data['status']
                else:
                    files[basename]['status'] = None

    return templates.TemplateResponse("result.html", {"request": request, "config": config, "segment": 'result', "uuid": fetch_uuid, "data": data, "recent_files": files })

# ================================================================================================================================================================
# /result/raw
# ================================================================================================================================================================

@app.get(
    "/result/raw", 
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
# Function for ping tests to kick
# ================================================================================================================================================================

def kick_off_ping(uuid_str = None, dst_location=None, src_location="NopeDIEOUT", ip_family_ipv4 = False, ip_family_ipv6 = False, ping_count=10, redirect_to_null=False):

    #if uuid_str == None:
    uuid_str = str(uuid.uuid1())

    ip_family = ""
    if ip_family_ipv4 == True and ip_family_ipv6 == False:
        ip_family = "--ipv4"
    if ip_family_ipv4 == False and ip_family_ipv6 == True:
        ip_family = "--ipv6"

    redirect=""
    if redirect_to_null:
        redirect = "> /dev/null 2>&1"

    print("          Trying to ping %s from %s" % (dst_location, src_location))
    cmd = "python3 %s/lg_cmd_ping.py --uuid=%s %s --count=%s %s %s %s" % (config['BIN_PATH'], uuid_str, ip_family, ping_count, src_location, dst_location, redirect)
    print("          CMD: %s" %(cmd))
    new_file = "ping_%s.json" % (uuid_str);
    write_blank_result(file_to_blank=new_file)
    stream = os.popen(cmd)

    return_str = '{"uidid": "%s", "url": "/result?fetch_uuid=%s"}' % (uuid_str, uuid_str)

    return return_str

# ================================================================================================================================================================
# /run/ping-via-gui
# ================================================================================================================================================================

class TestOfPing(BaseModel):
        dst_location: str
        src_location: str
        ipv4: Union[bool, None] = False
        ipv6: Union[bool, None] = False
        count: Union[int, None] = 10 

@app.post("/run/ping-via-gui",
    tags=["Tests In Development"],
    summary="Run a ping test.  Body encoded, not url encoded",
    description="Run a simple ping test.",
    )
async def create_item(body: TestOfPing):

    # TODO: some more logic on the input and sanitization of the inputs.

    return_str = kick_off_ping(dst_location=body.dst_location, src_location=body.src_location, ip_family_ipv4=body.ipv4, ip_family_ipv6=body.ipv6, ping_count=body.count)
    return return_str

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
    summary="Run a ping test.  Not body encoded, but url",
    description="Run a simple ping test.",
    )
async def run_ping(
        dst_location: Union[str, None] = Query(
            title="Destination Location",
            description="The target location that the test will be running to."
        ),
        src_location_enum: SrcLocationEnum = Query(
            title="Source Location",
            description="The location that will be SSH'ed into and the test run from.",
            default=srv_enum_firstvalue
        ),
        ipv4: Union[bool, None] = Query(default=False, title="Force IPv4", description='Force the --ipv4 flag passed to the ping command.'),
        ipv6: Union[bool, None] = Query(default=False, title="Force IPv6", description='Force the --ipv6 flag passed to the ping command.'),
        count: Union[int, None] = Query(default=10, ge=1, le=100, description='The number of pings to run')
    ):

    return_str = kick_off_ping(dst_location=dst_location, src_location=src_location_enum.name, ip_family_ipv4=ipv4, ip_family_ipv6=ipv6, ping_count=count)
    return return_str

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
# /test-sources
# ================================================================================================================================================================

@app.get("/test-sources", response_class=HTMLResponse, include_in_schema=False)
async def read_item(request: Request):

    return templates.TemplateResponse("test-sources.html", {"request": request, "config": config, "srv_config": srv_config, "segment": 'test-sources'})

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
