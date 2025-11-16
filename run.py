# run.py
from app import create_app
from app.models import db, Livro

# Chama a fábrica para criar a aplicação
app = create_app()

@app.shell_context_processor
def make_shell_context():
    """
    Torna o 'flask shell' mais fácil de usar.
    Ele automaticamente importa o 'db' e 'Livro'
    para dentro do shell.
    """
    return {'db': db, 'Livro': Livro}

if __name__ == '__main__':
    # Roda o app
    app.run(debug=True)