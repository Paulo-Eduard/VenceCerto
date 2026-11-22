# DEVELOPMENT_STATUS — VenceCerto

Atualizado: 2026-11-22

## Bloqueio do ambiente
A sessão não tem rede para pip/npm, nem servidor PostgreSQL, e faltam: FastAPI, SQLAlchemy,
Alembic, argon2-cffi, APScheduler, httpx, ruff, Vite/Tailwind etc. Logo, nada que dependa deles
pôde ser executado/validado. **Para continuar:** liberar instalação de pacotes (configurações de
rede) em um chat novo, ou rodar no seu ambiente com Docker.

## Visão de produto atualizada (2026-11-22)
Produto comercializável, identidade própria, núcleo SaaS primeiro. IA somente opcional, justificada e
desacoplada (`AI_PROVIDER=none` por padrão). Ver `docs/product-vision.md` e `docs/design-identity.md`.
Implementado: `app/domain/insights.py` (previsão por média móvel, sugestão de reposição, padrões de
desperdício) atrás do protocolo `DemandForecaster`. Nenhum provedor de IA externo foi implementado
(de propósito: sem histórico de vendas no escopo, não há ganho a justificar).
Pendente: validar conceito de logotipo; decidir se haverá importação de vendas/PDV.

## Demonstração executável (2026-11-22)
`backend/app/main.py` (FastAPI) + `backend/web/index.html`: expõe validade, PVPS, promoções e reposição.
Sem banco, sem login, sem multi-tenant. Serviços testados (36 testes); a camada FastAPI/HTML NÃO foi
executada na sessão de desenvolvimento (FastAPI indisponível) — validar no seu PC.
Rodar: `cd backend; pip install -r requirements-demo.txt; python -m uvicorn app.main:app --reload` -> http://localhost:8000

## Limitações conhecidas do pacote
- `docker-compose.yml` referencia `frontend/`, `app.main`, Alembic e `app.tasks` inexistentes: não sobe o sistema completo.
- `ci.yml` cobre só ruff + pytest do domínio; `cd-staging.yml`, `cd-production.yml` não existem.
- `requirements.txt` sem versões fixas; ruff não pôde ser executado nesta sessão.
- Docs pendentes: architecture, database, api, security, deployment, user-guide.

## Fases
| Fase | Estado |
|---|---|
| 1 Análise/planejamento | Feita (este arquivo, estrutura abaixo) |
| 2 Infraestrutura | Parcial: docker-compose, nginx, Dockerfile backend, .env.example, Makefile. **Não executados.** Faltam Dockerfile frontend, docker-compose.prod.yml |
| 3 Backend | Só o núcleo de domínio (puro, testado): `app/domain/{expiry,pvps,promotions,insights}.py` — 31 testes passando |
| 4–8 | Pendentes |

## Validado de fato
- `cd backend && python -m pytest -q` → 31 passed (validade, PVPS, promoções, insights).

## Próximos passos
1. Backend: `core/config`, `database`, models SQLAlchemy 2, migration Alembic inicial, `main.py` com `/health`.
2. Auth (Argon2id, JWT + rotação de refresh, bloqueio por tentativas), RBAC, tenant via dependency.
3. CRUDs, estoque transacional (`SELECT ... FOR UPDATE` + `allocate_pvps`), notificações/scheduler com advisory lock.
4. Frontend Vite/React/TS/Tailwind, 17 telas. 5. Testes de integração/E2E. 6. CI/CD e docs.

## Decisões
- Regras de negócio ficam em `app/domain` (funções puras) para serem testáveis sem banco.
- Dinheiro em `Decimal`; validade em `date`.
- Isolamento multi-tenant: `establishment_id` obrigatório em toda query via repositório.
