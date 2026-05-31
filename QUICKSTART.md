# 🚀 GUIA RÁPIDO - RPG LLM ADVENTURE

## Início Imediato (3 passos)

### 1️⃣ Prepare o Ambiente

```bash
./start.sh
```

### 2️⃣ Inicie o Servidor

```bash
cd backend
python main.py
```

### 3️⃣ Acesse e Jogue!

- **PC**: http://localhost:8000
- **Celular**: http://SEU_IP:8000 (veja no terminal)

---

## ⚡ Comandos Úteis

### Verificar Ollama

```bash
ollama list              # Ver modelos instalados
ollama pull llama3.2     # Baixar modelo
ollama serve             # Iniciar serviço
```

### Jogar no Terminal

```bash
cd cli
python rpg_cli.py
```

### Parar Servidor

Pressione `Ctrl+C` no terminal do servidor

---

## 🎮 Primeira Aventura Recomendada

- **LLM**: Ollama
- **Modelo**: llama3.2
- **Estilo**: épico e descritivo
- **Época**: fantasia medieval
- **Contexto**: reino em guerra contra dragões
- **Protagonista**: um jovem cavaleiro em busca de glória
- **Personagens**: dragões, magos, elfos e orcs

---

## 📱 Acesso Mobile

1. Verifique que PC e celular estão na **mesma WiFi**
2. No terminal, copie o IP mostrado (ex: 192.168.1.100)
3. No celular, abra navegador
4. Acesse: `http://192.168.1.100:8000`

---

## ❓ Problemas Comuns

### "Erro ao conectar ao Ollama"
```bash
ollama serve
```

### "Porta 8000 em uso"
```bash
sudo lsof -ti:8000 | xargs kill -9
```

### "API key inválida"
- Verifique se copiou corretamente
- OpenAI keys começam com `sk-`

---

## 💡 Dicas

- **Ações customizadas** são mais divertidas!
- **Experimente estilos** diferentes
- **Misture gêneros**: fantasia + sci-fi funciona!
- **Baixe o log** ao final para relembrar

**Boa aventura!** ⚔️🐉✨
