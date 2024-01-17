create database dashboard_gmail;

use dashboard_gmail;

create table Empresa(
	idEmpresa INT auto_increment,
    nome VARCHAR(30),
    email_dominio VARCHAR(60),
    primary key(idEmpresa)
);

create table Emitente(
	idEmitente INT auto_increment,
    nome VARCHAR(30),
    email VARCHAR(60),
    idEmpresa INT,
    primary key(idEmitente),
    foreign key(idEmpresa) references Empresa(idEmpresa)
);

create table Label(
	idLabel VARCHAR(30),
    nome varchar(30),
    primary key(idLabel)
);

create table Email(
	idEmail VARCHAR(30) not null,
    titulo VARCHAR(100),
    resumo BLOB,
    data_email DATETIME,
    destinatario_email VARCHAR(60),
    link BLOB,
    idEmitente INT,
    primary key(idEmail),
    foreign key(idEmitente) references Emitente(idEmitente)
);

create table email_label(
	idEmailLabel INT auto_increment,
    idEmail VARCHAR(30),
    idLabel VARCHAR(30),
    primary key(idEmailLabel),
    foreign key(idEmail) references Email(idEmail),
    foreign key(idLabel) references Label(idLabel)
);

create table Caixa_Entrada(
	idCaixEntrada varchar(100),
    titulo VARCHAR(100),
    data_email DATETIME,
    destinatario_email VARCHAR(60),
    idEmitente INT,
    primary key(idCaixEntrada),
    foreign key(idEmitente) references Emitente(idEmitente)
);