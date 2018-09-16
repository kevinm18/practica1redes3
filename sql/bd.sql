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
	num_interfaces int,
	estado int default 1,
	primary key (id)
);

create table interfaz_agente(
	id_agente int,
	id_interfaz int,
	estado int default 2,
	primary key(id_agente, id_interfaz),
	foreign key(id_agente) references agente(id)
);
