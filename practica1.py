import os, sys, time, threading
from snmpAccess import *
from snmpParse import *
from OID import *
from flask import Flask, render_template, request, json, redirect, url_for 
from flaskext.mysql import MySQL

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
hilosInterfaces = []
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
def pingUpDown(ip):
	while(1):
		response = os.system("ping -c 1 " + ip)
		if response == 0:
			cursor.execute('UPDATE agente SET estado = 0 where hostname = "' + ip + '"')
		else:
			cursor.execute('UPDATE agente SET estado = 1 where hostname = "' + ip + '"')
		conn.commit()
		time.sleep(5)

def interfazUpDown(host, comunidad, numInterfaces):
	while(1):
		for i in range (numInterfaces):
			oid = OID_INTERFAZ_UP_DOWN
			oid = oid + str(i + 1)
			estado = parseResultAfterEquals(snmpGet(comunidad, host, oid))
			cursor.execute('SELECT id FROM agente WHERE hostname = "' + host + '"') 
			idAgente = cursor.fetchone()[0]
			cursor.execute('UPDATE interfaz_agente SET estado = %s WHERE id_agente = %s AND id_interfaz = %s', (estado, idAgente, i + 1))
			conn.commit()
		time.sleep(3)

def generarGraficas(host, comunidad):
	while(1):
		
		time.sleep(5)

''' Metodos de navegacion '''

# Metodo de navegacion a la pantalla principal.
@app.route('/')
def main():
	numDispositivos = numeroDispositivos()[0]
	cursor.execute("SELECT * FROM agente")
	data = cursor.fetchall()
	for row in data:
		hilosPing.append(threading.Thread(target = pingUpDown, args = (row[1],)))
		hilosPing[-1].start()
		cursor.execute('SELECT num_interfaces FROM agente WHERE hostname = "' + row[1] + '"')
		numeroInterfaces = cursor.fetchone()[0]
		hilosInterfaces.append(threading.Thread(target = interfazUpDown, args = (row[1], row[4], numeroInterfaces,)))
		hilosInterfaces[-1].start()
		hilosGraficas.append(threading.Thread(target = generarGraficas, args = (row[1], row[4],)))
		hilosGraficas[-1].start()
	return render_template('index.html', data = data, numDispositivos = numDispositivos)

# Metodo de navegacion a la pantalla de agregar agente
@app.route('/add')
def add():
	return render_template('add.html')

# Metodo que obtiene la informacion de las interfaces de un agente y redirige
# a la pagina de ver estado de interfaces
@app.route('/estadoInterfaces/<idAgente>', methods = ['post', 'get'])
def estadoInterfaces(idAgente):
	execfile('hola.py')
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
		dataInterfaz[i].insert(1, nombreInterfaces[-1])
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

''' Metodo de ejecucion de la aplicacion '''

if __name__ == "__main__":
	app.run()