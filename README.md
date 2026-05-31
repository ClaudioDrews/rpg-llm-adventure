# 🎲 RPG LLM Adventure

**Aventuras Fantásticas alimentadas por IA**

Um jogo de RPG por texto inspirado nos clássicos livros "Aventuras Fantásticas" (Fighting Fantasy), onde você vive uma aventura única gerada por Inteligência Artificial.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## ✨ Características

- 🤖 **Múltiplos LLMs**: Suporte para Ollama (local), OpenAI e Anthropic
- 📱 **Interface Responsiva**: Jogue no PC ou celular
- 🎨 **Design Único**: Interface inspirada em livros antigos de RPG
- 🖥️ **CLI e Web**: Terminal minimalista ou navegador com design completo
- 📝 **Log Automático**: Toda aventura é salva em arquivo de texto
- ⚔️ **20 Rodadas**: História completa com início, meio e fim
- 🎯 **Customizável**: Defina estilo, época, contexto e personagens
- 🌐 **Acesso em Rede**: Jogue do celular conectado na mesma WiFi

---

## 📋 Requisitos

### Sistema
- Python 3.10 ou superior
- Ollama instalado (para uso local) OU API key (OpenAI/Anthropic)

### Hardware Testado
- **CPU**: Intel Core i7-12700H (funciona em configs inferiores)
- **RAM**: 4GB+ (8GB recomendado para Ollama)
- **OS**: Linux (testado no Linux Mint 22.3)

---

## 🚀 Instalação Rápida

### 1. Clone/Baixe o Projeto

```bash
cd ~/Projects  # ou onde preferir
# (extraia o arquivo zip aqui)
cd rpg-llm-adventure
```

### 2. Crie Ambiente Virtual

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

### 3. Instale Dependências

```bash
pip install -r requirements.txt
```

### 4. Configure Ollama (Opcional - para uso local)

```bash
# Se ainda não tiver instalado
curl -fsSL https://ollama.com/install.sh | sh

# Inicie o serviço
ollama serve &

# Baixe um modelo (recomendado: llama3.2)
ollama pull llama3.2

# Ou um modelo maior para melhor qualidade
ollama pull llama3.1
```

---

## 🎮 Como Jogar

### Opção 1: Interface Web (Recomendado)

```bash
cd backend
python main.py
```

Você verá algo como:

```
============================================================
🎲 RPG LLM ADVENTURE - Servidor Iniciado
============================================================

📱 Acesso Local: http://localhost:8000
🌐 Acesso na Rede: http://192.168.1.100:8000

💡 Para acessar do celular:
   1. Conecte o celular na mesma rede WiFi
   2. Abra o navegador e acesse: http://192.168.1.100:8000

============================================================
```

**Agora:**
1. Abra seu navegador em `http://localhost:8000`
2. Ou acesse do celular usando o IP mostrado
3. Configure sua aventura
4. Divirta-se! 🎉

### Opção 2: Terminal (CLI)

```bash
cd cli
chmod +x rpg_cli.py
python rpg_cli.py
```

Interface minimalista perfeita para terminais.

---

## ⚙️ Configuração

### Usando Ollama (Local - Grátis)

1. **LLM Type**: Ollama
2. **Model**: `llama3.2` (ou outro instalado)
3. **API Key**: (deixe em branco)

### Usando OpenAI API

1. **LLM Type**: OpenAI API
2. **Model**: `gpt-4o-mini` (econômico) ou `gpt-4o` (melhor)
3. **API Key**: Sua chave da OpenAI

### Usando Anthropic API

1. **LLM Type**: Anthropic API
2. **Model**: `claude-sonnet-4-20250514`
3. **API Key**: Sua chave da Anthropic

### Personalize Sua Aventura

- **Estilo Narrativo**: épico, humorístico, sombrio, romântico...
- **Época**: medieval, cyberpunk, era vitoriana, pós-apocalíptico...
- **Contexto**: reino em guerra, investigação de mistério, exploração espacial...
- **Protagonista**: descreva seu personagem!
- **Personagens**: magos, aliens, detectives, robôs...

---

## 📱 Jogando no Celular

### Conectar na Mesma Rede

1. Certifique-se de que PC e celular estão na mesma WiFi
2. Inicie o servidor (veja IP exibido no console)
3. No celular, abra o navegador
4. Acesse: `http://192.168.1.XXX:8000` (use o IP correto)

### Dicas
- Interface 100% responsiva
- Funciona offline (se usar Ollama)
- Salve o link como favorito no celular

