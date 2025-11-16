Projeto: Aplicativo Full-Stack de Biblioteca Pessoal
1. Descrição Detalhada do Domínio do Problema
Este projeto é um aplicativo web full-stack que consome uma API pública e implementa um módulo de persistência com CRUD.

O domínio do problema é o gerenciamento de uma biblioteca pessoal de livros. O sistema permite que um usuário busque por livros em uma fonte externa (a API do Google Books) e salve os livros de seu interesse em uma coleção pessoal, que é persistida em um banco de dados relacional. O usuário pode, a qualquer momento, visualizar sua coleção e remover itens dela.

2. Modelo Conceitual e Lógico do Banco de Dados
Modelo Conceitual
O sistema é centrado em uma única entidade principal: Livro. Esta entidade representa um livro que o usuário escolheu salvar em sua coleção pessoal. Os dados desta entidade são preenchidos tanto pela API do Google quanto pelo nosso próprio banco de dados (como o id único).

Para implementar o modelo conceitual, utilizamos uma única tabela no PostgreSQL, chamada livros. Esta tabela armazena as informações relevantes para exibir o livro na coleção do usuário.

A estrutura da tabela livros é a seguinte:

Nome da Coluna  -  Tipo de Dado (PostgreSQL)  -  Chave/Restrição  -  Descrição
     id                   Serial                  PRIMARY KEY          Identificador único auto-incrementado
 google_api_id         VARCHAR(100)             UNIQUE NOT NULL        O ID do livro vindo da API do Google
   titulo              VARCHAR(255)                 NOT NULL           O titulo do livro
   autor               VARCHAR(255)                                    O ano de publicação
  url_capa             VARCHAR(500)                                    O link para a imagem da capa

3. Scripts SQL de Criação e Inserção
Embora o projeto utilize o ORM SQLAlchemy (que gera o SQL automaticamente através do comando db.create_all()), os scripts SQL brutos equivalentes para PostgreSQL são os seguintes:

Script de Criação (DDL)
Este script cria a tabela livros conforme o modelo lógico.

CREATE TABLE livros (
    id SERIAL PRIMARY KEY,
    google_api_id VARCHAR(100) UNIQUE NOT NULL,
    titulo VARCHAR(255) NOT NULL,
    autor VARCHAR(255),
    ano_publicacao VARCHAR(10),
    url_capa VARCHAR(500)
);

Script de Inserção (DML)
Este script insere um livro de exemplo na tabela (simulando a ação da rota POST /api/livros).

INSERT INTO livros (google_api_id, titulo, autor, ano_publicacao, url_capa)
VALUES (
    'zyTCAlFPStQC', 
    'Duna', 
    'Frank Herbert', 
    '1965', 
    'http://books.google.com/books/content?id=zyTCAlFPStQC&printsec=frontcover&img=1&zoom=1&edge=curl&source=gbs_api'
);

4. Arquitetura do Código e Módulos
O projeto segue uma arquitetura de 3 camadas (3-Tier) clássica, separando as responsabilidades:

1. Backend (Servidor - app.py)
Tecnologia: Python com Flask e Flask-SQLAlchemy.

Responsabilidade: É o "cérebro" da aplicação.

Módulos:

API (Rotas): Define os endpoints (/api/livros, /api/buscar, etc.) que o frontend pode chamar.

Controle de CRUD (Req. #4): Implementa as funções adicionar_livro(), get_livros_salvos(), deletar_livro() que manipulam o banco.

Consumo de API Externa (Req. #1): A rota /api/buscar atua como um proxy, buscando dados na API do Google Books e formatando-os para o frontend.

Persistência (ORM): A classe Livro(db.Model) mapeia a tabela do banco para um objeto Python.

Segurança (Req. #6): Utiliza Flask-CORS para permitir a comunicação com o frontend e dotenv para gerenciar senhas externamente (Req. #5).

2. Frontend (Cliente - frontend/)
Tecnologia: HTML, CSS e JavaScript (Vanilla JS).

Responsabilidade: É o "rosto" da aplicação; tudo o que o usuário vê e com o que interage.

Módulos:

index.html: A estrutura (esqueleto) da página.

style.css: A estilização (pintura) e o layout dos cards.

script.js: O "cérebro" do frontend. É responsável por:

Ouvir eventos (cliques nos botões "Buscar", "Salvar", "Deletar").

Usar a função fetch para fazer requisições HTTP para a API do Backend.

Manipular o DOM para criar, atualizar e remover dinamicamente os cards de livros na tela.

3. Banco de Dados (Persistência)
Tecnologia: PostgreSQL.

Responsabilidade: É o "armazém" da aplicação.

Módulos:

Banco livros_db: O contêiner para nossos dados.

Tabela livros: Onde os dados da coleção pessoal do usuário são armazenados de forma permanente.

5. Exemplos de Consultas SQL Implementadas
O ORM (SQLAlchemy) abstrai as consultas SQL. As operações da API mapeiam para os seguintes comandos SQL:

GET /api/livros (Ler a coleção)

SQL: SELECT id, google_api_id, titulo, autor, ano_publicacao, url_capa FROM livros;

Resultado: Retorna uma lista (JSON) de todos os livros salvos no banco.

POST /api/livros (Salvar um livro)

SQL: INSERT INTO livros (google_api_id, titulo, ...) VALUES (...);

Resultado: Insere uma nova linha na tabela e retorna o objeto (JSON) do livro recém-criado.

DELETE /api/livros/<id> (Deletar um livro)

SQL: DELETE FROM livros WHERE id = 1; (Exemplo para o livro de ID 1)

Resultado: Remove a linha correspondente do banco e retorna uma mensagem de sucesso.

6. Instruções Completas de Execução
Siga estes passos para configurar e executar o projeto.

Pré-requisitos
Python 3.10+

PostgreSQL (com o servidor rodando)

(Opcional) Insomnia ou Postman para testes de API

Passo 1: Configuração do Ambiente Backend
1-Clone ou baixe o projeto.

2-Navegue até a pasta raiz projeto_livros.

3-Crie e ative um ambiente virtual:

# No terminal:
python -m venv venv
.\venv\Scripts\activate

4-Instale as dependências:

# No terminal:
pip install -r requirements.txt

5-Configure o Banco de Dados:

Abra o PGAdmin e crie um novo banco de dados chamado livros_db.

6-Configure as Variáveis de Ambiente:

Crie um arquivo .env na raiz (projeto_livros/).

Adicione sua string de conexão: DATABASE_URL="postgresql://postgres:SUA_SENHA@127.0.0.1:5432/livros_db"

7-Crie as Tabelas no Banco:

# No terminal digite o comando abaixo e pressione enter:
flask shell

# Dentro do shell do Python (>>>):
1- >>> from app import db
2- >>> db.create_all()
3- >>> exit()

Passo 2: Execução do Projeto

1- Dentro de um terminal, ative o venv utilizando o comando: .\venv\Scripts\activate
# Caso não tenha instalado o venv, utilize o comando python -m venv venv. Após isso, utilize o comando logo acima novamente.

2- Após utilizad o comando acima, certifique-se que em seu terminal apareceu escrito "(venv)" antes de diretório, feito isso, utilize o comando abaixo:
python app.py
Esse comando irá executar a aplicação

3- O servidor estará rodando em http://127.0.0.1:5000


Passo 3: Acessar o Aplicativo
 -Abra seu navegador e acesse: http://127.0.0.1:5000

 -A aplicação estará 100% funcional.