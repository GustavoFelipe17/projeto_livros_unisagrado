# tests/test_routes.py
import json

def test_get_livros_vazio(test_client):
    """
    GIVEN um cliente de teste (com um banco em memória limpo)
    WHEN a rota '/api/livros' é chamada (GET)
    THEN verifique se a resposta é 200 OK e uma lista vazia
    """
    # test_client é o "navegador falso" que criamos no conftest.py
    response = test_client.get('/api/livros')

    # Verifica o status code
    assert response.status_code == 200

    # Verifica se o conteúdo é uma lista vazia
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) == 0

def test_post_and_get_livro(test_client):
    """
    GIVEN um cliente de teste
    WHEN a rota '/api/livros' é chamada (POST) com dados de um livro
    THEN verifique se a resposta é 201 Created
    AND WHEN a rota '/api/livros' é chamada (GET) novamente
    THEN verifique se a resposta é 200 OK e contém o livro que foi criado
    """
    # Dados do livro de teste
    livro_data = {
        "google_api_id": "teste123",
        "titulo": "Livro de Teste",
        "autor": "Autor Teste",
        "ano_publicacao": "2025"
    }

    # 1. Teste do POST
    response_post = test_client.post('/api/livros', json=livro_data)

    # Verifica o status code
    assert response_post.status_code == 201 # 201 = Created

    # 2. Teste do GET (para ver se salvou)
    response_get = test_client.get('/api/livros')

    assert response_get.status_code == 200
    data = json.loads(response_get.data)

    # Verifica se agora temos 1 livro na lista
    assert len(data) == 1
    # Verifica se o título do livro é o que salvamos
    assert data[0]['titulo'] == "Livro de Teste"