# Testes

Executar: `cd backend && python -m pytest -q`

Cobertura atual (31 testes, `backend/tests/`):
- `test_domain.py`: classificação de validade (limites inclusive), PVPS (ordem, divisão entre lotes, lotes vencidos/vazios,
  desempate, quantidades inválidas), promoções (faixas, limite no custo, autorização abaixo do custo).
- `test_insights.py`: previsão, reposição, provedor plugável, ranking de desperdício.

Não existem ainda: testes de API, multi-tenant, concorrência de estoque, frontend e E2E (dependem de módulos não implementados).
