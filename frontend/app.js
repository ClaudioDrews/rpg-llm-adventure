// RPG LLM Adventure - Frontend JavaScript

let gameState = {
    sessionId: null,
    currentRound: 0,
    isPlaying: false
};

document.getElementById('llm-type').addEventListener('change', (e) => {
    const apiKeyGroup = document.getElementById('api-key-group');
    const modelInput = document.getElementById('llm-model');
    const llmType = e.target.value;
    if (llmType === 'ollama') {
        apiKeyGroup.classList.add('hidden');
        modelInput.value = 'llama3.2';
    } else {
        apiKeyGroup.classList.remove('hidden');
        if (llmType === 'openai') modelInput.value = 'gpt-4o-mini';
        else if (llmType === 'anthropic') modelInput.value = 'claude-sonnet-4-20250514';
    }
});

async function startAdventure() {
    const setup = {
        llm_type: document.getElementById('llm-type').value,
        llm_model: document.getElementById('llm-model').value,
        api_key: document.getElementById('api-key').value || null,
        narrative_style: document.getElementById('narrative-style').value,
        era: document.getElementById('era').value,
        context: document.getElementById('context').value,
        protagonist: document.getElementById('protagonist').value,
        characters: document.getElementById('characters').value
    };
    if (setup.llm_type !== 'ollama' && !setup.api_key) {
        alert('⚠️ Por favor, insira sua API key!');
        return;
    }
    showScreen('loading-screen');
    try {
        const response = await fetch('/api/game/start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(setup)
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Erro ao iniciar jogo');
        }
        const data = await response.json();
        gameState.sessionId = data.session_id;
        gameState.currentRound = data.round;
        gameState.isPlaying = true;
        displayRound(data);
        showScreen('game-screen');
    } catch (error) {
        console.error('Erro:', error);
        alert(`❌ Erro: ${error.message}`);
        showScreen('setup-screen');
    }
}

function displayRound(data) {
    document.getElementById('current-round').textContent = data.round;
    document.getElementById('session-id').textContent = data.session_id.substring(0, 8);
    const narrativeEl = document.getElementById('narrative-text');
    narrativeEl.textContent = data.narrative;
    narrativeEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
    if (data.is_final) {
        document.getElementById('options-section').classList.add('hidden');
        document.getElementById('final-section').classList.remove('hidden');
        if (data.log_file) {
            document.getElementById('log-download').innerHTML = `✅ Aventura concluída!<br><a href="/api/logs/${data.log_file}" class="download-link" download>📥 Baixar Log Completo</a>`;
        }
    } else {
        document.getElementById('options-section').classList.remove('hidden');
        displayOptions(data.options);
        document.getElementById('custom-input').value = '';
    }
}

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

async function selectOption(optionNumber) {
    await submitAction(optionNumber.toString());
}

async function submitCustomAction() {
    const customInput = document.getElementById('custom-input');
    const action = customInput.value.trim();
    if (!action) { alert('⚠️ Por favor, descreva sua ação!'); return; }
    await submitAction(action);
}

async function submitAction(action) {
    showScreen('loading-screen');
    try {
        const response = await fetch('/api/game/action', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: gameState.sessionId, action: action })
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Erro ao processar ação');
        }
        const data = await response.json();
        gameState.currentRound = data.round;
        displayRound(data);
        showScreen('game-screen');
    } catch (error) {
        console.error('Erro:', error);
        alert(`❌ Erro: ${error.message}`);
        showScreen('game-screen');
    }
}

function showScreen(screenId) {
    document.getElementById('setup-screen').classList.add('hidden');
    document.getElementById('game-screen').classList.add('hidden');
    document.getElementById('loading-screen').classList.add('hidden');
    document.getElementById(screenId).classList.remove('hidden');
}

document.addEventListener('keydown', (e) => {
    if (!gameState.isPlaying) return;
    if (e.key >= '1' && e.key <= '3') {
        const optionBtns = document.querySelectorAll('.option-btn');
        const index = parseInt(e.key) - 1;
        if (optionBtns[index]) selectOption(parseInt(e.key));
    }
    if (e.key === 'Enter' && document.activeElement.id === 'custom-input') {
        e.preventDefault();
        submitCustomAction();
    }
});

let clickCount = 0;
document.querySelector('h1').addEventListener('click', () => {
    clickCount++;
    if (clickCount === 3) {
        document.querySelector('h1').style.animation = 'spin 1s ease-in-out';
        setTimeout(() => { document.querySelector('h1').style.animation = ''; clickCount = 0; }, 1000);
    }
});
