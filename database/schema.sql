CREATE DATABASE IF NOT EXISTS sos_golpes;
USE sos_golpes;

CREATE TABLE Perfil (
    id_perfil INT AUTO_INCREMENT PRIMARY KEY,
    nome_perfil VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE Usuario (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    id_perfil INT NOT NULL,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    senha_hash VARCHAR(255) NOT NULL,
    token_2fa_secret VARCHAR(100) DEFAULT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_perfil) REFERENCES Perfil(id_perfil)
);

CREATE TABLE Registro_Leak (
    id_leak INT AUTO_INCREMENT PRIMARY KEY,
    senha_vazada_hash VARCHAR(255) NOT NULL UNIQUE,
    fonte_vazamento VARCHAR(150) NOT NULL
);

CREATE TABLE Analise_Link (
    id_analise INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    url_analisada TEXT NOT NULL,
    nivel_perigo ENUM('Seguro', 'Suspeito', 'Malicioso') NOT NULL,
    detalhes_analise TEXT,
    data_consulta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario) ON DELETE CASCADE
);

CREATE TABLE Log_Acesso (
    id_log INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT,
    acao_realizada VARCHAR(255) NOT NULL,
    endereco_ip VARCHAR(45) NOT NULL,
    data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario) ON DELETE SET NULL
);

INSERT INTO Perfil (nome_perfil) VALUES ('Administrador'), ('Cidadao');

INSERT INTO Registro_Leak (senha_vazada_hash, fonte_vazamento) VALUES 
(SHA2('123456', 256), 'RockYou2021'),
(SHA2('senha123', 256), 'Vazamento 2'),
(SHA2('admin', 256), 'Roteadores Padrao'),
(SHA2('BombaTermonuclear', 256), 'Forum de Gatos CatLovers'),
(SHA2('PUCPR', 256), 'Ataque Phishing Universidades');