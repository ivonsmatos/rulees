---
name: rulees-frontend
description: >
  Design system e convenções de frontend do Rulees. Use ao construir/alterar telas,
  componentes, layout, UX, estado, formulários, acessibilidade ou identidade visual —
  tanto no app PWA (React + Vite em frontend/) quanto no site de marketing (Next.js em
  "rulees site/saasox-nextjs"). Define tokens de marca, tipografia, padrões de componente,
  estados e regras de acessibilidade.
---

# Rulees — Frontend & Design System

O Rulees tem **dois frontends**, com a mesma identidade:

| Frontend | Onde | Stack | Para quê |
|---|---|---|---|
| **App (produto)** | `frontend/` | React 19 + Vite + TS + TanStack Query + Zustand + Zod + React Hook Form | A plataforma autenticada (reunião, Rules Ledger, documentos) |
| **Site (marketing)** | `rulees site/saasox-nextjs/` | Next.js 15 + React 19 + Bootstrap 5 (template SaasoX) | Landing, planos, blog, conversão/SEO |

## Identidade de marca (tokens)

Cores oficiais (fonte: `frontend/public` + `App.css`). Use **sempre** estas variáveis,
nunca hex solto:

```css
--brand-deep:   #375d61; /* teal escuro — fundo de destaque, header/footer */
--brand-mid:    #61a4ab; /* teal médio — apoio */
--brand-bright: #80d7e0; /* ciano — acento/realce */
--brand-soft:   #c8e3e6; /* ciano claro — superfícies/bordas */
--brand-muted:  #546061; /* cinza-azulado — texto secundário */
--surface:      #ffffff;
--ink:          #0b1f22; /* texto principal (preferir a #000 puro) */
```

- **theme-color** (PWA / meta): `#375D61`.
- **Logos:** `public/assets/img/rulees-logo.svg` (colorida, fundo claro),
  `rulees-logo-white.svg` (fundo escuro), `rulees-icon.svg` (favicon/quadrada).
- Não distorça a logo: proporção **3:1** (horizontal). Ícone é **1:1**.

## Tipografia

- **Títulos:** Sora (600–800). **Corpo:** DM Sans (400–500). (Site de marketing já carrega
  ambas via `next/font`.) No app, manter a stack do projeto.
- Hierarquia: **um único `<h1>` por página**, depois `<h2>`/`<h3>` em ordem lógica
  (vale para SEO e acessibilidade — ver skill de SEO/GEO).

## Estado no app (frontend/)

| Tipo de estado | Ferramenta |
|---|---|
| Servidor (dados da API) | **TanStack Query** (cache, refetch, loading/erro) |
| Sessão/UI local | **Zustand** |
| Tempo real (reunião) | WebSocket nativo → ver skill `rulees-realtime-events` |
| Offline/local | IndexedDB / Workbox (PWA) |
| Formulários | **React Hook Form + Zod** (validação no schema) |

Regra: **nunca** guardar token/credencial em estado global exposto; sessão fica em
`localStorage` sob `rulees.session` e vai no header `Authorization` + `X-Tenant-Id`.

## Convenções de componente

- Um componente por arquivo; nome em PascalCase; co-localizar por feature
  (`features/<dominio>/`).
- Texto de produto em **pt-BR**; nomes de código/identificadores em inglês.
- Toda imagem tem `alt` descritivo (não "img"). Ícones decorativos: `alt=""`.
- Estados vazios, de carregamento e de erro são **obrigatórios** em qualquer lista/painel.
- Botões e ações refletem permissão: esconder/desabilitar o que o papel não pode
  (viewer é read-only). A verdade é sempre revalidada no backend.

## Acessibilidade (mínimo inegociável)

- Contraste AA (teal escuro sobre claro já passa; cuidado com ciano sobre branco em texto).
- Navegação por teclado e `:focus-visible` visível.
- `aria-label` em ícones-botão; `lang="pt-BR"` no html.
- Alvos de toque ≥ 40px; nada de informação só por cor.

## Imagens

- Banco de imagens: **Unsplash/Pexels**. Verificar status 200 antes de usar; baixar para
  `public/assets/img/rulees/` (não hotlink em produção) com tamanho/densidade adequados.
- `next/image` com `width`/`height` corretos (evita layout shift / bom CLS).

## Ao entregar uma tela, cheque

1. [ ] `<h1>` único + hierarquia de headings correta.
2. [ ] Estados de loading/erro/vazio presentes.
3. [ ] Permissões refletidas na UI (viewer não vê ações de mutação).
4. [ ] `alt` em todas as imagens; foco e teclado ok.
5. [ ] Tokens de marca (sem hex solto), responsivo (mobile-first).
6. [ ] Texto pt-BR, humanizado e específico (nada de lorem ipsum).
