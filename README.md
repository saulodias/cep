# Sistema de Busca de CEP

Um sistema de busca de códigos postais (CEP) brasileiros com capacidades avançadas de tratamento de texto, utilizando a busca full-text do PostgreSQL com suporte a thesaurus personalizado para variações de endereços brasileiros.

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

## Configurando o Thesaurus de Endereços

O sistema utiliza um thesaurus personalizado para lidar com variações de endereços brasileiros (abreviações, diminutivos, etc.). Para configurá-lo:

1. Copie o arquivo do thesaurus para o diretório do PostgreSQL. Você precisará de privilégios de administrador para esta etapa.
   
   Opção 1 - Usando o Git Bash (Executar como Administrador):
   ```bash
   cp "address_pt.ths" "/c/Program Files/PostgreSQL/17/share/tsearch_data/"
   ```
   
   Opção 1.1 - Usando CMD do Windows (Executar como Administrador):
   ```cmd
   copy "address_pt.ths" "C:\Program Files\PostgreSQL\17\share\tsearch_data\"
   ```
   
   Opção 2 - Cópia manual:
   - Copie o arquivo `address_pt.ths` deste diretório
   - Cole em `C:\Program Files\PostgreSQL\17\share\tsearch_data\`

2. Verifique se o arquivo foi copiado corretamente acessando o diretório do PostgreSQL:
   ```bash
   ls "/c/Program Files/PostgreSQL/17/share/tsearch_data/address_pt.ths"
   ```

## Importando os Dados

Após configurar o thesaurus, importe os dados de CEP:

```bash
python import_cep_data.py --recreate-tables
```

Isto irá:
1. Criar o banco de dados se não existir
2. Criar as tabelas e índices necessários
3. Configurar a configuração personalizada de busca textual
4. Importar estados, cidades e dados de CEP
5. Criar índices de busca full-text

## Funcionalidades

- Suporte a busca full-text para endereços brasileiros
- Trata variações comuns na escrita de endereços:
  - Abreviações (R. → Rua, Av. → Avenida)
  - Diminutivos (casa → casinha)
  - Plurais (casa → casas)
  - Títulos (Cel. → Coronel)
  - E muito mais

## Atualizando Vectors de Busca

Após a importação inicial dos dados ou quando necessário atualizar os vetores de busca, execute:

```bash
psql -U postgres -d cep_database -f sql/setup_search_vectors.sql
```

Este comando:
1. Atualiza os vetores de busca para todos os endereços
2. Mostra o progresso da atualização em porcentagem
3. Verifica a conclusão do processo

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

#### GET /cep/busca
Busca CEPs com base em critérios.

Parâmetros de consulta:
- `logradouro`: Nome da rua, avenida, etc.
- `bairro`: Nome do bairro
- `cidade`: Nome da cidade
- `estado`: Nome ou sigla do estado

### Exemplos de Uso da API

```bash
# Buscar por CEP específico
curl http://localhost:8000/cep/01310000

# Buscar por endereço
curl http://localhost:8000/cep/busca?logradouro=Avenida%20Paulista&cidade=São%20Paulo

# Buscar por bairro
curl http://localhost:8000/cep/busca?bairro=Centro&cidade=Rio%20de%20Janeiro
``` 