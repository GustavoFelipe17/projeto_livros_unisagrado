import os
from flask import Flask, render_template
from flask_cors import CORS
from dotenv import load_dotenv

from .models import db
from .routes import api

def create_app(config_overrides=None):
    
    load_dotenv() 
    
    app = Flask(__name__)
    CORS(app)

    if config_overrides:
        app.config.update(config_overrides)
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    app.register_blueprint(api, url_prefix='/api')

    @app.route('/')
    def index():
        return render_template('index.html')
        
    return app