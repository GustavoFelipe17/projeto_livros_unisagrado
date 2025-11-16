import os
from flask import Flask, request, jsonify, make_response, render_template  # ATUALIZADO
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import requests
from flask_cors import CORS
import csv
import io

load_dotenv()
app = Flask(__name__)
CORS(app)

API_URL = os.getenv('API_BASE_URL')

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Livro(db.Model):
    __tablename__ = 'livros'
    
    id = db.Column(db.Integer, primary_key=True)
    google_api_id = db.Column(db.String(100), unique=True, nullable=False)
    titulo = db.Column(db.String(255), nullable=False)
    autor = db.Column(db.String(255))
    ano_publicacao = db.Column(db.String(10))
    url_capa = db.Column(db.String(500))
    avaliacao = db.Column(db.Integer, nullable=True)

    # ATUALIZAÇÃO 1: TRADUTOR JSON
    def to_dict(self):
        return {
            'id': self.id,
            'google_api_id': self.google_api_id,
            'titulo': self.titulo,
            'autor': self.autor,
            'ano_publicacao': self.ano_publicacao,
            'url_capa': self.url_capa,
            'avaliacao': self.avaliacao
        }

    def __repr__(self):
        return f'<Livro {self.titulo}>'
#FIM DA ATUALIZAÇÃO 1
# ATUALIZAÇÃO 2: ROTAS DA API DE CRUD
@app.route('/api/livros', methods=['POST'])
def adicionar_livro():
    dados = request.get_json()
    if not dados or 'google_api_id' not in dados or 'titulo' not in dados:
        return jsonify({'erro': 'Dados incompletos'}), 400

    novo_livro = Livro(
        google_api_id=dados['google_api_id'],
        titulo=dados['titulo'],
        autor=dados.get('autor'),
        ano_publicacao=dados.get('ano_publicacao'),
        url_capa=dados.get('url_capa')
    )
    
    db.session.add(novo_livro)
    
    try:
        db.session.commit()
        return jsonify(novo_livro.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        if 'unique constraint' in str(e):
            return jsonify({'erro': 'Este livro (google_api_id) já foi salvo.'}), 409
        return jsonify({'erro': f'Erro ao salvar no banco: {str(e)}'}), 500


@app.route('/api/livros', methods=['GET'])
def get_livros_salvos():
    livros_salvos = Livro.query.all()
    lista_json = [livro.to_dict() for livro in livros_salvos]
    return jsonify(lista_json)
# FIM DA ATUALIZAÇÃO 2

# ATUALIZAÇÃO 4: ROTAS PARA BUSCAR LIVROS NA API DO GOOGLE
@app.route('/api/buscar', methods=['GET'])
def buscar_livros_google():
    termo_busca = request.args.get('termo')

    if not termo_busca:
        return jsonify({'erro': 'O parâmetro "termo" é obrigatório'}), 400

    google_api_url = f"https://www.googleapis.com/books/v1/volumes?q={termo_busca}&maxResults=10"

    try:
        response = requests.get(google_api_url)
        response.raise_for_status() 
        
        dados_google = response.json()

        livros_formatados = []
        for item in dados_google.get('items', []):
            volume_info = item.get('volumeInfo', {})
            
            capa = volume_info.get('imageLinks', {}).get('thumbnail', None)
            
            autores = volume_info.get('authors', ['Autor desconhecido'])
            
            ano = volume_info.get('publishedDate', '0000')[:4]

            livro_limpo = {
                "google_api_id": item.get('id'),
                "titulo": volume_info.get('title'),
                "autor": ", ".join(autores),
                "ano_publicacao": ano,
                "url_capa": capa
            }
            livros_formatados.append(livro_limpo)
        
        return jsonify(livros_formatados)

    except requests.exceptions.RequestException as e:
        return jsonify({'erro': f'Erro ao se comunicar com a Google Books API: {str(e)}'}), 503 # 503 = Service Unavailable
# FIM DA ATUALIZAÇÃO 4

    # ATUALIZAÇÃO 5: ROTA PARA DELETAR LIVROS 
    # O <int:id> na rota captura o número (ID) do livro da URL
@app.route('/api/livros/<int:id>', methods=['DELETE'])
def deletar_livro(id):
    # 1. Encontrar o livro no banco pelo seu ID (chave primária)
    #    Usamos query.get() que é otimizado para buscar por ID
    livro_para_deletar = Livro.query.get(id)

    # 2. Validação (Req. #6 - Boas Práticas)
    #    Verificar se o livro com esse ID realmente existe
    if not livro_para_deletar:
        # 404 = Not Found
        return jsonify({'erro': 'Livro não encontrado com este ID.'}), 404

    # 3. Se encontrou, deletar o livro
    try:
        db.session.delete(livro_para_deletar)
        db.session.commit()
        # Retorna uma mensagem de sucesso
        return jsonify({'mensagem': f'Livro "{livro_para_deletar.titulo}" foi deletado com sucesso.'}), 200 # 200 = OK
    
    except Exception as e:
        # Se algo der errado no commit, desfazemos
        db.session.rollback()
        return jsonify({'erro': f'Erro ao deletar o livro: {str(e)}'}), 500 # 500 = Internal Server Error
# FIM DA ATUALIZAÇÃO 5

# ATUALIZAÇÃO 6: ROTA PARA ATUALIZAR UM LIVRO
@app.route('/api/livros/<int:id>', methods=['PUT'])
def atualizar_livro(id):
    # 1. Encontrar o livro no banco
    livro = Livro.query.get(id)
    
    if not livro:
        return jsonify({'erro': 'Livro não encontrado'}), 404

    # 2. Pegar os dados JSON da requisição
    dados = request.get_json()

    # 3. Atualizar o campo (só atualizamos a avaliação)
    #    Usamos .get() para não dar erro se o JSON não vier
    if 'avaliacao' in dados:
        try:
            livro.avaliacao = int(dados['avaliacao'])
        except ValueError:
            return jsonify({'erro': 'Avaliação deve ser um número'}), 400

    # 4. Salvar as mudanças no banco
    try:
        db.session.commit()
        # Retorna o livro atualizado
        return jsonify(livro.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': f'Erro ao atualizar: {str(e)}'}), 500

# --- FIM DA ROTA PUT ---

# @app.route('/api/livros/exportar', methods=['GET'])
# def exportar_livros_csv():
#     try:
#         # 1. Busca todos os livros no banco (igual ao GET)
#         livros_salvos = Livro.query.all()

#         # 2. Cria um "arquivo" em memória
#         #    StringIO é um arquivo de texto que vive na RAM
#         si = io.StringIO()
        
#         # 3. Prepara o "escritor" de CSV
#         #    csv.writer sabe formatar aspas e vírgulas corretamente
#         writer = csv.writer(si)

#         # 4. Escreve a linha do Cabeçalho (Header)
#         writer.writerow([
#             'ID', 
#             'Google_ID', 
#             'Titulo', 
#             'Autor', 
#             'Ano_Publicacao', 
#             'Avaliacao'
#         ])

#         # 5. Escreve os dados de cada livro
#         for livro in livros_salvos:
#             writer.writerow([
#                 livro.id,
#                 livro.google_api_id,
#                 livro.titulo,
#                 livro.autor,
#                 livro.ano_publicacao,
#                 livro.avaliacao
#             ])
        
#         # 6. Pega o conteúdo completo do arquivo em memória
#         output = si.getvalue()
        
#         # 7. Prepara a resposta do Flask
#         response = make_response(output)
        
#         # 8. Define os "Cabeçalhos HTTP" para forçar o Download
#         #    Isso é o que faz o navegador abrir o "Salvar Como..."
#         response.headers["Content-Disposition"] = "attachment; filename=minha_colecao.csv"
#         #    Isso diz ao navegador que é um arquivo CSV
#         response.headers["Content-Type"] = "text/csv"
        
#         return response

#     except Exception as e:
#         return jsonify({'erro': f'Erro ao gerar CSV: {str(e)}'}), 500

@app.route('/api/livros/relatorio/csv', methods=['GET'])
def get_livros_relatorio_csv():
    """
    Gera um relatório em CSV de todos os livros no banco de dados.
    """
    try:
        livros_salvos = Livro.query.all()

        if not livros_salvos:
            return jsonify({"erro": "Nenhum livro encontrado para o relatório"}), 404

        lista_de_dicionarios = [livro.to_dict() for livro in livros_salvos]

        fieldnames = lista_de_dicionarios[0].keys()

        si = io.StringIO()
        writer = csv.DictWriter(si, fieldnames=fieldnames, delimiter=';')
        
        writer.writeheader()
        writer.writerows(lista_de_dicionarios)

        output = make_response(si.getvalue())
        
        output.headers["Content-Disposition"] = "attachment; filename=relatorio_livros.csv"
        output.headers["Content-type"] = "text/csv"

        si.close()

        return output

    except Exception as e:
        print(f"Erro ao gerar relatório CSV: {e}")
        return jsonify({"erro": "Ocorreu um erro interno ao gerar o relatório"}), 500

@app.route('/')
def index():
    return render_template('index.html', API_URL_FROM_FLASK=API_URL)
    

# ATUALIZAÇÃO 3: PONTO DE EXECUÇÃO
if __name__ == '__main__':
    app.run(debug=True)