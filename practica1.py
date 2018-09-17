import os, sys, time, threading
from snmpAccess import *
from snmpParse import *
from OID import *
from flask import Flask, render_template, request, json, redirect, url_for 
from flaskext.mysql import MySQL
from rrd1 import *

app = Flask(__name__)
mysql = MySQL()

''' Configuracion de la conexion a MySQL '''

app.config['MYSQL_DATABASE_USER'] = 'kevin'
app.config['MYSQL_DATABASE_PASSWORD'] =	'root'
app.config['MYSQL_DATABASE_DB'] = 'agentes'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()

hilosPing = []
hilosInterfaces = {}
hilosGraficas = []

''' Metodos de acceso a la base de datos '''

# Obtiene el numero de dispositivos monitorizados
def numeroDispositivos():
	cursor.execute('SELECT COUNT(*) from agente')
	return cursor.fetchone()

# Inserta un nuevo dispositivo a la base de datos, asi como sus interfaces.
def insertar(host, comunidad, nombre, version, puerto, sistemaOperativo, interfaces):
	cursor.execute('INSERT INTO agente(hostname, version, puerto, comunidad, nombre, os, num_interfaces) VALUES (%s, %s, %s, %s, %s, %s, %s)', (host, version, puerto, comunidad, nombre, sistemaOperativo, interfaces))
	cursor.execute('SELECT MAX(id) from agente')
	idAgente = cursor.fetchone()[0]
	for i in range (int(interfaces)):
		cursor.execute('INSERT INTO interfaz_agente(id_agente, id_interfaz) VALUES (%s, %s)', (idAgente, i + 1))
	conn.commit()

''' Metodos usados por los hilos '''

# Verifica cada segundo si un agente esta conectado o desconectado y actualiza su estado en la bd
def pingUpDown(ip, comunidad, numeroInterfaces):
	while(1):
		mysqlPUD = MySQL()
		mysqlPUD.init_app(app)
		conexionPUD = mysqlPUD.connect()
		cursorPUD = conexionPUD.cursor()
		response = os.system("ping -c 1 " + ip)
		if response == 0:
			cursorPUD.execute('UPDATE agente SET estado = 0 where hostname = "' + ip + '"')
			hilosInterfaces.update({str(ip) : threading.Thread(target = interfazUpDown, args = (ip, comunidad, numeroInterfaces,))})
			hilosInterfaces[str(ip)].start()
		else:
			cursorPUD.execute('UPDATE agente SET estado = 1 where hostname = "' + ip + '"')
		conexionPUD.commit()
		conexionPUD.close()
		time.sleep(5)

# Monitoriza el estado de cada interfaz del agente en cuestion.
def interfazUpDown(host, comunidad, numInterfaces):
	while(1):
		mysqlIUD = MySQL()
		mysqlIUD.init_app(app)
		conexionIUD = mysqlIUD.connect()
		cursorIUD = conexionIUD.cursor()
		for i in range (numInterfaces):
			oid = OID_INTERFAZ_UP_DOWN
			oid = oid + str(i + 1)
			estado = parseResultAfterEquals(snmpGet(comunidad, host, oid))
			cursorIUD.execute('SELECT id FROM agente WHERE hostname = "' + host + '"') 
			idAgente = cursorIUD.fetchone()[0]
			cursorIUD.execute('UPDATE interfaz_agente SET estado = %s WHERE id_agente = %s AND id_interfaz = %s', (estado, idAgente, i + 1))
		conexionIUD.commit()
		conexionIUD.close()
		time.sleep(3)

# Metodo que ejecuta rrd2
def graphRRD(idInterfaz, host, comunidad):

	generarGraficas(idInterfaz, comunidad, host)

# Metodo que ejecuta rrd3
def executeRRD3():
	rrd3()

''' Metodos de navegacion '''

