// --- "Pontes" para os elementos do HTML ---
const campoBusca = document.getElementById('campo-busca');
const botaoBuscar = document.getElementById('botao-buscar');
const containerResultados = document.getElementById('container-resultados');
const containerSalvos = document.getElementById('container-salvos');
const botaoExportar = document.getElementById('botao-exportar');

// --- CONSTANTE DA NOSSA API ---
// O endereço do nosso servidor backend (Flask)
const API_BASE_URL = '/api';

// --- "Ouvintes" de Eventos ---
// O que acontece quando o usuário clica em "Buscar"
botaoBuscar.addEventListener('click', buscarLivros);
botaoExportar.addEventListener('click', exportarParaCSV); // <-- ADICIONA O OUVINTE CORRETO

// Combina os dois "DOMContentLoaded" em um só
document.addEventListener('DOMContentLoaded', () => {
    carregarLivrosSalvos();
});

// --- FUNÇÕES PRINCIPAIS ---

/**
 * Função 1: Buscar Livros (Fase 3 da API)
 * É chamada quando o usuário clica em "Buscar".
 */
async function buscarLivros() {
    const termo = campoBusca.value;
    if (!termo) {
        alert('Por favor, digite um termo para buscar.');
        return;
    }

    // Limpa os resultados antigos
    containerResultados.innerHTML = 'Carregando...';

    try {
        // 1. CHAMA A NOSSA API FLASK (GET /api/buscar)
        const response = await fetch(`${API_BASE_URL}/buscar?termo=${termo}`);
        
        if (!response.ok) {
            throw new Error('Falha ao buscar dados do Google. Status: ' + response.status);
        }

        const livrosEncontrados = await response.json();

        // 2. MOSTRA OS RESULTADOS NA TELA
        mostrarResultadosBusca(livrosEncontrados);

    } catch (error) {
        console.error('Erro ao buscar livros:', error);
        containerResultados.innerHTML = '<p>Erro ao buscar resultados.</p>';
    }
}

/**
 * Função 2: Carregar Livros Salvos (Fase 2 da API)
 * É chamada quando a página carrega.
 */
async function carregarLivrosSalvos() {
    // Limpa a estante antiga
    containerSalvos.innerHTML = 'Carregando...';

    try {
        // 1. CHAMA A NOSSA API FLASK (GET /api/livros)
        const response = await fetch(`${API_BASE_URL}/livros`);

        if (!response.ok) {
            throw new Error('Falha ao buscar livros salvos. Status: ' + response.status);
        }

        const livrosSalvos = await response.json();

        // 2. MOSTRA OS LIVROS SALVOS NA TELA
        mostrarLivrosSalvos(livrosSalvos);

    } catch (error) {
        console.error('Erro ao carregar livros salvos:', error);
        containerSalvos.innerHTML = '<p>Erro ao carregar sua estante de livros salvos.</p>';
    }
}

/**
 * Função 3: Salvar um Livro (Fase 2 da API)
 * É chamada pelo botão "Salvar" de um card de busca.
 */
async function salvarLivro(livro) {
    try {
        // 1. CHAMA A NOSSA API FLASK (POST /api/livros)
        const response = await fetch(`${API_BASE_URL}/livros`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            // Envia os dados do livro no corpo (body) da requisição
            body: JSON.stringify(livro),
        });

        if (response.status === 409) { // 409 = Conflict
            alert('Erro: Este livro já esta salvo na sua estante.');
            return;
        }

        if (!response.ok) {
            throw new Error('Falha ao salvar o livro. Status: ' + response.status);
        }

        const livroSalvo = await response.json();
        console.log('Livro salvo:', livroSalvo);
        
        // 2. ATUALIZA A LISTA DE LIVROS SALVOS
        // Não precisamos recarregar a página inteira!
        carregarLivrosSalvos();

    } catch (error) {
        console.error('Erro ao salvar livro:', error);
        alert('Ocorreu um erro ao tentar salvar o livro.');
    }
}

/**
 * Função 4: Deletar um Livro (Fase 4 da API)
 * É chamada pelo botão "Deletar" de um card salvo.
 */
