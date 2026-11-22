# Instalação e continuidade em outro computador

## Requisitos
Python 3.12+, Node 20+ (para o futuro frontend), Docker + Docker Compose, Git.

## Passos
1. Extraia o ZIP e entre em `VenceCerto/`.
2. `cp .env.example .env` e substitua todos os valores `change-me-*`.
3. Backend (hoje, só o domínio):
   ```bash
   cd backend
   python -m venv .venv && source .venv/bin/activate
   pip install pytest
   python -m pytest -q
   ```
4. `backend/requirements.txt` lista dependências **sem versões fixas**: em um ambiente com rede, instale,
   valide e fixe com `pip freeze`.
5. `git init` e versione (o `.gitignore` já exclui `.env`, caches e `node_modules`).

## Para continuar o desenvolvimento
Siga a seção "Próximos passos" de `DEVELOPMENT_STATUS.md`. `docker compose up --build` só funcionará após
implementar `app.main`, Alembic, scheduler e frontend.