# Metodo de navegacion a la pantalla principal.
@app.route('/', methods = ['post', 'get'])
def main():
	numDispositivos = numeroDispositivos()[0]
	cursor.execute("SELECT * FROM agente")
	data = cursor.fetchall()
	for row in data:
		cursor.execute('SELECT num_interfaces FROM agente WHERE hostname = "' + row[1] + '"')
		numeroInterfaces = cursor.fetchone()[0]
		hilosPing.append(threading.Thread(target = pingUpDown, args = (row[1], row[4], numeroInterfaces,)))
		hilosPing[-1].start()
	return render_template('index.html', data = data, numDispositivos = numDispositivos)

# Metodo de navegacion a la pantalla de agregar agente
@app.route('/add')
def add():
	return render_template('add.html')

@app.route('/delete/<idAgente>', methods = ['post', 'get'])
def delete(idAgente):
	cursor.execute('SELECT * FROM agente WHERE id = "' + idAgente + '"')
	dataAgente = cursor.fetchone()
	return render_template('confirm_delete.html', dataAgente = dataAgente)

# Metodo que obtiene la informacion de las interfaces de un agente y redirige
# a la pagina de ver estado de interfaces
@app.route('/estadoInterfaces/<idAgente>', methods = ['post', 'get'])
def estadoInterfaces(idAgente):
	cursor.execute('SELECT * FROM agente WHERE id = "' + idAgente + '"')
	dataAgente = cursor.fetchone()
	cursor.execute('SELECT * FROM interfaz_agente WHERE id_agente = "' + idAgente + '"')
	dataInterfaz = list(cursor.fetchall())
	for i in range(len(dataInterfaz)):
		elemento = list(dataInterfaz[i])
		del dataInterfaz[i]
		dataInterfaz.insert(i, elemento)
	nombreInterfaces = []
	for i in range (len((dataInterfaz))):
		oid = OID_INTERFAZ_NOMBRE
		oid = oid + str(i + 1)
		nombreInterfaces.append(parseResultAfterEquals(snmpGet(dataAgente[4], dataAgente[1], oid)))
		dataInterfaz[i].insert(0, nombreInterfaces[-1])
		del dataInterfaz[i][1]
	return render_template('estado_interfaces.html', dataAgente = dataAgente, dataInterfaz = dataInterfaz, nombreInterfaces = nombreInterfaces)

''' Metodos de formulario '''

# Metodo ejecutado por el formulario al agregar un nuevo agente
@app.route('/addAgent', methods = ['post', 'get'])
def agregar():
	host = request.form['host']
	comunidad = request.form['comunidad']
	nombre = request.form['nombre']
	version = request.form['version']
	puerto = request.form['puerto']
	if host and comunidad and nombre and version and puerto:
		sistemaOperativo = parseResultAfterEquals(snmpGet(comunidad, host, OID_SYSINFO))
		interfaces = parseResultAfterEquals(snmpGet(comunidad, host, OID_INTERFACES))
		insertar(host, comunidad, nombre, version, puerto, sistemaOperativo, interfaces)
		return redirect(url_for('main'))
	else:
		return json.dumps({'html':'<span> Llene todos los campos </span>'})

# Elimina agente alv.
@app.route('/eliminarAgente/<idAgente>', methods = ['post', 'get'])
def eliminarAgente(idAgente):
	cursor.execute('DELETE FROM interfaz_agente WHERE id_agente = "' + idAgente + '"')
	cursor.execute('DELETE FROM agente WHERE id = "' + idAgente + '"')
	return redirect(url_for('main'))

@app.route('/generarGrafica/<idInterfaz>_<idAgente>', methods = ['post', 'get'])
def generarGrafica(idInterfaz, idAgente):
	cursor.execute('SELECT hostname, comunidad FROM agente WHERE id = "' + idAgente + '"')
	dataAgente = cursor.fetchone()
	rrd1()
	hiloGrafica = threading.Thread(target = graphRRD, args = (idInterfaz, dataAgente[0], dataAgente[1],))
	hiloGrafica.start()
	hiloRRD3 = threading.Thread(target = executeRRD3, args = ())
	hiloRRD3.start()
	return redirect(url_for('main'))


''' Metodo de ejecucion de la aplicacion '''

if __name__ == "__main__":
	app.run()