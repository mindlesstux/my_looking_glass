from dotenv import load_dotenv
from fastapi import FastAPI, Query, Path
from fastapi.staticfiles import StaticFiles
from typing import Union
import uvicorn

load_dotenv()

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
    version="0.0.1",
    contact={
        "name": "MindlessTux",
        "url": "https://github.com/mindlesstux/my_looking_glass",
    },
    openapi_tags=tags_metadata
)
app.mount("/result_files", StaticFiles(directory="result_files"), name="result_files")

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
    return False

@app.get(
    "/run/mtr", 
    tags=["Tests In Planning"],
    )
async def run_mtr():
    return False

@app.get(
    "/run/whois", 
    tags=["Tests In Planning"],
    )
async def run_whois():
    return False

@app.get(
    "/run/curl", 
    tags=["Tests In Planning"],
    )
async def run_curl():
    return False

@app.get(
    "/run/openssl", 
    tags=["Tests In Planning"],
    )
async def run_openssl():
    return False

@app.get(
    "/run/nmap", 
    tags=["Tests In Planning"],
    )
async def run_nmap():
    return False

@app.get(
    "/run/snmp", 
    tags=["Tests In Planning"],
    )
async def run_snmp():
    return False

if __name__ == '__main__':
    uvicorn.run(app, port=9180, host='0.0.0.0')