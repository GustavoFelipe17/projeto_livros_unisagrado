1. Descrição Detalhada do Domínio do Problema
Este projeto é um aplicativo web full-stack que consome uma API pública e implementa um módulo de persistência com CRUD (Create, Read, Update, Delete) completo.

O domínio do problema é o gerenciamento de uma biblioteca pessoal de livros. O sistema permite que um usuário:

 -Busque livros em uma fonte externa (a API do Google Books).

 -Salve os livros de seu interesse em uma coleção pessoal (persistida em um banco de dados PostgreSQL).

 -Visualize todos os livros salvos em sua coleção.

 -Atualize os livros em sua coleção com uma avaliação pessoal (1 a 5 estrelas).

 -Delete livros de sua coleção.

 -Exporte sua coleção completa para um arquivo .csv.

2. Modelo Conceitual e Lógico do Banco de Dados
Modelo Conceitual
O sistema é centrado em uma única entidade principal: Livro. Esta entidade representa um livro que o usuário escolheu salvar em sua coleção. Os dados desta entidade são preenchidos tanto pela API do Google (título, autor) quanto pelo próprio usuário (avaliação).

Modelo Lógico (PostgreSQL)
Para implementar o modelo, utilizamos uma única tabela no PostgreSQL, chamada livros. Esta tabela armazena todas as informações relevantes e aplica restrições de domínio para garantir a integridade dos dados, conforme definido em app/models.py.

Nome da Coluna  -  Tipo de Dado (PostgreSQL)  -  Chave/Restrição  -  Descrição
     id                   SERIAL                    PRIMARY KEY         Identificador único auto-incrementado.
 google_api_id           VARCHAR(100)             UNIQUE NOT NULL       O ID do livro vindo da API do Google.
   titulo                VARCHAR(255)                NOT NULL           O título do livro.
   autor                 VARCAHR(255)                                   O(s) autor(es) do livro.
 ano_publicacao          VARCHAR(10)                                    O ano de publicação.
 url_capa                VARCHAR(10)                                    O link (URL) para a imagem da capa.
 avaliacao               INTEGER                      CHECK             Nota (1-5) dada pelo usuário. Permite NULL.

 3. Scripts SQL de Criação e Inserção
Embora o projeto utilize o ORM SQLAlchemy (que gera o SQL automaticamente através do comando db.create_all()), os scripts SQL brutos equivalentes para PostgreSQL são os seguintes:

Script de Criação (DDL)
Este script cria a tabela livros refletindo o modelo em app/models.py.

CREATE TABLE livros (
    id SERIAL PRIMARY KEY,
    google_api_id VARCHAR(100) UNIQUE NOT NULL,
    titulo VARCHAR(255) NOT NULL,
    autor VARCHAR(255),
    ano_publicacao VARCHAR(10),
    url_capa VARCHAR(500),
    avaliacao INTEGER,
    CONSTRAINT check_avaliacao_range CHECK (
        (avaliacao >= 1 AND avaliacao <= 5) OR (avaliacao IS NULL)
    )
);

Script de Inserção (DML)
Este script insere um livro de exemplo, simulando a ação da rota POST /api/livros.

INSERT INTO livros (google_api_id, titulo, autor, ano_publicacao, url_capa)
VALUES (
    'zyTCAlFPStQC', 
    'Duna', 
    'Frank Herbert', 
    '1965', 
    'http://books.google.com/books/content?id=zyTCAlFPStQC&printsec=frontcover&img=1&zoom=1&edge=curl&source=gbs_api'
);

4. Arquitetura do Código e Módulos
O projeto foi refatorado de um script monolítico para uma arquitetura modular profissional usando o padrão Application Factory. Isso separa as responsabilidades, tornando o projeto mais limpo, fácil de manter e testável.

Estrutura de Pastas e Responsabilidades
projeto_livros/ (Raiz)

run.py: O ponto de entrada da aplicação. Ele importa a "fábrica" e inicia o servidor Flask.

.env: Armazena as credenciais secretas do banco de dados. (Não versionado).

setup.py: Permite que o projeto seja instalado como um pacote, o que é essencial para que os testes (pytest) encontrem os módulos.

pytest.ini: Configura o pytest para encontrar os arquivos de teste.

app/ (O Módulo da Aplicação)

__init__.py: Contém a "fábrica" create_app(). É responsável por:

Criar a instância do app Flask.

Carregar as configurações (do .env ou dos testes).

Inicializar o db e o CORS.

Registrar o blueprint da API (routes.py).

Servir a rota principal / que carrega o index.html.

models.py: Define a estrutura do banco de dados (o modelo Livro) e suas regras (CHECK, UNIQUE, NOT NULL).

