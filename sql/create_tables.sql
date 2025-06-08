-- Active: 1749331579998@@127.0.0.1@5432@cep_database

-- CREATE DATABASE cep_database;

-- Estados table
CREATE TABLE IF NOT EXISTS estados (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    uf CHAR(2) NOT NULL UNIQUE
);

-- Cidades table  
CREATE TABLE IF NOT EXISTS cidades (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    estado_id INTEGER REFERENCES estados(id)
);

-- CEPs table
CREATE TABLE IF NOT EXISTS ceps (
    id SERIAL PRIMARY KEY,
    cep CHAR(8) NOT NULL UNIQUE,
    logradouro TEXT,
    complemento TEXT,
    bairro VARCHAR(100),
    cidade_id INTEGER REFERENCES cidades(id),
    estado_id INTEGER REFERENCES estados(id)
);

-- Search table for denormalized data and search functionality
CREATE TABLE IF NOT EXISTS ceps_search (
    id SERIAL PRIMARY KEY,
    cep CHAR(8) NOT NULL UNIQUE,
    logradouro TEXT,
    complemento TEXT,
    bairro VARCHAR(100),
    cidade VARCHAR(100),
    uf CHAR(2),
    search_vector tsvector,
    UNIQUE (cep)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_ceps_cep ON ceps(cep);
CREATE INDEX IF NOT EXISTS idx_ceps_cidade ON ceps(cidade_id);
CREATE INDEX IF NOT EXISTS idx_ceps_estado ON ceps(estado_id);
CREATE INDEX IF NOT EXISTS idx_ceps_search_cep ON ceps_search(cep);
CREATE INDEX IF NOT EXISTS idx_ceps_search_vector ON ceps_search USING GIN(search_vector);
CREATE INDEX IF NOT EXISTS idx_cidades_nome ON cidades(nome);
CREATE INDEX IF NOT EXISTS idx_estados_sigla ON estados(uf); 