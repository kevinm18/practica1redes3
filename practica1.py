import os, sys

from flask import Flask, render_template
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


@app.route('/')
def main():
	cursor.execute("SELECT * FROM agente")
	data = cursor.fetchall()
	for row in data:
		response = os.system("ping -c 1 " + row [0])
	return render_template('index.html', data = data)

@app.route('/add')
def add():
	return render_template('add.html')

@app.route('/addAgent', methods = ['post', 'get'])
def agregar():
	return "agregado"


if __name__ == "__main__":
	app.run()