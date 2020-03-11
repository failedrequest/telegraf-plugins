#!/usr/bin/env python3

# 3/10/2020
# Updated for python3
# A Simple sysctl to telegraf plugin for freebsd's vmstats to get interupts

from freebsd_sysctl import Sysctl as sysctl
import subprocess as sp
import re
import json
import sys

hostname = sysctl("kern.hostname").value
vmstat_data = {}
points_vmstat = {}

vmstat_output = sp.check_output(["vmstat", "-i", "--libxo", "json", "/dev/null"],universal_newlines=True)

vmstat_data = json.loads(vmstat_output)

for x in enumerate(vmstat_data["interrupt-statistics"]["interrupt"]):
  normal_key_name = (x[1]["name"]).strip().replace(".","_").replace(":","_").replace(" ","")
  points_vmstat[normal_key_name] = x[1]["total"]

def points_to_influx(points):
    field_tags= ",".join(["{k}={v}".format(k=str(x[0]), v=x[1]) for x in list(points_vmstat.items())])
    print(("bsd_interupt_stats,{}").format(field_tags))


points_to_influx(points_vmstat)






