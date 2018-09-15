drop database agentes;

create database agentes;

use agentes;

create table agente(
	id int auto_increment,
	hostname varchar(20),
	version varchar(5),
	puerto int,
	comunidad varchar(50),
	nombre varchar(50),
	os varchar(50),
	primary key (id)
);
