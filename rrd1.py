import time
import rrdtool
from snmpAccess import *
from snmpParse import *
from OID import *

total_input_traffic = 0
total_output_traffic = 0
tiempo_actual = int(time.time())
tiempo_final = tiempo_actual - 86400
tiempo_inicial = tiempo_final -25920000

def generarGraficas(interfaz, comunidad, host):
    while 1:
    	# trafico de entrada y salida
        total_input_traffic = int(parseResultAfterEquals(
            snmpGet(comunidad, host, 
                         OID_INPUT_TRAFFIC + str(interfaz))))

        total_output_traffic = int(parseResultAfterEquals(
            snmpGet(comunidad, host, 
                         OID_OUTPUT_TRAFFIC + str(interfaz))))

        valorTraffic = "N:" + str(total_input_traffic) + ':' + str(total_output_traffic)
        rrdtool.update('practica1_1.rrd', valorTraffic)
        rrdtool.dump('practica1_1.rrd','practica1_1.xml')

        # paquetes de entrada y salida
        total_input_pkts = int(parseResultAfterEquals(
            snmpGet(comunidad, host,
                        OID_INPUT_PKTS + str(interfaz))))

        total_output_pkts = int(parseResultAfterEquals(
            snmpGet(comunidad, host,
                        OID_OUTPUT_PKTS + str(interfaz))))

        valorPkts = 'N:' + str(total_input_pkts) + ':' + str(total_input_pkts)
        rrdtool.update('practica1_2.rrd', valorPkts)
        rrdtool.dump('practica1_2.rrd','practica1_2.xml')

       # conexiones TCP establecidas o en espera
        total_tcp_established = int(parseResultAfterEquals(
        	snmpGet(comunidad, host, OID_TCP_CURR_EST)))

        valorTCPEst = 'N:' + str(total_tcp_established) + ':' + str(0)
        rrdtool.update('practica1_3.rrd', valorTCPEst)
        rrdtool.dump('practica1_3.rrd', 'practica1_3.xml')

        # errores UDP
        udp_errors = int(parseResultAfterEquals(
        	snmpGet(comunidad, host, OID_UDP_ERRORS)))

        valorUDPErr = 'N:' + str(udp_errors) + ':' + str(0)
        rrdtool.update('practica1_4.rrd', valorTCPEst)
        rrdtool.dump('practica1_4.rrd', 'practica1_4.xml')

        # estadisticas de entrada y salida TCP

        tcp_stats_in = int(parseResultAfterEquals(
        	snmpGet(comunidad, host, OID_TCP_IN)))

        tcp_stats_out = int(parseResultAfterEquals(
        	snmpGet(comunidad, host, OID_TCP_OUT)))

        valorTCPStats = 'N:' + str(tcp_stats_in) + ':' + str(tcp_stats_out)
        rrdtool.update('practica1_5.rrd', valorTCPStats)
        rrdtool.dump('practica1_5.rrd', 'practica1_5.xml')

        time.sleep(1)

    if ret:
        print rrdtool.error()
        time.sleep(300)

def rrd1():
	ret = rrdtool.create("practica1_1.rrd",
	                     "--start",'N',
	                     "--step",'60',
	                     "DS:inoctets:COUNTER:600:U:U",
	                     "DS:outoctets:COUNTER:600:U:U",
	                     "RRA:AVERAGE:0.5:1:20",
	                     "RRA:AVERAGE:0.5:6:10")

	ret2 = rrdtool.create("practica1_2.rrd",
	                     "--start",'N',
	                     "--step",'60',
	                     "DS:inpackets:COUNTER:600:U:U",
	                     "DS:outpackets:COUNTER:600:U:U",
	                     "RRA:AVERAGE:0.5:1:20",
	                     "RRA:AVERAGE:0.5:6:10")

	ret3 = rrdtool.create("practica1_3.rrd",
	                     "--start",'N',
	                     "--step",'60',
	                     "DS:inpackets:COUNTER:600:U:U",
	                     "DS:outpackets:COUNTER:600:U:U",
	                     "RRA:AVERAGE:0.5:1:20",
	                     "RRA:AVERAGE:0.5:6:10")

	ret4 = rrdtool.create("practica1_4.rrd",
	                     "--start",'N',
	                     "--step",'60',
	                     "DS:inpackets:COUNTER:600:U:U",
	                     "DS:outpackets:COUNTER:600:U:U",
	                     "RRA:AVERAGE:0.5:1:20",
	                     "RRA:AVERAGE:0.5:6:10")

	ret5 = rrdtool.create("practica1_5.rrd",
	                     "--start",'N',
	                     "--step",'60',
	                     "DS:inpackets:COUNTER:600:U:U",
	                     "DS:outpackets:COUNTER:600:U:U",
	                     "RRA:AVERAGE:0.5:1:20",
	                     "RRA:AVERAGE:0.5:6:10")

	if ret or ret2 or ret3 or ret4 or ret5:
	    print rrdtool.error()

def rrd3():
	tiempo_actual = int(time.time())
	while 1:
	    ret = rrdtool.graph( "practica1_1.png",
	                     "--start",str(tiempo_actual),
	 #                    "--end","N",
	                     "--vertical-label=Bytes/s",
	                     "DEF:inoctets=practica1_1.rrd:inoctets:AVERAGE",
	                     "DEF:outoctets=practica1_1.rrd:outoctets:AVERAGE",
	                     "LINE1:inoctets#00FF00:In traffic",
	                     "LINE1:outoctets#0000FF:Out traffic\r")

	    ret2 = rrdtool.graph("practica1_2.png",
	                     "--start",str(tiempo_actual),
	#                    "--end","N",
	                     "--vertical-label=Bytes/s",
	                     "DEF:inpackets=practica1_2.rrd:inpackets:AVERAGE",
	                     "DEF:outpackets=practica1_2.rrd:outpackets:AVERAGE",
	                     "LINE1:inpackets#00FF00:In packets",
	                     "LINE1:outpackets#0000FF:In packets\r")

	    ret3 = rrdtool.graph("practica1_3.png",
	                     "--start",str(tiempo_actual),
	#                    "--end","N",
	                     "--vertical-label=Bytes/s",
	                     "DEF:inpackets=practica1_3.rrd:inpackets:AVERAGE",
	                     "DEF:outpackets=practica1_3.rrd:outpackets:AVERAGE",
	                     "LINE1:inpackets#00FF00:Conexiones TCP",
	                     "LINE1:outpackets#0000FF: \r")

	    ret4 = rrdtool.graph("practica1_4.png",
	                     "--start",str(tiempo_actual),
	#                    "--end","N",
	                     "--vertical-label=Bytes/s",
	                     "DEF:inpackets=practica1_4.rrd:inpackets:AVERAGE",
	                     "DEF:outpackets=practica1_4.rrd:outpackets:AVERAGE",
	                     "LINE1:inpackets#00FF00:Errores UDP",
	                     "LINE1:outpackets#0000FF: \r")

	    ret5 = rrdtool.graph("practica1_5.png",
	                     "--start",str(tiempo_actual),
	#                    "--end","N",
	                     "--vertical-label=Bytes/s",
	                     "DEF:inpackets=practica1_5.rrd:inpackets:AVERAGE",
	                     "DEF:outpackets=practica1_5.rrd:outpackets:AVERAGE",
	                     "LINE1:inpackets#FF0000:In TCP`",
	                     "LINE1:outpackets#0000FF:Out TCP\r")

	    time.sleep(10)

