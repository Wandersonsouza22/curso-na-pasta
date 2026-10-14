# -*- coding: utf-8 -*-
"""Monta o index.html a partir de src/page.inline.html.

O corpo da página (as nove seções, a barra fixa, o rodapé e o botão do
WhatsApp) mora em src/page.inline.html, que é o arquivo que a gente edita.
Este script só acrescenta o que um arquivo publicado precisa e que o
artefato não tinha: doctype, idioma, título, descrição, canônico, cartão
de compartilhamento, ícone e as fontes servidas do próprio domínio.

Mudou o endereço final? Troque BASE e rode `python3 build.py`. Nenhum
outro arquivo precisa ser tocado: todos os caminhos internos são
relativos, então a página funciona em qualquer subpasta; só as etiquetas
sociais exigem endereço absoluto.
"""
import re

# ---------------------------------------------------------------- endereço
# Sem barra no fim. É o único lugar com o endereço escrito à mão.
BASE = "https://curso.souintencao.com.br"

TITULO = "Curso na Pasta · dê o seu curso de sobrancelhas"
DESC = ("154 páginas prontas para imprimir e dar o seu próprio curso de "
        "sobrancelhas: plano de aula, apostila, exercícios, fichas e "
        "certificados com a sua marca. R$47.")
OG_ALT = ("Curso na Pasta: capas do Guia da Instrutora, da Apostila da Aluna "
          "e dos Modelos de Certificado")
CHECKOUT = "https://pay.kiwify.com.br/7HPiCO2"

# Pixel da Meta do Curso na Pasta, no portfólio BM01, onde o domínio está
# verificado. O ID é público: ele aparece no código-fonte de qualquer página
# que o use. A compra NÃO é medida aqui: ela acontece na Kiwify e sai de lá.
PIXEL = "1760430108515112"
PRECO = "47.00"

FONTES = [
    ("Cormorant Garamond", "cormorant-400.woff2", 400, "normal"),
    ("Cormorant Garamond", "cormorant-400i.woff2", 400, "italic"),
    ("Cormorant Garamond", "cormorant-500.woff2", 500, "normal"),
    ("Inter", "inter-400.woff2", 400, "normal"),
    ("Inter", "inter-500.woff2", 500, "normal"),
    ("Inter", "inter-600.woff2", 600, "normal"),
]


def face(fam, arq, peso, estilo):
    # swap: o texto aparece na fonte do sistema e troca quando a nossa chega.
    # Em block a primeira dobra fica em branco por até três segundos.
    return (f"@font-face{{font-family:'{fam}';src:url('fonts/{arq}') format('woff2');"
            f"font-weight:{peso};font-style:{estilo};font-display:swap;"
            f"unicode-range:U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,"
            f"U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,"
            f"U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD}}")


def main():
    corpo = open("src/page.inline.html", encoding="utf-8").read()

    # As fontes vinham do Google. Agora saem do próprio domínio: uma conexão
    # a menos antes do primeiro texto, e a página não depende de terceiro.
    corpo = re.sub(
        r'<link rel="preconnect"[^>]*>\s*|<link rel="stylesheet" href="https://fonts\.googleapis[^"]*">\s*',
        "", corpo)

    # As quatro imagens do herói aparecem antes de qualquer rolagem: não podem
    # ser lazy, e o navegador precisa das proporções antes de baixá-las.
    heroi = {
        "img/hero-mapa.jpg": (520, 736, ""),
        "img/hero-plano.jpg": (520, 736, ""),
        "img/hero-capa.jpg": (760, 1074, ' fetchpriority="high"'),
        "img/hero-cert.jpg": (640, 452, ""),
    }
    for caminho, (w, h, extra) in heroi.items():
        antes = f'src="{caminho}"'
        assert corpo.count(antes) == 1, caminho
        corpo = corpo.replace(
            antes, f'{antes} width="{w}" height="{h}" decoding="async"{extra}')

    faces = "".join(face(*f) for f in FONTES)

    jsonld = f"""{{
 "@context":"https://schema.org",
 "@type":"Product",
 "name":"Curso na Pasta",
 "description":"Kit de material didático impresso para profissionais de sobrancelhas que vão dar aula: plano de aula, apostila, caderno de exercícios, fichas de atendimento e modelos de certificado, em 154 páginas.",
 "image":"{BASE}/img/og.jpg",
 "url":"{BASE}/",
 "brand":{{"@type":"Brand","name":"Fabrise Academy"}},
 "offers":{{
   "@type":"Offer",
   "price":"47.00",
   "priceCurrency":"BRL",
   "availability":"https://schema.org/InStock",
   "url":"{CHECKOUT}"
 }}
}}"""

    # O pixel é a única coisa de terceiro que a página carrega. Fica no fim do
    # head para não atrasar o primeiro texto, e o fbevents.js é assíncrono.
    pixel = f"""<script>
!function(f,b,e,v,n,t,s){{if(f.fbq)return;n=f.fbq=function(){{n.callMethod?
n.callMethod.apply(n,arguments):n.queue.push(arguments)}};if(!f._fbq)f._fbq=n;
n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;
t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}}
(window,document,'script','https://connect.facebook.net/en_US/fbevents.js');
fbq('init','{PIXEL}');fbq('track','PageView');
</script>
<noscript><img height="1" width="1" style="display:none" alt=""
src="https://www.facebook.com/tr?id={PIXEL}&amp;ev=PageView&amp;noscript=1"></noscript>"""

    # Duas tarefas, uma passada só pelos botões de compra:
    #
    # 1. Repassar os parâmetros do anúncio (utm_*, fbclid) para o checkout. Sem
    #    isso a venda chega na Kiwify sem origem e não dá para saber qual
    #    criativo pagou. Só acrescenta o que o link ainda não tem.
    # 2. Disparar InitiateCheckout no clique. É o evento mais perto da compra
    #    que esta página consegue ver: o que acontece depois é na Kiwify.
    rastreio = f"""<script>
(function(){{
  var ALVO='pay.kiwify.com.br';
  function links(){{return document.querySelectorAll('a[href*="'+ALVO+'"]')}}
  function repassa(){{
    if(location.search.length<2)return;
    var vindos=new URLSearchParams(location.search);
    links().forEach(function(a){{
      var u;try{{u=new URL(a.href)}}catch(e){{return}}
      vindos.forEach(function(v,k){{if(!u.searchParams.has(k))u.searchParams.set(k,v)}});
      a.href=u.toString();
    }});
  }}
  document.addEventListener('click',function(e){{
    var el=e.target;
    if(el&&el.nodeType!==1)el=el.parentElement;
    if(!el||!el.closest||!el.closest('a[href*="'+ALVO+'"]'))return;
    if(window.fbq)fbq('track','InitiateCheckout',
      {{value:{PRECO},currency:'BRL',content_name:'Curso na Pasta'}});
  }},true);
  if(document.readyState==='loading')
    document.addEventListener('DOMContentLoaded',repassa);
  else repassa();
}})();
</script>"""

    cabeca = f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{TITULO}</title>
