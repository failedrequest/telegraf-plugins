#!/usr/bin/env python2.7
# Mark Saad  - msaad@lucera.com
# 5/12/2019
# A Simple sysctl to telegraf plugin for freebsd's sfxge driver 

import sysctl
import re
import pprint as pp
import ConfigParser
import time
import calendar

sysname = sysctl.filter('kern.hostname')[0]
hostname = sysname.value
sfxge_data = {}
config = ConfigParser.ConfigParser()
config.read('sfxge_sysctl_poller.cfg')
points_nic0 = {}
points_nic1 = {}
concat_points =""


nic0 = config.get('nics', 'nic0')
nic1 = config.get('nics', 'nic1')

nic0a = re.split('(\d)',nic0)
nic1a = re.split('(\d)',nic1)

nic0_target = ("dev.{}.{}").format(nic0a[0],nic0a[1])
nic1_target = ("dev.{}.{}").format(nic1a[0],nic1a[1])

nic0_stats = sysctl.filter(nic0_target)
nic1_stats = sysctl.filter(nic1_target)

for  i in range(len(nic0_stats)):
    raw_var =  str(nic0_stats[i]).replace(">", "")
    split_var = re.split(':',raw_var)
    long_oid = (split_var[1]).lstrip().replace(".","_")
    oid = (long_oid).replace("dev_sfxge_0_","")
    try:
       points_nic0[oid] = int(nic0_stats[i].value)
    except ValueError:
       points_nic0[oid] = str(nic0_stats[i].value)
    continue


for  i in range(len(nic1_stats)):
    raw_var =  str(nic1_stats[i]).replace(">", "")
    split_var = re.split(':',raw_var)
    long_oid = (split_var[1]).lstrip().replace(".","_")
    oid = (long_oid).replace("dev_sfxge_1_","")
    try:
       points_nic1[oid] = int(nic1_stats[i].value)
    except ValueError:
       points_nic1[oid] = str(nic1_stats[i].value)
    continue


for x in points_nic0.items():
    concat_points += ("{}={},").format(str(x[0]),x[1])
stamp = calendar.timegm(time.gmtime())
print("sfxge_stats,host={},interface={},{}{}").format(hostname,nic0,concat_points,stamp)

for x in points_nic1.items():
    concat_points += ("{}={},").format(str(x[0]),x[1])
stamp = calendar.timegm(time.gmtime())
print("sfxge_stats,host={},interface={},{}{}").format(hostname,nic1,concat_points,stamp)
