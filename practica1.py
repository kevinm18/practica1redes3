import os, sys, time, threading
from snmpAccess import *
from snmpParse import *
from OID import *
from flask import Flask, render_template, request, json, redirect, url_for 
from flaskext.mysql import MySQL

app = Flask(__name__)
mysql = MySQL()

app.config['MYSQL_DATABASE_USER'] = 'kevin'
app.config['MYSQL_DATABASE_PASSWORD'] =	'root'
app.config['MYSQL_DATABASE_DB'] = 'agentes'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()

def insertar(host, comunidad, nombre, version, puerto, sistemaOperativo, interfaces):
	cursor.execute('INSERT INTO agente(hostname, version, puerto, comunidad, nombre, os, num_interfaces) VALUES (%s, %s, %s, %s, %s, %s, %s)', (host, version, puerto, comunidad, nombre, sistemaOperativo, interfaces))
	conn.commit()

def ping(ip):
	while(1):
		response = os.system("ping -c 1 " + ip)
		if response == 0:
			cursor.execute('UPDATE agente SET estado = 0 where hostname = "' + ip + '"')
		else:
			cursor.execute('UPDATE agente SET estado = 1 where hostname = "' + ip + '"')
		conn.commit()
		time.sleep(1)

@app.route('/')
def main():
	cursor.execute("SELECT * FROM agente")
	data = cursor.fetchall()
	for row in data:
		hiloPing = threading.Thread(target = ping, args = (row[1],))
		hiloPing.start()
	return render_template('index.html', data = data)

@app.route('/add')
def add():
	return render_template('add.html')

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

if __name__ == "__main__":
	app.run()