routes.py: Define todas as rotas da API (/api/...) usando um Flask Blueprint. Contém toda a lógica de negócios (CRUD, busca, exportação).

templates/: Contém os arquivos HTML (ex: index.html) que são servidos pelo Flask.

static/: Contém os arquivos estáticos (ex: style.css, script.js) que são usados pelo HTML.

tests/

conftest.py: Prepara o ambiente de testes, criando um app Flask "falso" conectado a um banco de dados SQLite em memória.

test_routes.py: Contém os testes unitários que simulam chamadas à API e verificam as respostas, garantindo que o CRUD funcione.

5. Exemplos de Consultas SQL Implementadas

O ORM (SQLAlchemy) abstrai as consultas. As operações da API (definidas em routes.py) mapeiam para os seguintes comandos SQL:

GET /api/livros (Ler a coleção)

SQL: SELECT * FROM livros;

Resultado: Retorna um JSON com a lista de todos os livros salvos.

POST /api/livros (Salvar um livro)

SQL: INSERT INTO livros (google_api_id, titulo, autor, ...) VALUES ($1, $2, $3, ...);

Resultado: Insere um livro no banco. Retorna um JSON do livro recém-criado (Status 201).

PUT /api/livros/<id> (Atualizar avaliação)

SQL: UPDATE livros SET avaliacao = $1 WHERE id = $2;

Resultado: Atualiza a nota de um livro. Retorna um JSON do livro atualizado (Status 200).

DELETE /api/livros/<id> (Deletar um livro)

SQL: DELETE FROM livros WHERE id = $1;

Resultado: Remove um livro do banco. Retorna um JSON com uma mensagem de sucesso (Status 200).

GET /api/livros/exportar (Exportar CSV)

SQL: SELECT * FROM livros;

Resultado: Pega todos os dados e os formata como um arquivo minha_colecao.csv, forçando o download no navegador.

6. Instruções Completas de Execução
Siga estes passos para configurar e executar o projeto.

Pré-requisitos
Python 3.10+

PostgreSQL (com o servidor rodando)

Git (opcional, para clonar)

Passo 1: Download e Setup do Ambiente
1-Clone ou baixe o projeto.

2-Navegue até a pasta raiz projeto_livros em um terminal.

3-Crie e ative um ambiente virtual:  
# Digite primeiro este comando
python -m venv venv 
# Depois digite esse
.\venv\Scripts\activate

Passo 2: Instalação das Dependências
Instale todas as bibliotecas necessárias:

# também no diretório da pasta raiz:
pip install Flask Flask-SQLAlchemy psycopg2-binary python-dotenv requests flask-cors pytest

2-(Para Testes) Instale seu projeto em modo editável (isso permite que o pytest encontre o módulo app):
# No terminal:
pip install -e .

Passo 3: Configuração do Banco de Dados e .env
Abra o PGAdmin (ou outro cliente PostgreSQL) e crie um novo banco de dados vazio chamado livros_db.

Na pasta raiz projeto_livros/, crie um arquivo chamado .env.

Copie o conteúdo abaixo para dentro do .env, substituindo SUA_SENHA pela sua senha do PostgreSQL (se ela tiver caracteres como @, use %40):
DATABASE_URL="postgresql://postgres:SUA_SENHA@127.0.0.1:5432/livros_db"

Passo 4: Criação das Tabelas
Antes de rodar o app, precisamos criar as tabelas no banco.

Defina a variável de ambiente FLASK_APP para que o shell funcione:

PowerShell

# Para PowerShell
$env:FLASK_APP = "run.py"
Bash

# Para CMD clássico
set FLASK_APP=run.py
Execute o flask shell (que agora usa o run.py):

Bash

flask shell
Dentro do shell do Python (>>>), digite os comandos para criar as tabelas com base nos models.py:

Python

>>> db.create_all()
>>> exit()
Passo 5: Execução do Projeto
Com o venv ainda ativo, execute o projeto com um único comando:

python run.py
O servidor estará rodando em http://127.0.0.1:5000.

Passo 6: Acessar o Aplicativo
Abra seu navegador.

Acesse: http://127.0.0.1:5000

A aplicação estará 100% funcional.

7. Execução dos Testes Unitários (Req. #7)
Para garantir a qualidade e a estabilidade da API, testes unitários foram criados.

Certifique-se de que seu venv está ativo e que você executou pip install -e . (Passo 2).

(O servidor python run.py não precisa estar rodando).

Na pasta raiz projeto_livros/, simplesmente execute:

pytest

O pytest encontrará o conftest.py, criará um banco de dados SQLite em memória, rodará todos os testes e apresentará um relatório de sucesso (ex: 2 passed).