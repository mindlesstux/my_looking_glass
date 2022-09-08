from textwrap import dedent
import os
from tkinter import EXCEPTION
import paramiko
import json
import argparse
import pingparsing
import traceback

# A bit of a hack but works just in case running manually to develop/debug
config={}
config['CONFIGJSON_PATH'] = os.getenv('CONFIGJSON_PATH',default="./config.json")
config['RESULT_PATH'] = os.getenv('RESULT_PATH',default="./result_files")
config['BIN_PATH'] = os.getenv('BIN_PATH',default="/app/bin")

parser = argparse.ArgumentParser(prog='lg_cmd_ping.py', description="This is a wrapper script to ping to be called from an API server.")
cmd = "ping"

# Load the config.json
srv_config = {}
with open('config.json') as json_file:
    srv_config = json.load(json_file)

# Read our cmdline args
parser.add_argument("-u", "--uuid", help="UUID for the test", default=None)
parser.add_argument("-4", "--ipv4", help="Force IPv4", action="store_true", default=False)
parser.add_argument("-6", "--ipv6", help="Force IPv6", action="store_true", default=False)
parser.add_argument("--ping6", help="Use ping6 for IPv6", action="store_true", default=False)
parser.add_argument("-c", "--count", type=int, default=10, help="Number of pings, default 10")
parser.add_argument("sourcehost", metavar='sourcehost', nargs=1, default="localhost", help="The source host")
parser.add_argument("targethost", metavar='targethost', nargs=1, default="localhost", help="The target host")
args = parser.parse_args()

# To write the json multiple times
def write_result(return_dict):
    if args.uuid is not None:
        filename="%s/ping_%s.json" % (config['RESULT_PATH'], args.uuid)
        f = open(filename, "w")
        f.write(json.dumps(return_dict))
        f.close()
    else:
        print("%s" % json.dumps(return_dict))

try:
    return_dict = {}
    return_dict['type'] = "ping"
    return_dict['ping_target'] = args.targethost[0]
    return_dict['ping_source'] = args.sourcehost[0]
    return_dict['complete'] = False
    return_dict['status'] = "processing"
    write_result(return_dict)

    # Build the command
    if args.ping6:
        cmd = "ping6"
    else:
        if args.ipv4 and not args.ipv6:
            cmd = cmd + " -4"
        if args.ipv6 and not args.ipv4:
            cmd = cmd + " -6"
    if args.count:
        cmd = cmd + " -c %s" % args.count
    if args.targethost:
        cmd = cmd + " %s" % args.targethost[0]

    # Dump to this point
    print("%s" % (cmd))
    return_dict['cmd'] = cmd
    return_dict['status'] = "connecting..."
    write_result(return_dict)

    # SSH for now using username and password
    client = paramiko.client.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    parser = pingparsing.PingParsing()
    #host = args.sourcehost[0]
    #client.connect(host, username=config['USERNAME'], password=config['PASSWORD'])
    ssh_host = srv_config['ssh_hosts'][args.sourcehost[0]]['hostname']
    ssh_user = srv_config['ssh_creds'][srv_config['ssh_hosts'][args.sourcehost[0]]['ssh_cred']]['username']
    ssh_pass = srv_config['ssh_creds'][srv_config['ssh_hosts'][args.sourcehost[0]]['ssh_cred']]['password']

    return_dict['status'] = "connecting..."
    write_result(return_dict)

    client.connect(ssh_host, username=ssh_user, password=ssh_pass)
    output=""

    # Dump to this point
    return_dict['status'] = "connected"
    write_result(return_dict)


    return_dict['status'] = "running command"
    write_result(return_dict)

    stdin, stdout, stderr = client.exec_command(cmd)
    stdout=stdout.readlines()
    strblob = ''.join(stdout)
    client.close()
    stdin.close()
    stderr.close()

    return_dict['status'] = "parsing"
    write_result(return_dict)

    stats = parser.parse(dedent(strblob))

    return_dict['ping_stats'] = stats.as_dict()
    return_dict['ping_parsedraw'] = stats.icmp_replies
    return_dict['raw'] = strblob

    # Write for the final time
    return_dict['complete'] = True
    return_dict['status'] = "complete"
    write_result(return_dict)
except Exception as e:
    return_dict['complete'] = True
    return_dict['status'] = "failed"
    print("Exception:")
    print("   ", e)
    print(traceback.print_exc())
    return_dict['exception'] = str(e)
    write_result(return_dict)