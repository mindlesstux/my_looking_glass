from textwrap import dedent
import os
import paramiko
import json
import argparse
import pingparsing

config={}
config['USERNAME'] = os.environ['SSH_USERNAME']
config['PASSWORD'] = os.environ['SSH_PASSWORD']
config['SSH_KEY'] = os.environ['SSH_KEY']
config['RESULT_PATH'] = os.environ['RESULT_PATH']
if hasattr(os.environ, 'BIN_PATH'):
    config['BIN_PATH'] = os.environ['BIN_PATH']
else:
    config['BIN_PATH'] = 'bin'

parser = argparse.ArgumentParser(prog='lg_cmd_ping.py', description="This is a wrapper script to ping to be called from an API server.")
cmd = "ping"

parser.add_argument("-u", "--uuid", help="UUID for the test", default=None)
parser.add_argument("-4", "--ipv4", help="Force IPv4", action="store_true", default=False)
parser.add_argument("-6", "--ipv6", help="Force IPv6", action="store_true", default=False)
parser.add_argument("--ping6", help="Use ping6 for IPv6", action="store_true", default=False)
parser.add_argument("-c", "--count", type=int, default=10, help="Number of pings, default 10")
parser.add_argument("sourcehost", metavar='sourcehost', nargs=1, default="localhost", help="The source host")
parser.add_argument("targethost", metavar='targethost', nargs=1, default="localhost", help="The target host")
args = parser.parse_args()

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


print("%s" % (cmd))

client = paramiko.client.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
parser = pingparsing.PingParsing()

host = args.sourcehost[0]

client.connect(host, username=config['USERNAME'], password=config['PASSWORD'])
output=""

stdin, stdout, stderr = client.exec_command(cmd)
stdout=stdout.readlines()
strblob = ''.join(stdout)
client.close()
stdin.close()
stderr.close()
stats = parser.parse(dedent(strblob))
return_dict = {}
return_dict['stats'] = stats.as_dict()
return_dict['raw'] = stats.icmp_replies

if args.uuid is not None:
    filename="%s/ping_%s.json" % (config['RESULT_PATH'], args.uuid)
    f = open(filename, "a")
    f.write(json.dumps(return_dict))
    f.close()