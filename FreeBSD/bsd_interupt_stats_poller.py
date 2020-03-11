#!/usr/bin/env python3

# 3/10/2020
# Updated for python3
# A Simple sysctl to telegraf plugin for freebsd's vmstats

from freebsd_sysctl import Sysctl as sysctl
import subprocess as sp
import re
import json
import pprint as pp
import sys

hostname = sysctl("kern.hostname").value
vmstat_data = {}
points_vmstat = {}

vmstat_output = sp.check_output(["vmstat", "-i", "--libxo", "json", "/dev/null"],universal_newlines=True)

vmstat_data = json.loads(vmstat_output)

pp.pprint(type(vmstat_data["interrupt-statistics"]["interrupt"]))

def points_to_influx(points,nic):
    field_tags= ",".join(["{k}={v}".format(k=str(x[0]), v=x[1]) for x in list(points.items())])
    print(("bsd_nic_stats,interface={} {}").format(nic,field_tags))

def gen_points(nic):
    points = {}
    for  i in nic:
        raw_var =  str(i.name).replace(">", "")
        long_oid = (raw_var).lstrip().replace(".","_")
        split_oid = long_oid.split("_")
        oid = (long_oid).replace(split_oid[0]+"_"+split_oid[1]+"_"+split_oid[2]+"_","").lstrip()
        if oid[0] == '%':
            oid = oid.replace('%','')
        try:
            points[oid] = int(i.value)
        except ValueError:
             points[oid] = "\"" + str(i.value) + "\""
             continue
    return points



