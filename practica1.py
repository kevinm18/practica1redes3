import os, sys
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

def insertar(host, comunidad, nombre, version, puerto, sistemaOperativo):
	cursor.execute('INSERT INTO agente(hostname, version, puerto, comunidad, nombre, os) VALUES (%s, %s, %s, %s, %s, %s)', (host, version, puerto, comunidad, nombre, sistemaOperativo))
	conn.commit()

@app.route('/')
def main():
	cursor.execute("SELECT * FROM agente")
	data = cursor.fetchall()
	for row in data:
		pass
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
		insertar(host, comunidad, nombre, version, puerto, sistemaOperativo)
		return redirect(url_for('main'))
	else:
		return json.dumps({'html':'<span>Llene todos los campos</span>'})

if __name__ == "__main__":
	app.run()