# app/__init__.py
import os
from flask import Flask, render_template
from flask_cors import CORS
from dotenv import load_dotenv

# Importamos nossos módulos criados
from .models import db
from .routes import api

def create_app():
    """Fábrica de Aplicação (Application Factory)"""
    
    # Carrega variáveis de ambiente
    load_dotenv() # Informa onde está o .env
    
    app = Flask(__name__)
    CORS(app) # Habilita o CORS

    # --- Configuração ---
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # --- Inicialização dos Módulos ---
    
    # 1. Conecta o 'db' (de models.py) com o app Flask
    db.init_app(app)

    # 2. Registra o Blueprint (de routes.py)
    #    Todo endpoint em routes.py será prefixado com /api
    #    Ex: @api.route('/livros') vira http://.../api/livros
    app.register_blueprint(api, url_prefix='/api')

    # Rota de teste da raiz (opcional)
    @app.route('/')
    def index():
        return render_template('index.html')
        
    return app