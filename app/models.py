# app/models.py
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint

# 1. Criamos a *instância* do SQLAlchemy, mas sem app.
#    O app será conectado a ele depois.
db = SQLAlchemy()

# 2. Colamos nossas classes de modelo aqui
class Livro(db.Model):
    __tablename__ = 'livros'
    
    id = db.Column(db.Integer, primary_key=True)
    google_api_id = db.Column(db.String(100), unique=True, nullable=False)
    titulo = db.Column(db.String(255), nullable=False)
    autor = db.Column(db.String(255))
    ano_publicacao = db.Column(db.String(10))
    url_capa = db.Column(db.String(500))
    avaliacao = db.Column(db.Integer, nullable=True, default=None)

    # Regra de CHECK para a avaliação
    __table_args__ = (
        CheckConstraint('avaliacao >= 1 AND avaliacao <= 5', name='check_avaliacao_range'),
    )

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