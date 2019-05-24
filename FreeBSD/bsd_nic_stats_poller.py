#!/usr/bin/env python2.7
# Mark Saad  - msaad@lucera.com
# 5/12/2019
# A Simple sysctl to telegraf plugin for freebsd's nic sysctls
# Should work with anyting that reports data back as an oid in dev.NIC.INSTANCE.stats 

import sysctl
import re
import pprint as pp
import time
import sys

sysname = sysctl.filter('kern.hostname')[0]
hostname = sysname.value
sfxge_data = {}
points_nic0 = {}

if len(sys.argv) == 3:
    nic0 =  sys.argv[1]
    nic1 =  sys.argv[2]
else:
    print("Usage: {} {} {}").format(sys.argv[0],"sfxge0","sfxge1")
    sys.exit(127)

nic0a = re.split('(\d)',nic0)
nic1a = re.split('(\d)',nic1)

if nic0a == "sfxge":
     nic0_target = ("dev.{}.{}.stats").format(nic0a[0],nic0a[1])
     nic1_target = ("dev.{}.{}.stats").format(nic1a[0],nic1a[1])
else:     
     nic0_target = ("dev.{}.{}").format(nic0a[0],nic0a[1])
     nic1_target = ("dev.{}.{}").format(nic1a[0],nic1a[1])


nic0_stats = sysctl.filter(nic0_target)
nic1_stats = sysctl.filter(nic1_target)

def points_to_influx(points):
    concat_points = ""
    for x in points.items():
        concat_points += ("{}={},").format(str(x[0]),x[1])
        trim_points = concat_points[:-1]+' '
    return trim_points

def gen_points(nic):
    points = {}
    for  i in range(len(nic)):
        raw_var =  str(nic[i]).replace(">", "")
        split_var = re.split(':',raw_var)
        name = split_var[1].lstrip().split(".")
        long_oid = (split_var[1]).lstrip().replace(".","_")
        split_oid = long_oid.split("_")
        oid = (long_oid).replace(split_oid[0]+"_"+split_oid[1]+"_"+split_oid[2]+"_","").lstrip()
        if oid[0] == '%':
            oid = oid.replace('%','')
        try:
            points[oid] = int(nic[i].value)
        except ValueError:
             #points[oid] = "\"" + str(nic[i].value) + "\""
             continue
    return points


stamp = int(time.time() * 1000)
points_nic0 = gen_points(nic0_stats)
tmp_nic0 = points_to_influx(points_nic0)
print("sfxge_stats,host={},interface={},type=sdn {}{}").format(hostname,nic0,tmp_nic0,stamp)

points_nic1 = gen_points(nic1_stats)
tmp_nic1 = points_to_influx(points_nic1)
print("sfxge_stats,host={},interface={},type=sdn {}{}").format(hostname,nic1,tmp_nic1,stamp)


