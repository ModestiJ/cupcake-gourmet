"""Smoke test E2E contra a produção usando só a stdlib."""
import http.cookiejar
import re
import sys
import time
import urllib.parse
import urllib.request

BASE = sys.argv[1].rstrip("/")
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
op.addheaders = [("User-Agent", "smoke-test")]
ok = True


def req(path, data=None, referer=None):
    url = BASE + path
    body = urllib.parse.urlencode(data).encode() if data is not None else None
    r = urllib.request.Request(url, data=body)
    if referer or data is not None:
        r.add_header("Referer", referer or url)
    t = time.time()
    resp = op.open(r, timeout=90)
    return resp, resp.read().decode("utf-8", "replace"), time.time() - t


def csrf(html):
    return re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', html).group(1)


def check(nome, cond, extra=""):
    global ok
    ok &= bool(cond)
    print(("PASS " if cond else "FAIL ") + nome + (f"  [{extra}]" if extra else ""))


# 1. páginas públicas + tempo
for p in ["/", "/sobre/", "/entregas/", "/conta/entrar/", "/manifest.webmanifest", "/sw.js", "/static/css/app.css"]:
    resp, html, dt = req(p)
    check(f"GET {p} -> {resp.status}", resp.status == 200, f"{dt:.2f}s")

resp, html, _ = req("/")
check("vitrine lista cupcakes", "Pistache Siciliano" in html and "Destaques do dia" in html)
check("header HSTS", "max-age" in (resp.headers.get("Strict-Transport-Security") or ""))
check("header X-Frame-Options", resp.headers.get("X-Frame-Options") == "DENY")
_, html, _ = req("/?q=pistache")
check("busca pistache", "Pistache Siciliano" in html and "Morango com Chantilly" not in html)

# 2. http -> https
try:
    r = urllib.request.urlopen(urllib.request.Request(BASE.replace("https://", "http://") + "/"), timeout=60)
    check("http redireciona para https", r.geturl().startswith("https://"))
except Exception as e:  # noqa
    check("http redireciona para https", False, str(e))

# 3. 404 amigável
try:
    req("/nao-existe/")
    check("404", False)
except urllib.error.HTTPError as e:
    check("404 amigável", e.code == 404 and "saiu do forno" in e.read().decode())

# 4. login cliente demo
_, html, _ = req("/conta/entrar/")
_, html, _ = req("/conta/entrar/", {"csrfmiddlewaretoken": csrf(html), "username": "cliente@cupcake.dev", "password": "Cliente@123"})
check("login cliente demo", "Olá, Cliente" in html)

# 5. painel bloqueado para cliente
try:
    req("/painel/")
    check("painel 403 para cliente", False)
except urllib.error.HTTPError as e:
    check("painel 403 para cliente", e.code == 403)

# 6. carrinho + checkout retirada pagando na entrega
_, html, _ = req("/cupcake/1/")
estoque_antes = int(re.search(r"(\d+) disponível", html).group(1))
_, html, _ = req("/carrinho/adicionar/1/", {"csrfmiddlewaretoken": csrf(html), "quantidade": "2"})
check("adicionou ao carrinho", "adicionado ao carrinho" in html)
_, html, _ = req("/checkout/")
check("checkout mostra taxa do bairro", "Taxa: R$ 8,00" in html, "Vila Mariana")
resp, html, _ = req("/checkout/", {"csrfmiddlewaretoken": csrf(html), "tipo_entrega": "ENTREGA",
                                     "endereco": re.search(r'name="endereco" value="(\d+)"', html).group(1),
                                     "metodo_pagamento": "PIX", "observacao": "smoke test – pode cancelar"})
check("pedido criado e foi para pagamento Pix", "Pix copia e cola" in html, resp.geturl())
pk = re.search(r"/pedidos/(\d+)/pagamento", resp.geturl()).group(1)
_, html, _ = req(f"/pedidos/{pk}/pagamento/", {"csrfmiddlewaretoken": csrf(html), "simular": "recusa"})
check("pagamento recusado simulado", "recusado pela operadora" in html)
_, html, _ = req(f"/pedidos/{pk}/pagamento/", {"csrfmiddlewaretoken": csrf(html)})
check("pagamento aprovado", "Pagamento aprovado" in html and "Aprovado" in html)
check("linha do tempo", "Recebido" in html and "Em preparo" in html)

# 7. cancelar (devolve estoque)
_, html, _ = req(f"/pedidos/{pk}/cancelar/", {"csrfmiddlewaretoken": csrf(html)})
check("pedido cancelado", "cancelado" in html.lower() and "Estornado" in html)
_, html, _ = req("/cupcake/1/")
check("estoque devolvido", int(re.search(r"(\d+) disponível", html).group(1)) == estoque_antes)

print("\nRESULTADO:", "TUDO OK" if ok else "HÁ FALHAS")
