// RPG LLM Adventure - Frontend JavaScript

// ===== I18N SYSTEM =====

const I18N = {
    pt: {
        pageTitle: 'Aventuras Fantásticas',
        subtitle: 'SISTEMA DE AVENTURA IA',
        systemConfig: 'Configuração do Sistema',
        adventureParams: 'Parâmetros da Aventura',
        aiModel: 'Modelo de IA',
        specificModel: 'Modelo Específico',
        apiKey: 'API Key',
        narrativeStyle: 'Estilo Narrativo',
        era: 'Época',
        context: 'Contexto',
        protagonist: 'Protagonista',
        characters: 'Personagens e Criaturas',
        adventureDuration: 'Duração da Aventura',
        advanced: 'Avançado',
        temperature: 'Temperature',
        maxTokens: 'Max Tokens',
        options: 'Opções',
        customCommand: 'Comando Customizado',
        availableOptions: 'Opções Disponíveis',
        language: 'Idioma / Language',
        loadModels: 'Carregar Modelos',
        startAdventure: 'Iniciar Aventura',
        executeCommand: 'Executar Comando',
        endAdventure: 'Concluir Aventura',
        fullHistory: 'Histórico Completo',
        closeHistory: 'Fechar Histórico',
        preparing: 'Preparando aventura...',
        consulting: 'Consultando o oráculo...',
        ending: 'Concluindo aventura...',
        processing: 'PROCESSANDO DADOS...',
        loading: 'Carregando...',
        round: 'RODADA',
        session: 'SESSÃO',
        endTransmission: 'Fim da Transmissão',
        adventureComplete: 'Aventura concluída!',
        downloadLog: 'Baixar Log Completo',
        rounds8: '8 rodadas (aventura curta)',
        rounds12: '12 rodadas (aventura média)',
        rounds20: '20 rodadas (aventura épica)',
        rounds0: 'Até o fim (sem limite)',
        selectModel: 'Selecione um modelo...',
        clickLoadModels: 'Clique em Carregar Modelos',
        noModels: 'Nenhum modelo encontrado',
        errorLoading: 'Erro ao carregar',
        needApiKey: 'Por favor, insira sua API key!',
        needAction: 'Por favor, descreva sua ação!',
        errorLoadModels: 'Erro ao carregar modelos',
        errorStartGame: 'Erro ao iniciar jogo',
        errorProcessAction: 'Erro ao processar ação',
        errorEndAdventure: 'Erro ao concluir aventura',
        bookMode: 'Modo Livro',
        terminalMode: 'Modo Terminal',
        noRounds: 'Nenhuma rodada registrada ainda.',
        roundLabel: 'Rodada',
        action: 'Ação',
        waiting: 'aguardando',
        apiKeyPlaceholder: 'Sua API key',
        customPlaceholder: 'Digite sua ação...',
    },
    en: {
        pageTitle: 'Fantastic Adventures',
        subtitle: 'AI ADVENTURE SYSTEM',
        systemConfig: 'System Configuration',
        adventureParams: 'Adventure Parameters',
        aiModel: 'AI Model',
        specificModel: 'Specific Model',
        apiKey: 'API Key',
        narrativeStyle: 'Narrative Style',
        era: 'Era',
        context: 'Context',
        protagonist: 'Protagonist',
        characters: 'Characters and Creatures',
        adventureDuration: 'Adventure Duration',
        advanced: 'Advanced',
        temperature: 'Temperature',
        maxTokens: 'Max Tokens',
        options: 'Options',
        customCommand: 'Custom Command',
        availableOptions: 'Available Options',
        language: 'Idioma / Language',
        loadModels: 'Load Models',
        startAdventure: 'Start Adventure',
        executeCommand: 'Execute Command',
        endAdventure: 'End Adventure',
        fullHistory: 'Full History',
        closeHistory: 'Close History',
        preparing: 'Preparing adventure...',
        consulting: 'Consulting the oracle...',
        ending: 'Ending adventure...',
        processing: 'PROCESSING DATA...',
        loading: 'Loading...',
        round: 'ROUND',
        session: 'SESSION',
        endTransmission: 'End of Transmission',
        adventureComplete: 'Adventure complete!',
        downloadLog: 'Download Full Log',
        rounds8: '8 rounds (short adventure)',
        rounds12: '12 rounds (medium adventure)',
        rounds20: '20 rounds (epic adventure)',
        rounds0: 'Until the end (no limit)',
        selectModel: 'Select a model...',
        clickLoadModels: 'Click Load Models',
        noModels: 'No models found',
        errorLoading: 'Error loading',
        needApiKey: 'Please enter your API key!',
        needAction: 'Please describe your action!',
        errorLoadModels: 'Error loading models',
        errorStartGame: 'Error starting game',
        errorProcessAction: 'Error processing action',
        errorEndAdventure: 'Error ending adventure',
        bookMode: 'Book Mode',
        terminalMode: 'Terminal Mode',
        noRounds: 'No rounds recorded yet.',
        roundLabel: 'Round',
        action: 'Action',
        waiting: 'pending',
        apiKeyPlaceholder: 'Your API key',
        customPlaceholder: 'Type your action...',
    }
};

