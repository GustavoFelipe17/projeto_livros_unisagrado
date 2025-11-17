# tests/conftest.py
import pytest
from app import create_app
from app.models import db

@pytest.fixture(scope='module')
def test_app():
    """Cria uma instância do app Flask para testes."""

    # 1. Configurações que vão SUBSTITUIR as do .env
    config_overrides = {
        "TESTING": True,
        # Usa um banco de dados SQLite em memória
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
        "LOGIN_DISABLED": True
    }

    # 2. Chama a nossa fábrica com essas configurações
    app = create_app(config_overrides)

    # 3. Cria um "contexto" para o app
    with app.app_context():
        # 4. Cria o banco DE DADOS EM MEMÓRIA
        db.create_all()

        # 5. Entrega (yield) o app para o teste
        yield app

        # 6. (Depois que o teste rodar) Limpa tudo
        db.drop_all()

@pytest.fixture(scope='module')
def test_client(test_app):
    """Cria um 'cliente' de teste (um navegador falso)."""
    return test_app.test_client()