---

## 📂 Estrutura do Projeto

```
rpg-llm-adventure/
├── backend/              # Servidor FastAPI
│   ├── main.py          # API e servidor web
│   ├── llm_manager.py   # Gerenciador de LLMs
│   └── game_state.py    # Estado do jogo
├── frontend/            # Interface web
│   ├── index.html       # HTML + CSS
│   └── app.js           # JavaScript
├── cli/                 # Interface terminal
│   └── rpg_cli.py       # CLI completa
├── logs/                # Logs das aventuras (auto-criado)
├── requirements.txt     # Dependências Python
└── README.md           # Este arquivo
```

---

## 🎯 Mecânicas do Jogo

### Fluxo de Jogo

1. **Configuração**: Escolha LLM e defina sua aventura
2. **Rodada 1-19**: 
   - Leia a narrativa
   - Escolha entre 3 opções OU crie sua própria ação
   - A IA continua a história
3. **Rodada 20**: Conclusão épica da aventura
4. **Fim**: Baixe o log completo da história

### Opções de Ação

- **Opções 1-3**: Escolhas pré-definidas pela IA
- **Ação Customizada**: Escreva o que quiser fazer!
- **Atalhos** (web): Pressione `1`, `2` ou `3` no teclado

---

## 📝 Logs das Aventuras

Cada aventura completa gera um arquivo `.txt` em `logs/` com:

- Configuração completa da aventura
- Todas as 20 rodadas
- Suas escolhas e ações
- Narrativa completa
- Timestamp

**Exemplo**: `logs/aventura_20250207_143022.txt`

---

## 🐛 Solução de Problemas

### Erro: "Não foi possível conectar ao Ollama"

```bash
# Verifique se Ollama está rodando
ollama serve

# Em outro terminal, teste
ollama list
```

### Erro: "API key inválida"

- Verifique se copiou a chave corretamente
- OpenAI: Deve começar com `sk-`
- Anthropic: Formato diferente

### Erro: "Porta 8000 já em uso"

```bash
# Mate o processo usando a porta
sudo lsof -ti:8000 | xargs kill -9

# Ou use outra porta editando main.py (linha final)
```

### Interface não carrega no celular

1. Verifique se ambos estão na mesma WiFi
2. Desative firewall temporariamente
3. Use o IP correto (192.168.x.x, não 127.0.0.1)

---

## 💡 Dicas e Truques

### Para Melhor Qualidade de História

- Use modelos maiores (llama3.1, gpt-4o, claude-opus)
- Seja específico na configuração
- Descreva bem seu protagonista
- Experimente estilos narrativos diferentes

### Performance

- **Ollama**: Modelos 7B são rápidos, 70B+ são mais lentos mas melhores
- **APIs**: Geralmente mais rápidas, mas custam dinheiro
- **RAM**: 8GB+ recomendado para modelos locais grandes

### Criatividade

- Tente ações customizadas inusitadas!
- Misture gêneros (fantasia + sci-fi)
- Crie protagonistas únicos
- Quebre a quarta parede (às vezes funciona!)

---

## 🔧 Customização Avançada

### Alterar Número de Rodadas

Em `backend/main.py`, procure por `20` e altere para o desejado.

### Mudar Temperatura da IA

Em `backend/llm_manager.py`, altere `temperature: 0.8` para:
- `0.5-0.7`: Mais conservador, consistente
- `0.8-1.0`: Mais criativo, surpreendente

### Adicionar Novo LLM

Edite `llm_manager.py` e adicione método `_generate_novo_llm()`.

---

## 📚 Recursos Adicionais

- [Documentação Ollama](https://ollama.com/docs)
- [API OpenAI](https://platform.openai.com/docs)
- [API Anthropic](https://docs.anthropic.com)
- [FastAPI Docs](https://fastapi.tiangolo.com)

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se livre para:

- Reportar bugs
- Sugerir features
- Melhorar a documentação
- Adicionar novos LLMs
- Criar temas visuais

---

## 📄 Licença

MIT License - Use, modifique e distribua livremente!

---

## 🙏 Agradecimentos

- **Fighting Fantasy** - Ian Livingstone & Steve Jackson
- **Ollama** - LLMs locais incríveis
- **FastAPI** - Framework web moderno
- **Comunidade Open Source** ❤️

---

## 🎲 Que a Aventura Comece!

Criado com 💜 por entusiastas de RPG e IA.

**Boa sorte, aventureiro!** ⚔️🐉✨
