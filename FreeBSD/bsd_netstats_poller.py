#!/usr/bin/env python3

# 3/21/2021
# Updated for python3
# A Simple sysctl to telegraf plugin for freebsd's netstats ip info

from freebsd_sysctl import Sysctl as sysctl
import subprocess as sp
import re
import json
import sys
import pprint as pp

hostname = sysctl("kern.hostname").value
netstat_data = {}
points_netstat = {}

netstat_output = sp.check_output(["netstat", "-s", "-p", "ip", "--libxo", "json", "/dev/null"],universal_newlines=True)

netstat_data = json.loads(netstat_output)

for x in netstat_data["statistics"]:
  for k,v in netstat_data["statistics"][x].items():
     points_netstat[k] = v

def points_to_influx(points):
    field_tags= ",".join(["{k}={v}".format(k=str(x[0]), v=x[1]) for x in list(points_netstat.items())])
    print(("bsd_netstat,type=netstat {}").format(field_tags))


points_to_influx(points_netstat)