// Language detection and persistence
let currentLang = 'pt';

function detectLanguage() {
    const browserLang = navigator.language || '';
    return browserLang.startsWith('pt') ? 'pt' : 'en';
}

function t(key) {
    return (I18N[currentLang] && I18N[currentLang][key]) || (I18N['pt'][key]) || key;
}

function setLanguage(lang) {
    currentLang = lang;
    localStorage.setItem('rpg-lang', lang);
    renderUI();
}

// ===== GAME STATE =====

let gameState = {
    sessionId: null,
    currentRound: 0,
    isPlaying: false,
    isSubmitting: false,
    history: []
};

const OLLAMA_MODELS_OPENAI = ['gpt-4o-mini', 'gpt-4o', 'gpt-4.1-nano'];
const OLLAMA_MODELS_ANTHROPIC = ['claude-sonnet-4-20250514', 'claude-haiku-3-5'];

function populateModelSelect(models) {
    const select = document.getElementById('llm-model');
    select.innerHTML = '';
    models.forEach(model => {
        const option = document.createElement('option');
        option.value = model;
        option.textContent = model;
        select.appendChild(option);
    });
}

async function fetchOllamaModels() {
    const btn = document.getElementById('load-models-btn');
    btn.disabled = true;
    btn.textContent = t('loading');
    try {
        const response = await fetch('/api/ollama/models');
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || t('errorLoadModels'));
        }
        const data = await response.json();
        populateModelSelect(data.models);
        if (data.models.length === 0) {
            const select = document.getElementById('llm-model');
            select.innerHTML = '<option value="">' + t('noModels') + '</option>';
        }
    } catch (error) {
        console.error('Erro ao carregar modelos:', error);
        showError(error.message);
        const select = document.getElementById('llm-model');
        select.innerHTML = '<option value="">' + t('errorLoading') + '</option>';
    } finally {
        btn.disabled = false;
        btn.textContent = t('loadModels');
    }
}

// Configurar visibilidade de API key
document.getElementById('llm-type').addEventListener('change', (e) => {
    const apiKeyGroup = document.getElementById('api-key-group');
    const loadModelsBtn = document.getElementById('load-models-btn');
    
    const llmType = e.target.value;
    
    // Mostrar/ocultar API key
    if (llmType === 'ollama') {
        apiKeyGroup.classList.add('hidden');
        loadModelsBtn.classList.remove('hidden');
        const select = document.getElementById('llm-model');
        select.innerHTML = '<option value="">' + t('clickLoadModels') + '</option>';
    } else {
        apiKeyGroup.classList.remove('hidden');
        loadModelsBtn.classList.add('hidden');
        if (llmType === 'openai') {
            populateModelSelect(OLLAMA_MODELS_OPENAI);
        } else if (llmType === 'anthropic') {
            populateModelSelect(OLLAMA_MODELS_ANTHROPIC);
        }
    }
});

