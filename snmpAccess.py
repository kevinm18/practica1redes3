from pysnmp.hlapi import *

def snmpGet(comunidad, ip, oid):
	resultado = {}
	errorIndication, errorStatus, errorIndex, varBinds = next(
		getCmd(SnmpEngine(),
           CommunityData(comunidad),
           UdpTransportTarget((ip, 161)),
           ContextData(),
           ObjectType(ObjectIdentity(oid)))
	)
	if errorIndication:
		print(errorIndication)
		return
	elif errorStatus:
		print('%s at %s' % (errorStatus.prettyPrint(),
                        errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
		return
	else:
		resultado.update({'errorIndication': errorIndication})
		resultado.update({'errorStatus': errorStatus})
		resultado.update({'errorIndex': errorIndex})
		resultado.update({'varBinds': varBinds})
		return resultado

