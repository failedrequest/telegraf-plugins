#!/usr/bin/env python3

# 3/10/2020
# Updated for python3
# A Simple sysctl to telegraf plugin for freebsd's nic sysctls
# Should work with anyting that reports data back as an oid in dev.NIC.INSTANCE.stats 

from freebsd_sysctl import Sysctl as sysctl
import re
#import pprint as pp
import sys

hostname = sysctl("kern.hostname").value
sfxge_data = {}
points_nic0 = {}

if len(sys.argv) == 3:
    nic0 =  sys.argv[1]
    nic1 =  sys.argv[2]
else:
    print(("Usage: {} {} {}").format(sys.argv[0],"sfxge0","sfxge1"))
    sys.exit(127)

nic0a = re.split('(\d)',nic0)
nic1a = re.split('(\d)',nic1)

if nic0a == "sfxge":
     nic0_target = ("dev.{}.{}.stats").format(nic0a[0],nic0a[1])
     nic1_target = ("dev.{}.{}.stats").format(nic1a[0],nic1a[1])
else:     
     nic0_target = ("dev.{}.{}").format(nic0a[0],nic0a[1])
     nic1_target = ("dev.{}.{}").format(nic1a[0],nic1a[1])


nic0_stats = sysctl(nic0_target).children
nic1_stats = sysctl(nic1_target).children

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

points_nic0 = gen_points(nic0_stats)
points_to_influx(points_nic0,nic0)

points_nic1 = gen_points(nic1_stats)
points_to_influx(points_nic1,nic1)