// Event listener do botão Carregar Modelos
document.getElementById('load-models-btn').addEventListener('click', fetchOllamaModels);

// Função de erro com fade-out automático
function showError(message) {
    const container = document.querySelector('.content');
    const existing = document.getElementById('error-msg');
    if (existing) existing.remove();

    const errorDiv = document.createElement('div');
    errorDiv.id = 'error-msg';
    errorDiv.style.cssText = `
        background: #3a1111;
        border: 1px solid #cc3333;
        color: #ff6666;
        padding: 1rem;
        border-radius: 4px;
        margin-bottom: 1rem;
        text-align: center;
        font-size: 1.1rem;
        transition: opacity 0.5s ease;
    `;
    errorDiv.textContent = `⚠ ${message}`;
    container.prepend(errorDiv);

    // Fade-out automático após 5 segundos
    setTimeout(() => {
        errorDiv.style.opacity = '0';
        setTimeout(() => {
            if (errorDiv.parentNode) errorDiv.remove();
        }, 500);
    }, 5000);
}

// Iniciar aventura
async function startAdventure() {
    const setup = {
        llm_type: document.getElementById('llm-type').value,
        llm_model: document.getElementById('llm-model').value,
        api_key: document.getElementById('api-key').value || null,
        narrative_style: document.getElementById('narrative-style').value,
        era: document.getElementById('era').value,
        context: document.getElementById('context').value,
        protagonist: document.getElementById('protagonist').value,
        characters: document.getElementById('characters').value,
        temperature: parseFloat(document.getElementById('temperature').value) || 0.8,
        max_tokens: parseInt(document.getElementById('max-tokens').value) || 512,
        total_rounds: parseInt(document.getElementById('total-rounds').value) || 20,
        lang: currentLang
    };

    // Validação
    if (setup.llm_type !== 'ollama' && !setup.api_key) {
        showError(t('needApiKey'));
        return;
    }

    // Resetar histórico ao iniciar nova aventura
    gameState.history = [];

    // Mostrar loading com mensagem de start
    showScreen('loading-screen', t('preparing'));

    try {
        const response = await fetch('/api/game/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(setup)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || t('errorStartGame'));
        }

        const data = await response.json();
        
        // Atualizar estado
        gameState.sessionId = data.session_id;
        gameState.currentRound = data.round;
        gameState.isPlaying = true;

        // Mostrar primeira rodada
        displayRound(data);
        showScreen('game-screen');

    } catch (error) {
        console.error('Erro:', error);
        showError(error.message);
        showScreen('setup-screen');
    }
}

// Exibir rodada
function displayRound(data) {
    // Atualizar contador
    document.getElementById('current-round').textContent = data.round;
    document.getElementById('session-id').textContent = data.session_id.substring(0, 8);

    // Exibir narrativa
    const narrativeEl = document.getElementById('narrative-text');
    narrativeEl.textContent = data.narrative;
    
    // Scroll suave para narrativa
    narrativeEl.scrollIntoView({ behavior: 'smooth', block: 'start' });

    if (data.is_final) {
        // Rodada final
        document.getElementById('options-section').classList.add('hidden');
        document.getElementById('final-section').classList.remove('hidden');
        
        if (data.log_file) {
            const logDownload = document.getElementById('log-download');
            logDownload.innerHTML = `
                ✅ ${t('adventureComplete')}<br>
                <a href="/api/logs/${data.log_file}" class="download-link" download>
                    📥 ${t('downloadLog')}
                </a>
            `;
        }
    } else {
        // Exibir opções
        document.getElementById('options-section').classList.remove('hidden');
        displayOptions(data.options);
        
        // Limpar input customizado
        document.getElementById('custom-input').value = '';
    }
}

// Exibir opções
function displayOptions(options) {
    const container = document.getElementById('options-container');
    container.innerHTML = '';

    options.forEach((option, index) => {
        const btn = document.createElement('button');
        btn.className = 'option-btn';
        btn.setAttribute('data-number', index + 1);
        btn.onclick = () => selectOption(index + 1);
        
        const textDiv = document.createElement('div');
        textDiv.className = 'option-text';
        textDiv.textContent = option;
        
        btn.appendChild(textDiv);
        container.appendChild(btn);
    });
}

