#!/bin/bash

# Script de inicialização rápida do RPG LLM Adventure

set -e

echo "============================================================"
echo "🎲 RPG LLM ADVENTURE - Inicialização"
echo "============================================================"
echo ""

if [ ! -f "requirements.txt" ]; then
    echo "❌ Erro: Execute este script do diretório raiz do projeto!"
    exit 1
fi

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

detect_ip() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        LOCAL_IP=$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null || echo "")
    else
        LOCAL_IP=$(ip route get 1 2>/dev/null | awk '{print $7; exit}' || hostname -I 2>/dev/null | awk '{print $1}' || echo "")
    fi
    if [ -z "$LOCAL_IP" ]; then
        LOCAL_IP="localhost"
    fi
}

OLLAMA_PID=""
cleanup() {
    echo ""
    echo "🛑 Encerrando..."
    if [ -n "$OLLAMA_PID" ]; then
        kill $OLLAMA_PID 2>/dev/null && echo "✓ Ollama encerrado"
    fi
    exit 0
}
trap cleanup EXIT INT TERM

echo "📦 Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 não encontrado!${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✓ Python $PYTHON_VERSION encontrado${NC}"

if [ ! -d "venv" ]; then
    echo ""
    echo "📦 Criando ambiente virtual..."
    python3 -m venv venv
    echo -e "${GREEN}✓ Ambiente virtual criado${NC}"
fi

if [ ! -f "venv/bin/activate" ]; then
    echo -e "${RED}❌ Erro: venv/bin/activate não encontrado${NC}"
    exit 1
fi

echo ""
echo "📦 Ativando ambiente virtual..."
source venv/bin/activate
echo -e "${GREEN}✓ Ambiente ativado${NC}"

echo ""
echo "📦 Instalando dependências..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo -e "${GREEN}✓ Dependências instaladas${NC}"

echo ""
echo "🤖 Verificando Ollama (opcional)..."
if command -v ollama &> /dev/null; then
    echo -e "${GREEN}✓ Ollama encontrado${NC}"
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Ollama já está rodando${NC}"
    else
        echo -e "${YELLOW}⚠ Ollama não está rodando. Iniciando...${NC}"
        ollama serve > /dev/null 2>&1 &
        OLLAMA_PID=$!
        sleep 3
        if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
            echo -e "${GREEN}✓ Ollama iniciado (PID: $OLLAMA_PID)${NC}"
        else
            echo -e "${YELLOW}⚠ Ollama não respondeu, continuando sem...${NC}"
            OLLAMA_PID=""
        fi
    fi
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo ""
        echo "Modelos disponíveis:"
        ollama list 2>/dev/null || echo "  (nenhum modelo encontrado)"
    fi
else
    echo -e "${YELLOW}⚠ Ollama não encontrado (você pode usar APIs em vez disso)${NC}"
fi

mkdir -p logs
mkdir -p backend/logs

echo ""
echo "============================================================"
echo -e "${GREEN}✅ Inicialização Completa!${NC}"
echo "============================================================"
echo ""

detect_ip

echo "📱 Acesso Local:   http://localhost:8000"
echo "🌐 Acesso na Rede: http://$LOCAL_IP:8000"
echo ""
echo "💡 Para celular:   http://$LOCAL_IP:8000"
echo "🛑 Pressione Ctrl+C para parar"
echo "============================================================"
echo ""

if [ ! -f "backend/main.py" ]; then
    echo -e "${RED}❌ Erro: backend/main.py não encontrado!${NC}"
    exit 1
fi

cd backend
python main.py
