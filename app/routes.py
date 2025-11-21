from flask import request, jsonify, make_response, Blueprint
import requests
import csv
import io

from .models import db, Livro

api = Blueprint('api', __name__)

@api.route('/livros', methods=['POST'])
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

@api.route('/livros', methods=['GET'])
def get_livros_salvos():
    livros_salvos = Livro.query.all()
    lista_json = [livro.to_dict() for livro in livros_salvos]
    return jsonify(lista_json)

@api.route('/buscar', methods=['GET'])
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
        return jsonify({'erro': f'Erro ao se comunicar com a Google Books API: {str(e)}'}), 503

@api.route('/livros/<int:id>', methods=['DELETE'])
def deletar_livro(id):
    livro_para_deletar = Livro.query.get(id)
    if not livro_para_deletar:
        return jsonify({'erro': 'Livro não encontrado com este ID.'}), 404
    
    try:
        db.session.delete(livro_para_deletar)
        db.session.commit()
        return jsonify({'mensagem': f'Livro "{livro_para_deletar.titulo}" foi deletado com sucesso.'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': f'Erro ao deletar o livro: {str(e)}'}), 500

@api.route('/livros/<int:id>', methods=['PUT'])
def atualizar_livro(id):
    livro = Livro.query.get(id)
    if not livro:
        return jsonify({'erro': 'Livro não encontrado'}), 404
    
    dados = request.get_json()
    
    if 'avaliacao' in dados:
        try:
            livro.avaliacao = int(dados['avaliacao'])
        except ValueError:
            return jsonify({'erro': 'Avaliação deve ser um número'}), 400
    
    try:
        db.session.commit()
        return jsonify(livro.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': f'Erro ao atualizar: {str(e)}'}), 500

@api.route('/livros/exportar', methods=['GET'])
def exportar_livros_csv():
    try:
        livros_salvos = Livro.query.all()
        si = io.StringIO()
        writer = csv.writer(si)
        writer.writerow(['ID', 'Google_ID', 'Titulo', 'Autor', 'Ano_Publicacao', 'Avaliacao'])
        
        for livro in livros_salvos:
            writer.writerow([
                livro.id,
                livro.google_api_id,
                livro.titulo,
                livro.autor,
                livro.ano_publicacao,
                livro.avaliacao
            ])
        
        output = si.getvalue()
        response = make_response(output)
        response.headers["Content-Disposition"] = "attachment; filename=minha_colecao.csv"
        response.headers["Content-Type"] = "text/csv"
        return response
    
    except Exception as e:
        return jsonify({'erro': f'Erro ao gerar CSV: {str(e)}'}), 500