// Selecionar opção
async function selectOption(optionNumber) {
    await submitAction(optionNumber.toString());
}

// Submeter ação customizada
async function submitCustomAction() {
    if (gameState.isSubmitting) return;

    const customInput = document.getElementById('custom-input');
    const action = customInput.value.trim();

    if (!action) {
        showError(t('needAction'));
        return;
    }

    await submitAction(action);
}

// Submeter ação
async function submitAction(action) {
    if (gameState.isSubmitting) return;
    gameState.isSubmitting = true;
    try {
        // Salvar rodada atual no histórico ANTES de buscar a próxima
        if (gameState.currentRound > 0) {
            const narrativeEl = document.getElementById('narrative-text');
            gameState.history.push({
                round: gameState.currentRound,
                narrative: narrativeEl.textContent,
                player_action: action
            });
        }
    
        // Mostrar loading
        showScreen('loading-screen', t('consulting'));
    
        try {
            const response = await fetch('/api/game/action', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    session_id: gameState.sessionId,
                    action: action
                })
            });
    
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || t('errorProcessAction'));
            }
    
            const data = await response.json();
            
            // Atualizar estado
            gameState.currentRound = data.round;
    
            // Exibir próxima rodada
            displayRound(data);
            showScreen('game-screen');
    
        } catch (error) {
            console.error('Erro:', error);
            showError(error.message);
            showScreen('game-screen');
        }
    } finally {
        gameState.isSubmitting = false;
    }
}

// Trocar telas
function showScreen(screenId, loadingMessage) {
    // Ocultar todas as telas
    document.getElementById('setup-screen').classList.add('hidden');
    document.getElementById('game-screen').classList.add('hidden');
    document.getElementById('loading-screen').classList.add('hidden');

    // Mostrar tela desejada
    document.getElementById(screenId).classList.remove('hidden');

    // Se for loading, atualizar mensagem
    if (screenId === 'loading-screen') {
        const loadingText = document.getElementById('loading-text');
        if (loadingText) {
            loadingText.textContent = loadingMessage || t('processing');
        }
    }
}

// ===== TEMA (Modo Terminal / Modo Livro) =====

function toggleTheme() {
    document.body.classList.toggle('livro-mode');
    const isLivro = document.body.classList.contains('livro-mode');
    localStorage.setItem('rpg-theme', isLivro ? 'livro' : 'terminal');

    const btn = document.getElementById('theme-toggle');
    if (btn) {
        btn.textContent = isLivro ? t('terminalMode') : t('bookMode');
    }
}

// Restaurar tema salvo ao carregar
function restoreTheme() {
    const savedTheme = localStorage.getItem('rpg-theme');
    if (savedTheme === 'livro') {
        document.body.classList.add('livro-mode');
        const btn = document.getElementById('theme-toggle');
        if (btn) btn.textContent = t('terminalMode');
    }
}

// ===== HISTÓRICO (Accordion) =====

function renderHistory() {
    const accordion = document.getElementById('history-accordion');
    if (!accordion) return;

    accordion.innerHTML = '';

    if (gameState.history.length === 0) {
        accordion.innerHTML = '<p style="color:#888; text-align:center; padding:1rem;">' + t('noRounds') + '</p>';
        return;
    }

    gameState.history.forEach((entry) => {
        const entryDiv = document.createElement('div');
        entryDiv.style.cssText = `
            margin-bottom: 1rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid rgba(51, 255, 51, 0.2);
        `;

        const roundHeader = document.createElement('div');
        roundHeader.style.cssText = `
            font-weight: bold;
            color: var(--terminal-bright);
            margin-bottom: 0.3rem;
            font-size: 1.1rem;
        `;
        roundHeader.textContent = t('roundLabel') + ' ' + entry.round;

        const narrativeText = document.createElement('div');
        narrativeText.style.cssText = `
            color: var(--terminal-green);
            margin-bottom: 0.3rem;
            opacity: 0.9;
        `;
        const truncatedNarrative = entry.narrative.length > 200
            ? entry.narrative.substring(0, 200) + '...'
            : entry.narrative;
        narrativeText.textContent = truncatedNarrative;

        const actionText = document.createElement('div');
        actionText.style.cssText = `
            color: var(--terminal-dim);
            font-style: italic;
            font-size: 0.95rem;
        `;
        actionText.textContent = '➜ ' + t('action') + ': ' + (entry.player_action || '(' + t('waiting') + ')');

        entryDiv.appendChild(roundHeader);
        entryDiv.appendChild(narrativeText);
        entryDiv.appendChild(actionText);
        accordion.appendChild(entryDiv);
    });
}

