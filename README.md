# Curso na Pasta · página de vendas

Página única, estática, sem dependência de servidor. Qualquer hospedagem que
sirva arquivos funciona: GitHub Pages, Netlify, Vercel, Cloudflare Pages ou a
pasta `public_html` de uma hospedagem comum.

## O que é cada coisa

| Caminho | O que é |
|---|---|
| `index.html` | A página publicada. **Gerado.** Não edite à mão. |
| `src/page.inline.html` | O corpo da página: as nove seções, a barra fixa, o rodapé e o botão do WhatsApp. **É aqui que se edita.** |
| `build.py` | Monta o `index.html` a partir do `src`, acrescentando cabeçalho, etiquetas sociais e fontes. Gera também `robots.txt` e `sitemap.xml`. |
| `img/` | As quinze imagens da página mais o cartão de compartilhamento (`og.jpg`). |
| `fonts/` | Cormorant Garamond e Inter servidas do próprio domínio. |
| `favicon.svg`, `favicon-32.png`, `apple-touch-icon.png` | Ícone da aba e do atalho no celular. |
| `build/` | Ferramentas de conferência e o fonte do cartão. Não vai para o ar. |

## Como editar e republicar

1. Edite `src/page.inline.html`.
2. Rode `python3 build.py`.
3. Confira: `python3 -m http.server 8777` e abra `http://127.0.0.1:8777`.
4. Comite e empurre. A hospedagem publica sozinha.

O `build.py` falha de propósito se sobrar travessão no texto visível, se
alguma imagem voltar a ser embutida em base64 ou se as fontes voltarem a vir
do Google.

## Trocar o endereço

O endereço aparece escrito uma vez só, na constante `BASE` no topo do
`build.py`. Troque, rode `python3 build.py` e pronto: canônico, `og:url`,
`og:image`, dados estruturados, `robots.txt` e `sitemap.xml` se ajustam juntos.

Todos os caminhos internos são relativos, então a página funciona em qualquer
subpasta sem alteração. Só as etiquetas sociais exigem endereço absoluto, e
são elas que o `BASE` alimenta.

## Depois de publicar

- Passe o endereço no depurador de compartilhamento do Facebook e no do
  LinkedIn para forçar a leitura do cartão novo.
- Troque o link de "página de vendas" no produto da Kiwify, que hoje aponta
  para o perfil do Instagram.
- Cadastre o endereço no Google Search Console.

## Pesos

Documento 55 KB. Primeira tela: documento, duas fontes e quatro imagens, cerca
de 215 KB. As outras onze imagens só baixam quando entram na tela.
