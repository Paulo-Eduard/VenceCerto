# VenceCerto — Visão de produto

**Posicionamento:** plataforma SaaS de controle de validade e prevenção de perdas para supermercados.
Proposta de valor mensurável: menos mercadoria vencida, margem protegida, decisões baseadas em dados.

## Princípios de engenharia
1. Arquitetura em camadas (api → services → repositories → models) com regras de negócio puras em `app/domain`.
2. Regras documentadas aqui e em `docs/` e cobertas por testes; a documentação deve refletir o que está implementado.
3. Isolamento multi-tenant obrigatório e testado.
4. Nada simulado: telas e endpoints só entram quando ligados ao banco.
5. Componentes de interface reutilizáveis sobre tokens de design próprios (ver `docs/design-identity.md`).

## Política de IA
- **Núcleo primeiro.** Validade, PVPS, alertas, promoções, perdas, relatórios, auditoria e segurança não dependem de IA.
- **Opcional e desacoplada.** IA entra apenas atrás de interfaces (`DemandForecaster` em `app/domain/insights.py`). Desligada por configuração (`AI_PROVIDER=none`, padrão) ou indisponível → o sistema usa a implementação estatística local, sem erro para o usuário.
- **Só com valor demonstrável.**

| Capacidade | Justificativa | Base atual (sem IA externa) | Evolução com IA/ML (opcional) |
|---|---|---|---|
| Previsão de demanda | Reduz ruptura e excesso | Média móvel ponderada | Modelo sazonal (feriados, dia da semana), exige histórico de vendas |
| Sugestão de reposição | Compra certa evita vencimento | Ponto de pedido + estoque máximo | Ajuste pela previsão ML |
| Padrões de desperdício | Mostra onde a perda se concentra | Agrupamento por categoria/fornecedor/motivo | Detecção de anomalias |
| Análise de comportamento de estoque | Giro e cobertura | Indicadores no dashboard | Clusterização de produtos |

- Sugestões são **explicáveis** (campo `reason`) e **nunca executam ações sozinhas** (nem alteram preços ou criam pedidos).
- Dados enviados a serviços externos: minimizados, sem dados pessoais, ativados por estabelecimento (LGPD).
- **Dependência de dados:** previsão de demanda exige histórico de vendas, que o escopo atual não importa. Registrar saídas (`stock/exit`) já gera esse histórico; integração com PDV/importação de vendas é item de roadmap.

## Identidade e comercialização
- Marca própria, verde/branco/neutros; sem aparência de template genérico.
- Material de apresentação (demo com dados de seed claramente marcados, indicadores de ROI) após o núcleo estar validado.