<meta name="description" content="{DESC}">
<link rel="canonical" href="{BASE}/">
<meta name="theme-color" content="#E9E0D0">
<meta name="robots" content="index,follow,max-image-preview:large">
<meta name="author" content="Fabrise Souza">

<meta property="og:type" content="website">
<meta property="og:locale" content="pt_BR">
<meta property="og:site_name" content="Curso na Pasta">
<meta property="og:title" content="{TITULO}">
<meta property="og:description" content="{DESC}">
<meta property="og:url" content="{BASE}/">
<meta property="og:image" content="{BASE}/img/og.jpg">
<meta property="og:image:secure_url" content="{BASE}/img/og.jpg">
<meta property="og:image:type" content="image/jpeg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{OG_ALT}">

<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{TITULO}">
<meta name="twitter:description" content="{DESC}">
<meta name="twitter:image" content="{BASE}/img/og.jpg">
<meta name="twitter:image:alt" content="{OG_ALT}">

<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="icon" href="favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="apple-touch-icon.png">

<link rel="preload" href="fonts/cormorant-400.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="fonts/inter-400.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="img/hero-capa.jpg" as="image" fetchpriority="high">

<style>{faces}</style>
<script type="application/ld+json">{jsonld}</script>
{pixel}
</head>
<body>
"""

    saida = cabeca + corpo.rstrip() + "\n" + rastreio + "\n</body>\n</html>\n"

    # Travas: nada de travessão no texto visível e nenhuma imagem embutida.
    visivel = re.sub(r"<(style|script)\b.*?</\1>", " ", saida, flags=re.S | re.I)
    visivel = re.sub(r"<!--.*?-->", " ", visivel, flags=re.S)
    visivel = re.sub(r"<[^>]+>", " ", visivel)
    for c in ("—", "–"):
        assert c not in visivel, f"travessao em {visivel[visivel.find(c)-60:visivel.find(c)+60]!r}"
    assert "data:image" not in saida, "sobrou imagem embutida"
    assert "fonts.googleapis" not in saida, "sobrou link do Google Fonts"

    open("index.html", "w", encoding="utf-8").write(saida)
    print(f"index.html  {len(saida)//1024} KB")

    # Buscadores só leem robots.txt na raiz do domínio. Em subpasta este
    # arquivo é inofensivo e inútil; vira útil no dia do domínio próprio.
    open("robots.txt", "w", encoding="utf-8").write(
        "User-agent: *\nAllow: /\n\nSitemap: " + BASE + "/sitemap.xml\n")

    open("sitemap.xml", "w", encoding="utf-8").write(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f'  <url><loc>{BASE}/</loc><changefreq>monthly</changefreq>'
        '<priority>1.0</priority></url>\n</urlset>\n')
    print("robots.txt, sitemap.xml")


if __name__ == "__main__":
    main()
