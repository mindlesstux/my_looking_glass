from config import config
from fastapi import APIRouter, HTTPException, FastAPI, Query, Path, Request, APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import Optional, Union
from uuid import UUID
import datetime
import glob
import json
import os

router = APIRouter()

# ================================================================================================================================================================
# /result
# ================================================================================================================================================================

@router.get(
    "/result", 
    tags=["Tests In Development"],
    summary="Fetch a result json via GUI",
    description="Fetches a result json file via GUI.",
    include_in_schema=False
    )
async def result2(
        request: Request,
        fetch_uuid: Union[UUID, None] = None,
    ):
    data = None
    files = None
    if fetch_uuid is not None:
        for file in glob.glob('%s/*%s.json' % (config.config['RESULT_PATH'], fetch_uuid)):
            f = open(file)
            data = json.loads(f.read())
            f.close()
    else:
        files = {}
        file_list = sorted(glob.iglob('%s/*.json' % (config.config['RESULT_PATH'])), key=os.path.getctime, reverse=True)
        for x in range(0, 9):
            if config.indexExists(file_list, x):
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

    return config.templates.TemplateResponse("result.html", {"request": request, "config": config.config, "segment": 'result', "uuid": fetch_uuid, "data": data, "recent_files": files })

# ================================================================================================================================================================
# /result/raw
# ================================================================================================================================================================

@router.get(
    "/result/raw", 
    summary="Fetch a raw result json",
    description="Fetches a raw result json file.",
    )
async def result2_raw_get(
        fetch_uuid: UUID,
    ):
    data = {}
    for file in glob.glob('%s/*%s.json' % (config.config['RESULT_PATH'], fetch_uuid)):
        f = open(file)
        data = json.loads(f.read())
        f.close()
    
    return data

@router.post(
    "/result/raw", 
    summary="Fetch a raw result json",
    description="Fetches a raw result json file.",
    )
async def result2_raw_post(
        fetch_uuid: UUID,
    ):
    data = {}
    for file in glob.glob('%s/*%s.json' % (config.config['RESULT_PATH'], fetch_uuid)):
        f = open(file)
        data = json.loads(f.read())
        f.close()
    
    return data