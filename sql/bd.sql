drop database agentes;

create database agentes;

use agentes;

create table agente(
	hostname varchar(20),
	version varchar(5),
	puerto int,
	comunidad varchar(50),
	nombre varchar(50)
);

insert into agente(nombre, version, puerto, comunidad, hostname) 
	values ('ubuntu', 'v2c', 9050, 'comunidadSNMP', '192.168.0.7');