async function deletarLivro(idDoLivro) {
    // Confirmação com o usuário
    if (!confirm('Tem certeza que deseja retirar este livro da estante?')) {
        return; // Usuário cancelou
    }

    try {
        // 1. CHAMA A NOSSA API FLASK (DELETE /api/livros/<id>)
        const response = await fetch(`${API_BASE_URL}/livros/${idDoLivro}`, {
            method: 'DELETE',
        });

        if (!response.ok) {
            throw new Error('Falha ao deletar o livro. Status: ' + response.status);
        }

        const resultado = await response.json();
        console.log('Mensagem:', resultado.mensagem);

        // 2. ATUALIZA A LISTA DE LIVROS SALVOS
        carregarLivrosSalvos();

    } catch (error) {
        console.error('Erro ao deletar livro:', error);
        alert('Ocorreu um erro ao tentar deletar o livro.');
    }
}

async function atualizarAvaliacao(idDoLivro, avaliacao) {
    console.log(`Atualizando livro ${idDoLivro} para nota ${avaliacao}`);

    try {
        // 1. CHAMA A NOSSA API FLASK (PUT /api/livros/<id>)
        const response = await fetch(`${API_BASE_URL}/livros/${idDoLivro}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            // Envia o JSON com a nova avaliação
            body: JSON.stringify({ "avaliacao": parseInt(avaliacao) })
        });

        if (!response.ok) {
            throw new Error('Falha ao atualizar a avaliação.');
        }

        const livroAtualizado = await response.json();
        console.log('Livro atualizado:', livroAtualizado);

        // 2. ATUALIZA A LISTA (o jeito mais simples)
        // Apenas recarregamos a lista de salvos para mostrar a nova nota
        carregarLivrosSalvos();

    } catch (error) {
        console.error('Erro ao atualizar avaliação:', error);
        alert('Ocorreu um erro ao salvar sua avaliação.');
    }
}

// --- FUNÇÕES "AJUDANTES" (Para criar o HTML) ---

/**
 * Recebe uma lista de livros (da busca) e cria os cards na tela.
 */
function mostrarResultadosBusca(livros) {
    // Limpa a área
    containerResultados.innerHTML = '';

    if (livros.length === 0) {
        containerResultados.innerHTML = '<p>Nenhum livro encontrado.</p>';
        return;
    }

    // Cria um "card" para cada livro
    livros.forEach(livro => {
        const card = document.createElement('div');
        card.className = 'livro-card';
        
        // Usamos uma imagem "placeholder" se não houver capa
        const capaUrl = livro.url_capa || 'https://via.placeholder.com/150?text=Sem+Capa';
        
        card.innerHTML = `
            <img src="${capaUrl}" alt="Capa do ${livro.titulo}">
            <h3>${livro.titulo || 'Título desconhecido'}</h3>
            <p>${livro.autor || 'Autor desconhecido'}</p>
            <p>Ano: ${livro.ano_publicacao || '----'}</p>
            <button class="botao-salvar">Salvar na Coleção</button>
        `;

        // Adiciona o evento de clique no botão "Salvar"
        // Precisamos passar o objeto 'livro' inteiro para a função salvar
        const botaoSalvar = card.querySelector('.botao-salvar');
        botaoSalvar.addEventListener('click', () => salvarLivro(livro));

        containerResultados.appendChild(card);
    });
}

/**
 * Recebe uma lista de livros (salvos) e cria os cards na tela.
 */
function mostrarLivrosSalvos(livros) {
    // Limpa a área
    containerSalvos.innerHTML = '';

    if (livros.length === 0) {
        containerSalvos.innerHTML = '<p>Sua estante esta vazia.</p>';
        return;
    }

    // Cria um "card" para cada livro
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

        // Adiciona o evento de clique no botão "Deletar"
        // Precisamos passar apenas o 'id' do livro para a função deletar
        const botaoDeletar = card.querySelector('.botao-deletar');
        botaoDeletar.addEventListener('click', () => deletarLivro(livro.id));

        const selectAvaliacao = card.querySelector('.select-avaliacao');
        selectAvaliacao.addEventListener('change', (event) => {
            // Pega o valor (ex: "5") e o ID do livro
            const novaAvaliacao = event.target.value;
            const livroId = event.target.dataset.id;

            // Só atualiza se o usuário escolheu uma nota (e não o "Avaliar...")
            if (novaAvaliacao !== "0") {
                atualizarAvaliacao(livroId, novaAvaliacao);
            }
        });

        containerSalvos.appendChild(card);
    });
}

function exportarParaCSV() {
    // Manda o navegador navegar até a URL da API de exportação.
    // O backend força o download (Content-Disposition).
    console.log('Iniciando download do CSV...');
    window.location.href = `${API_BASE_URL}/livros/exportar`; // <-- USA A ROTA CORRETA
}
