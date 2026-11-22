# VenceCerto

SaaS multiempresa de controle de validade, estoque e prevenção de perdas para supermercados.

> **Estado: em desenvolvimento inicial — NÃO está pronto para produção.**
> Leia [DEVELOPMENT_STATUS.md](DEVELOPMENT_STATUS.md) para o que existe e o que falta.

## O que está implementado e testado
Regras de negócio puras em `backend/app/domain/` (31 testes automatizados):
- `expiry.py` — classificação de lotes (dentro da validade, próximo, urgente, vencido, esgotado) com prazos configuráveis.
- `pvps.py` — Primeiro que Vence, Primeiro que Sai: ignora lotes vencidos/vazios, divide a baixa entre lotes, desempate determinístico.
- `promotions.py` — recomendação explicável de promoção; nunca vende abaixo do custo sem autorização de administrador.
- `insights.py` — previsão de demanda (média móvel ponderada), sugestão de reposição e padrões de desperdício, atrás do protocolo `DemandForecaster`. IA externa é opcional (`AI_PROVIDER=none`) e não implementada.

## O que NÃO está implementado
API FastAPI, banco/models/migrations, autenticação, multi-tenant, CRUDs, estoque transacional, alertas/scheduler,
dashboard, relatórios, auditoria, frontend, seed, testes de integração/E2E, CD (staging/produção).
`docker-compose.yml` referencia esses itens e, por isso, ainda não sobe o sistema completo.

## Ver a demonstração
```powershell
cd backend
pip install -r requirements-demo.txt
python -m uvicorn app.main:app --reload
```
Abra http://localhost:8000 (página) ou http://localhost:8000/docs (API). Sem banco e sem login.

## Executar os testes
```bash
cd backend
python -m pip install pytest      # Python 3.12+
python -m pytest -q
```

## Documentação
- [docs/product-vision.md](docs/product-vision.md) — visão, princípios e política de IA
- [docs/design-identity.md](docs/design-identity.md) — identidade visual (rascunho)
- [docs/installation.md](docs/installation.md) — instalação e continuação em outro computador
- [docs/testing.md](docs/testing.md) — testes

## Segurança
Nunca versione `.env`. Use `.env.example` como modelo e troque todos os segredos.
