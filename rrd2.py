import time
import rrdtool
from snmpAccess import *
from snmpParse import *
from OID import *

total_input_traffic = 0
total_output_traffic = 0

def generarGraficas(interfaz, comunidad, host):
    while 1:
        total_input_traffic = int(parseResultAfterEquals(
            snmpGet(comunidad, host, 
                         OID_INPUT_TRAFFIC + str(interfaz))))

        total_output_traffic = int(parseResultAfterEquals(
            snmpGet(comunidad, host, 
                         OID_OUTPUT_TRAFFIC + str(interfaz))))

        # total_input_pkts = int(parseResultAfterEquals(
        #     snmpGet(comunidad, host,
        #                 OID_INPUT_PKTS + str(interfaz))))

        # total_output_pkts = int(parseResultAfterEquals(
        #     snmpGet(comunidad, host,
        #                 OID_OUTPUT_PKTS + str(interfaz))))


        valor = "N:" + str(total_input_traffic) + ':' + str(total_output_traffic)
        print valor
        rrdtool.update('practica1.rrd', valor)
        rrdtool.dump('practica1.rrd','practica1.xml')
        time.sleep(1)

    if ret:
        print rrdtool.error()
        time.sleep(300)
