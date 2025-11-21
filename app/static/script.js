const campoBusca = document.getElementById('campo-busca');
const botaoBuscar = document.getElementById('botao-buscar');
const containerResultados = document.getElementById('container-resultados');
const containerSalvos = document.getElementById('container-salvos');
const botaoExportar = document.getElementById('botao-exportar');

const API_BASE_URL = '/api';

botaoBuscar.addEventListener('click', buscarLivros);
botaoExportar.addEventListener('click', exportarParaCSV);

document.addEventListener('DOMContentLoaded', () => {
    carregarLivrosSalvos();
});

async function buscarLivros() {
    const termo = campoBusca.value;
    if (!termo) {
        alert('Por favor, digite um termo para buscar.');
        return;
    }

    containerResultados.innerHTML = 'Carregando...';

    try {
        const response = await fetch(`${API_BASE_URL}/buscar?termo=${termo}`);
        
        if (!response.ok) {
            throw new Error('Falha ao buscar dados do Google. Status: ' + response.status);
        }

        const livrosEncontrados = await response.json();

        mostrarResultadosBusca(livrosEncontrados);

    } catch (error) {
        console.error('Erro ao buscar livros:', error);
        containerResultados.innerHTML = '<p>Erro ao buscar resultados.</p>';
    }
}

async function carregarLivrosSalvos() {
    containerSalvos.innerHTML = 'Carregando...';

    try {
        const response = await fetch(`${API_BASE_URL}/livros`);

        if (!response.ok) {
            throw new Error('Falha ao buscar livros salvos. Status: ' + response.status);
        }

        const livrosSalvos = await response.json();

        mostrarLivrosSalvos(livrosSalvos);

    } catch (error) {
        console.error('Erro ao carregar livros salvos:', error);
        containerSalvos.innerHTML = '<p>Erro ao carregar sua estante de livros salvos.</p>';
    }
}

async function salvarLivro(livro) {
    try {
        const response = await fetch(`${API_BASE_URL}/livros`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(livro),
        });

        if (response.status === 409) { 
            alert('Erro: Este livro já esta salvo na sua estante.');
            return;
        }

        if (!response.ok) {
            throw new Error('Falha ao salvar o livro. Status: ' + response.status);
        }

        const livroSalvo = await response.json();
        console.log('Livro salvo:', livroSalvo);
        
        carregarLivrosSalvos();

    } catch (error) {
        console.error('Erro ao salvar livro:', error);
        alert('Ocorreu um erro ao tentar salvar o livro.');
    }
}

async function deletarLivro(idDoLivro) {
    if (!confirm('Tem certeza que deseja retirar este livro da estante?')) {
        return; 
    }

    try {
        const response = await fetch(`${API_BASE_URL}/livros/${idDoLivro}`, {
            method: 'DELETE',
        });

        if (!response.ok) {
            throw new Error('Falha ao deletar o livro. Status: ' + response.status);
        }

        const resultado = await response.json();
        console.log('Mensagem:', resultado.mensagem);

        carregarLivrosSalvos();

    } catch (error) {
        console.error('Erro ao deletar livro:', error);
        alert('Ocorreu um erro ao tentar deletar o livro.');
    }
}

async function atualizarAvaliacao(idDoLivro, avaliacao) {
    console.log(`Atualizando livro ${idDoLivro} para nota ${avaliacao}`);

    try {
        const response = await fetch(`${API_BASE_URL}/livros/${idDoLivro}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ "avaliacao": parseInt(avaliacao) })
        });

        if (!response.ok) {
            throw new Error('Falha ao atualizar a avaliação.');
        }

        const livroAtualizado = await response.json();
        console.log('Livro atualizado:', livroAtualizado);

        carregarLivrosSalvos();

    } catch (error) {
        console.error('Erro ao atualizar avaliação:', error);
        alert('Ocorreu um erro ao salvar sua avaliação.');
    }
}

function mostrarResultadosBusca(livros) {
    containerResultados.innerHTML = '';

    if (livros.length === 0) {
        containerResultados.innerHTML = '<p>Nenhum livro encontrado.</p>';
        return;
    }

    livros.forEach(livro => {
        const card = document.createElement('div');
        card.className = 'livro-card';
        
        const capaUrl = livro.url_capa || 'https://via.placeholder.com/150?text=Sem+Capa';
        
        card.innerHTML = `
            <img src="${capaUrl}" alt="Capa do ${livro.titulo}">
            <h3>${livro.titulo || 'Título desconhecido'}</h3>
            <p>${livro.autor || 'Autor desconhecido'}</p>
            <p>Ano: ${livro.ano_publicacao || '----'}</p>
            <button class="botao-salvar">Salvar na Coleção</button>
        `;

        const botaoSalvar = card.querySelector('.botao-salvar');
        botaoSalvar.addEventListener('click', () => salvarLivro(livro));

        containerResultados.appendChild(card);
    });
}

function mostrarLivrosSalvos(livros) {
    containerSalvos.innerHTML = '';

    if (livros.length === 0) {
        containerSalvos.innerHTML = '<p>Sua estante esta vazia.</p>';
        return;
    }

    livros.forEach(livro => {
        const card = document.createElement('div');
        card.className = 'livro-card';

        const capaUrl = livro.url_capa || 'https://via.placeholder.com/150?text=Sem+Capa';

        card.innerHTML = `
            <img src="${capaUrl}" alt="Capa do ${livro.titulo}">
            <h3>${livro.titulo}</h3>
            <p>${livro.autor}</p>
            <p>Ano: ${livro.ano_publicacao}</p>

            <select class="select-avaliacao" data-id="${livro.id}">
                <option value="0">${livro.avaliacao ? 'Sua nota: ' + livro.avaliacao + ' Estrelas' : 'Avaliar...'}</option>
                <option value="1">1 ESTRELA</option>
                <option value="2">2 ESTRELAS</option>
                <option value="3">3 ESTRELAS</option>
                <option value="4">4 ESTRELAS</option>
                <option value="5">5 ESTRELAS</option>
            </select>

            <button class="botao-deletar">Deletar</button>
        `;

        const botaoDeletar = card.querySelector('.botao-deletar');
        botaoDeletar.addEventListener('click', () => deletarLivro(livro.id));

        const selectAvaliacao = card.querySelector('.select-avaliacao');
        selectAvaliacao.addEventListener('change', (event) => {
            const novaAvaliacao = event.target.value;
            const livroId = event.target.dataset.id;

            if (novaAvaliacao !== "0") {
                atualizarAvaliacao(livroId, novaAvaliacao);
            }
        });

        containerSalvos.appendChild(card);
    });
}

function exportarParaCSV() {
    console.log('Iniciando download do CSV...');
    window.location.href = `${API_BASE_URL}/livros/exportar`;
}