// ===== CONCLUIR AVENTURA =====

async function endAdventure() {
    if (gameState.isSubmitting) return;
    gameState.isSubmitting = true;
    try {
        showScreen('loading-screen', t('ending'));
        
        const response = await fetch('/api/game/end', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: gameState.sessionId })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || t('errorEndAdventure'));
        }
        
        const data = await response.json();
        gameState.currentRound = data.round;
        displayRound(data);
        showScreen('game-screen');
        
    } catch (error) {
        console.error('Erro:', error);
        showError(error.message);
        showScreen('game-screen');
    } finally {
        gameState.isSubmitting = false;
    }
}

// ===== RENDER UI (i18n) =====

function renderUI() {
    // Page title
    document.title = '🎲 ' + t('pageTitle');

    // Header
    const gameTitle = document.getElementById('game-title');
    if (gameTitle) gameTitle.textContent = t('pageTitle');
    const gameSubtitle = document.getElementById('game-subtitle');
    if (gameSubtitle) gameSubtitle.textContent = t('subtitle');

    // Section titles
    const sectionSystem = document.getElementById('section-title-system');
    if (sectionSystem) sectionSystem.textContent = t('systemConfig');
    const sectionParams = document.getElementById('section-title-params');
    if (sectionParams) sectionParams.textContent = t('adventureParams');

    // Options/summary titles
    const optionsSummary = document.getElementById('options-summary');
    if (optionsSummary) optionsSummary.textContent = t('options');
    const advancedSummary = document.getElementById('advanced-summary');
    if (advancedSummary) advancedSummary.textContent = t('advanced');

    // Language label
    const langLabel = document.getElementById('lang-label');
    if (langLabel) langLabel.textContent = t('language');

    // Labels by for attribute mapping
    const labelMap = {
        'llm-type': 'aiModel',
        'llm-model': 'specificModel',
        'api-key': 'apiKey',
        'temperature': 'temperature',
        'max-tokens': 'maxTokens',
        'narrative-style': 'narrativeStyle',
        'era': 'era',
        'context': 'context',
        'protagonist': 'protagonist',
        'characters': 'characters',
        'total-rounds': 'adventureDuration',
    };
    document.querySelectorAll('label[for]').forEach(label => {
        const key = labelMap[label.getAttribute('for')];
        if (key) label.textContent = t(key);
    });

    // Custom command label
    const cmdLabel = document.getElementById('custom-cmd-label');
    if (cmdLabel) cmdLabel.textContent = t('customCommand') + ':';

    // Buttons
    const loadBtn = document.getElementById('load-models-btn');
    if (loadBtn && !loadBtn.disabled) loadBtn.textContent = t('loadModels');
    const startBtn = document.getElementById('start-btn');
    if (startBtn) startBtn.textContent = t('startAdventure');
    const executeBtn = document.getElementById('execute-cmd-btn');
    if (executeBtn) executeBtn.textContent = t('executeCommand');
    const endBtn = document.getElementById('end-game-btn');
    if (endBtn) endBtn.textContent = t('endAdventure');

    // Theme toggle
    const themeBtn = document.getElementById('theme-toggle');
    if (themeBtn) {
        const isLivro = document.body.classList.contains('livro-mode');
        themeBtn.textContent = isLivro ? t('terminalMode') : t('bookMode');
    }

    // History toggle (default state)
    const historyBtn = document.getElementById('history-toggle-btn');
    const historyAccordion = document.getElementById('history-accordion');
    if (historyBtn && historyAccordion && historyAccordion.classList.contains('hidden')) {
        historyBtn.textContent = t('fullHistory');
    }

    // Game screen section titles
    const optionsTitle = document.getElementById('options-title');
    if (optionsTitle) optionsTitle.textContent = t('availableOptions');
    const finalTitle = document.getElementById('final-title');
    if (finalTitle) finalTitle.textContent = t('endTransmission');

    // Status bar labels
    const roundLabel = document.getElementById('round-label');
    if (roundLabel) roundLabel.textContent = t('round');
    const sessionLabel = document.getElementById('session-label');
    if (sessionLabel) sessionLabel.textContent = t('session') + ':';

    // Select options (total-rounds)
    const totalRounds = document.getElementById('total-rounds');
    if (totalRounds) {
        const savedValue = totalRounds.value;
        const optionsMap = {
            '8': t('rounds8'),
            '12': t('rounds12'),
            '20': t('rounds20'),
            '0': t('rounds0'),
        };
        for (const opt of totalRounds.options) {
            if (optionsMap[opt.value]) opt.textContent = optionsMap[opt.value];
        }
        totalRounds.value = savedValue;
    }

    // Placeholders
    const apiKeyInput = document.getElementById('api-key');
    if (apiKeyInput) apiKeyInput.placeholder = t('apiKeyPlaceholder');
    const customInput = document.getElementById('custom-input');
    if (customInput) customInput.placeholder = t('customPlaceholder');
}

