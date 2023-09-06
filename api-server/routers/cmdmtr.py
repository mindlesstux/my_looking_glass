from config import config
from fastapi import APIRouter, HTTPException, FastAPI, Query, Path, Request, APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel
from typing import Optional, Union
from uuid import UUID
import json
import os
import uuid

router = APIRouter()

# ================================================================================================================================================================
# Function for ping tests to kick
# ================================================================================================================================================================

def kick_off_mtr(uuid_str = None, dst_location=None, src_location="NopeDIEOUT", ip_family_ipv4 = False, ip_family_ipv6 = False, ping_count=10, redirect_to_null=False):

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
    cmd = "python3 %s/lg_cmd_mtr.py --uuid=%s %s --count=%s %s %s %s" % (config.config['BIN_PATH'], uuid_str, ip_family, ping_count, src_location, dst_location, redirect)
    print("          CMD: %s" %(cmd))

    stream = os.popen(cmd)

    return_str = '{"uidid": "%s", "url": "/result?fetch_uuid=%s"}' % (uuid_str, uuid_str)

    return return_str

# ================================================================================================================================================================
# /run/mtr-via-gui
# ================================================================================================================================================================

class TestOfMTR(BaseModel):
        dst_location: str
        src_location: str
        ipv4: Union[bool, None] = False
        ipv6: Union[bool, None] = False
        count: Union[int, None] = 10 

@router.post("/run/mtr-via-gui",
    tags=["Tests In Development"],
    summary="Run MTR",
    description="Run MTR",
    include_in_schema=False,
    )
async def create_item(body: TestOfMTR):

    # TODO: some more logic on the input and sanitization of the inputs.

    return_str = kick_off_mtr(dst_location=body.dst_location, src_location=body.src_location, ip_family_ipv4=body.ipv4, ip_family_ipv6=body.ipv6, ping_count=body.count)
    return return_str

# ================================================================================================================================================================
# /run/mtr
# ================================================================================================================================================================

@router.get(
    "/run/mtr", 
    response_class=HTMLResponse,
    include_in_schema=False)
async def read_item(request: Request):
    return config.templates.TemplateResponse("tool-ping-get.html", {"request": request, "config": config.config, "segment": 'tool-ping'})


@router.post(
    "/run/mtr", 
    tags=["Tests In Development"],
    summary="Run MTR",
    description="Run MTR",
    )
async def run_mtr(
        dst_location: Union[str, None] = Query(
            title="Destination Location",
            description="The target location that the test will be running to."
        ),
        src_location_enum: config.SrcLocationEnum = Query(
            title="Source Location",
            description="The location that will be SSH'ed into and the test run from.",
            default=config.srv_enum_firstvalue
        ),
        ipv4: Union[bool, None] = Query(default=False, title="Force IPv4", description='Force the --ipv4 flag passed to the ping command.'),
        ipv6: Union[bool, None] = Query(default=False, title="Force IPv6", description='Force the --ipv6 flag passed to the ping command.'),
        count: Union[int, None] = Query(default=10, ge=1, le=100, description='The number of pings to run')
    ):

    return_str = kick_off_mtr(dst_location=dst_location, src_location=src_location_enum.name, ip_family_ipv4=ipv4, ip_family_ipv6=ipv6, ping_count=count)
    return return_str