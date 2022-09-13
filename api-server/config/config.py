
from enum import Enum
from fastapi.templating import Jinja2Templates
import json
import os

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