// ===== EVENT LISTENERS =====

document.addEventListener('DOMContentLoaded', () => {
    // Initialize language
    const savedLang = localStorage.getItem('rpg-lang');
    currentLang = savedLang || detectLanguage();
    renderUI();

    // Language selector
    const langSelect = document.getElementById('lang-select');
    if (langSelect) {
        langSelect.value = currentLang;
        langSelect.addEventListener('change', (e) => {
            setLanguage(e.target.value);
        });
    }

    // Theme
    restoreTheme();

    const themeBtn = document.getElementById('theme-toggle');
    if (themeBtn) {
        themeBtn.addEventListener('click', toggleTheme);
    }

    // Histórico toggle
    const historyBtn = document.getElementById('history-toggle-btn');
    const historyAccordion = document.getElementById('history-accordion');
    if (historyBtn && historyAccordion) {
        historyBtn.addEventListener('click', () => {
            const isHidden = historyAccordion.classList.contains('hidden');
            if (isHidden) {
                historyAccordion.classList.remove('hidden');
                renderHistory();
                historyBtn.textContent = t('closeHistory');
            } else {
                historyAccordion.classList.add('hidden');
                historyBtn.textContent = t('fullHistory');
            }
        });
    }

    // Concluir Aventura
    const endGameBtn = document.getElementById('end-game-btn');
    if (endGameBtn) {
        endGameBtn.addEventListener('click', endAdventure);
    }
});

// Atalhos de teclado
document.addEventListener('keydown', (e) => {
    if (!gameState.isPlaying) return;

    // Números 1-3 para opções
    if (e.key >= '1' && e.key <= '3') {
        const optionBtns = document.querySelectorAll('.option-btn');
        const index = parseInt(e.key) - 1;
        if (optionBtns[index]) {
            selectOption(parseInt(e.key));
        }
    }

    // Enter no input customizado
    if (e.key === 'Enter' && document.activeElement.id === 'custom-input') {
        e.preventDefault();
        submitCustomAction();
    }
});

// Easter egg: logo animado
let clickCount = 0;
document.addEventListener('DOMContentLoaded', () => {
    const h1 = document.getElementById('game-title');
    if (h1) {
        h1.addEventListener('click', () => {
            clickCount++;
            if (clickCount === 3) {
                h1.style.animation = 'spin 1s ease-in-out';
                setTimeout(() => {
                    h1.style.animation = '';
                    clickCount = 0;
                }, 1000);
            }
        });
    }
});
