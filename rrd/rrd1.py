#!/usr/bin/env python

import rrdtool
ret = rrdtool.create("practica1.rrd",
                     "--start",'N',
                     "--step",'60',
                     "DS:inoctets:COUNTER:600:U:U",
                     "DS:outoctets:COUNTER:600:U:U",
                     "RRA:AVERAGE:0.5:1:20",
                     "RRA:AVERAGE:0.5:6:10")

if ret:
    print rrdtool.error()

