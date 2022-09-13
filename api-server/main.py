from enum import Enum
from fastapi import FastAPI, Query, Path, Request, APIRouter
from fastapi.logger import logger
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional, Union
from uuid import UUID
from routers import quack, result, cmdping, cmdmtr, cmdcurl, cmdnmap, cmdopenssl, cmdsnmp, cmdwhois
from config import config
import datetime
import glob
import logging
import os
import json
import uuid
import uvicorn

app = FastAPI(
    title="My Looking Glass",
    description=config.description,
    version="10002",
    contact={
        "name": "MindlessTux",
        "url": "https://github.com/mindlesstux/my_looking_glass",
    },
    openapi_tags=config.tags_metadata
)
app.include_router(quack.router)
app.include_router(result.router)
app.include_router(cmdping.router)
app.include_router(cmdmtr.router)
app.include_router(cmdnmap.router)
app.include_router(cmdopenssl.router)
app.include_router(cmdsnmp.router)
app.include_router(cmdwhois.router)
app.include_router(cmdcurl.router)

gunicorn_logger = logging.getLogger('gunicorn.error')
logger.handlers = gunicorn_logger.handlers
if __name__ != "main":
    logger.setLevel(gunicorn_logger.level)
else:
    logger.setLevel(logging.DEBUG)


# ================================================================================================================================================================
# /static
# ================================================================================================================================================================

app.mount("/static", StaticFiles(directory=config.config['path_static']), name="static")

# ================================================================================================================================================================
# /
# ================================================================================================================================================================

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def read_item(request: Request):
    return config.templates.TemplateResponse("start.html", {"request": request, "config": config.config, "segment": 'index'})


# ================================================================================================================================================================
# /test-sources
# ================================================================================================================================================================

@app.get("/test-sources", response_class=HTMLResponse, include_in_schema=False)
async def read_item(request: Request):

    return config.templates.TemplateResponse("test-sources.html", {"request": request, "config": config.config, "srv_config": config.srv_config, "segment": 'test-sources'})

# ================================================================================================================================================================
# /flipDebug
# ================================================================================================================================================================

@app.get("/flipDebug", response_class=HTMLResponse, include_in_schema=False)
async def read_item(request: Request):
    if config.config['SHOW_DEBUG_THINGS'] == False:
        config.config['SHOW_DEBUG_THINGS'] = True
    else:
        config.config['SHOW_DEBUG_THINGS'] = False
    return RedirectResponse("/")


# ================================================================================================================================================================
# /healthcheck
# ================================================================================================================================================================

@app.get("/healthcheck", response_class=HTMLResponse, include_in_schema=False)
async def read_item(request: Request):
    config.config['HEALTH_CRON_COUNT'] = config.config['HEALTH_CRON_COUNT'] + 1
    if config.config['HEALTH_CRON_COUNT'] >= config.config['HEALTH_CRON']:
        # TODO: handle some cron tasks
        config.config['HEALTH_CRON_COUNT'] = 0
    return config.templates.TemplateResponse("healthcheck.html", {"request": request, "config": config.config, "segment": 'debug-healthcheck'})

# ================================================================================================================================================================
# /debug
# ================================================================================================================================================================

@app.get("/debug", response_class=HTMLResponse, include_in_schema=False)
async def read_item(request: Request):

    return config.templates.TemplateResponse("debug.html", {"request": request, "config": config.config, "segment": 'debug-stuff'})

# ================================================================================================================================================================
# Main entry point
# ================================================================================================================================================================

if __name__ == '__main__':
    uvicorn.run(
        app,
        port=9180,
        host='0.0.0.0',
        proxy_headers=True,
        forwarded_allow_ips='*'
        )
