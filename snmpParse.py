# Filtra el resultado de una consulta SNMP y quita toda la demas informacion no util.
def parseResultAfterEquals(resultado):
	varBinds = resultado['varBinds']
	for vB in varBinds:
		varB = (' = '.join([x.prettyPrint() for x in vB]))
		res = varB.split()[2]
	return res
