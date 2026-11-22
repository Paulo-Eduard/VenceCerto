# Identidade visual do VenceCerto (rascunho para validação)

Conceito: **"o check de validade"** — marca baseada em um selo de verificação sobre calendário/etiqueta de preço,
refletindo controle e precisão. Sensação: calma, confiável, operacional.

## Tokens (Tailwind `theme.extend`)
- `brand-700 #1F6B3A` (primária), `brand-500 #2E9B57`, `brand-50 #EEF8F1`.
- Semânticos de validade (nunca só cor: sempre ícone + rótulo): ok = verde, próximo = âmbar `#C98A12`, urgente = laranja `#D2541B`, vencido = vermelho `#B3261E`, esgotado = cinza `#6B7280`.
- Neutros: fundo `#F6F7F5`, superfície `#FFFFFF`, borda `#E3E6E1`, texto `#1B1F1C`.
- Tipografia: fonte de interface legível em tabelas densas; números tabulares em quantidades e valores.
- Raio 8px, sombras discretas, densidade pensada para uso diário em balcão/estoque.

## Componentes base (reutilizáveis)
`StatusBadge` (estados de lote), `DataTable` (paginação, ordenação, estado vazio), `FilterBar`, `KpiCard`,
`ConfirmDialog` (ações destrutivas), `FormField` (RHF + Zod), `PageHeader`, `Toast`.

Pendente: validar o conceito de logotipo com o responsável pelo produto antes de implementar.
