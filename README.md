# Sistema de Busca de CEP

Um sistema de busca de códigos postais (CEP) brasileiros com capacidades avançadas de tratamento de texto, utilizando a busca full-text do PostgreSQL com suporte a um Synonym Dictionary para variações de endereços brasileiros.

## Atribuição dos Dados

Esta base de dados contém mais de 1,1 milhão de CEPs em mais de 10.000 cidades brasileiras. Dados fornecidos pelo CEP Aberto (cepaberto.com).

## Configuração do Ambiente Python

1. Certifique-se de ter Python 3.8 ou superior instalado
2. Clone este repositório:
```bash
git clone https://github.com/seu-usuario/cep.git
cd cep
```

3. Crie e ative um ambiente virtual:
```bash
# Windows CMD
python -m venv venv
venv\Scripts\activate

# Windows Git Bash
python -m venv venv
source venv/Scripts/activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

4. Instale as dependências:
```bash
python -m pip install -r requirements.txt
```

## Instruções de Configuração

1. Instale o PostgreSQL 17 ou superior
2. Crie um usuário de banco de dados com as permissões apropriadas
3. Atualize os parâmetros de conexão no arquivo `import_cep_data.py` se necessário:
```python
DB_PARAMS = {
    'dbname': DB_NAME,
    'user': 'postgres',
    'password': 'sua_senha',
    'host': 'localhost',
    'port': '5432'
}
```

## Configurando o Synonym Dictionary de Endereços

O sistema utiliza um Synonym Dictionary (`address_pt.syn`) para lidar com variações de endereços brasileiros (abreviações, diminutivos, etc.). Para configurá-lo:

1. Copie o arquivo do Synonym Dictionary para o diretório do PostgreSQL. Você precisará de privilégios de administrador para esta etapa.
   
   Opção 1 - Usando o Git Bash (Executar como Administrador):
   ```bash
   cp "address_pt.syn" "/c/Program Files/PostgreSQL/17/share/tsearch_data/"
   ```
   
   Opção 1.1 - Usando CMD do Windows (Executar como Administrador):
   ```cmd
   copy "address_pt.syn" "C:\Program Files\PostgreSQL\17\share\tsearch_data\"
   ```
   
   Opção 2 - Cópia manual:
   - Copie o arquivo `address_pt.syn` deste diretório
   - Cole em `C:\Program Files\PostgreSQL\17\share\tsearch_data\`

2. Verifique se o arquivo foi copiado corretamente acessando o diretório do PostgreSQL:
   ```bash
   ls "/c/Program Files/PostgreSQL/17/share/tsearch_data/address_pt.syn"
   ```

## Configuração do Banco de Dados

1. Crie o banco de dados e execute os scripts SQL importantes na ordem:
```bash
psql -U postgres -c "CREATE DATABASE cep_database;"
psql -U postgres -d cep_database -f "sql/create_tables.sql"
psql -U postgres -d cep_database -f "sql/setup_config.sql"
psql -U postgres -d cep_database -f "sql/setup_normalization.sql"
```

## Preparando os Dados

Antes de importar os dados, você precisará decomprimir o arquivo `csv.tar.gz`:

```bash
# Windows (usando 7-Zip ou PowerShell)
tar -xzf csv.tar.gz

# Linux/Mac
tar -xzf csv.tar.gz
```

Isso criará o arquivo `csv/cep.csv` que será usado para a importação.

## Importando os Dados

Após configurar o Synonym Dictionary e executar os scripts SQL, e ter decomprimido o arquivo CSV, importe os dados de CEP:

```bash
python import_cep_data.py
```

Isto irá importar estados, cidades e dados de CEP.

## Atualizando Vectors de Busca

Após a importação inicial dos dados ou quando necessário atualizar os vetores de busca, execute:

```bash
psql -U postgres -d cep_database -f sql/setup_search_vectors.sql
```

Isso preencherá os vetores de busca para todos os endereços, garantirá que todos os dados estejam normalizados e prontos para a busca full-text.

## Funcionalidades

- Suporte a busca full-text para endereços brasileiros
- Trata variações comuns na escrita de endereços:
  - Abreviações (R. → Rua, Av. → Avenida)
  - Diminutivos (casa → casinha)
  - Plurais (casa → casas)
  - Títulos (Cel. → Coronel)
  - E muito mais

## Esquema do Banco de Dados

### Estados
- Chave primária: id
- Campos: nome, sigla, nome_normalizado, nome_busca (tsvector)

### Cidades
- Chave primária: id
- Campos: nome, estado_id (FK), nome_normalizado, nome_busca (tsvector)

### CEPs
- Chave primária: cep
- Campos: logradouro, complemento, bairro, cidade_id (FK), estado_id (FK), endereco_busca (tsvector)

## Capacidades de Busca

O sistema suporta busca por:
- Nomes de ruas e variações
- Bairros
- Cidades
- Estados
- Códigos postais
- Consultas mistas

Todas as buscas tratam:
- Insensibilidade a maiúsculas/minúsculas
- Insensibilidade a acentos
- Abreviações comuns
- Variações de endereços

## API REST

### Endpoints

#### GET /cep/{cep}
Retorna informações detalhadas sobre um CEP específico.

#### GET /search
Busca CEPs com base em critérios.

Parâmetros de consulta:
- `q`: Termo de busca (logradouro, bairro, etc.)
- `limit`: Número máximo de resultados (1-100)

### Exemplos de Uso da API

```bash
# Buscar por CEP específico
curl http://localhost:8000/cep/01310000

# Buscar por endereço
curl "http://localhost:8000/search?q=Avenida%20Paulista&limit=10"

# Buscar por bairro
curl "http://localhost:8000/search?q=Centro&limit=10"
```