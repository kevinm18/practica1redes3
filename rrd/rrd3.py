import sys
import rrdtool
import time
tiempo_actual = int(time.time())
tiempo_final = tiempo_actual - 86400
tiempo_inicial = tiempo_final -25920000

while 1:
    ret = rrdtool.graph( "net.png",
                     "--start",'1504542540',
 #                    "--end","N",
                     "--vertical-label=Bytes/s",
                     "DEF:inoctets=net3.rrd:inoctets:AVERAGE",
                     "DEF:outoctets=net3.rrd:outoctets:AVERAGE",
                     "AREA:inoctets#00FF00:In traffic",
                     "LINE1:outoctets#0000FF:Out traffic\r")

    time.sleep(30)
