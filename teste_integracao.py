"""
Teste de integração completo da Fase 3.
Corre 3 servidores, executa operações via cliente, testa falha do head
e sincronização de estado com novo servidor.

Uso: python3 teste_integracao.py
"""

import subprocess
import sys
import time
import os

PROJ = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJ)

ZK     = 'localhost:2181'
IP     = '172.22.21.107'
PORTOS = [5000, 6000, 7000, 8000]

VERDE    = '\033[92m'
VERMELHO = '\033[91m'
AZUL     = '\033[94m'
RESET    = '\033[0m'

ok_total = 0
fail_total = 0


def titulo(msg):
    print('\n' + AZUL + '=' * 60)
    print(msg)
    print('=' * 60 + RESET)


def testar(p, cmd, esperado_ok=True):
    global ok_total, fail_total
    resp = p.processa(cmd)
    passou = resp is not None and (resp.startswith('OK') if esperado_ok else resp.startswith('NOK'))
    cor = VERDE if passou else VERMELHO
    sinal = 'PASS' if passou else 'FAIL'
    if passou:
        ok_total += 1
    else:
        fail_total += 1
    print('%s[%s]%s %-50s' % (cor, sinal, RESET, cmd[:50]))
    if resp:
        for linha in resp.split('\n')[:4]:
            print('       ' + linha)
    return resp


def iniciar_servidor(porto, num_cert, esperar=2.0):
    proc = subprocess.Popen(
        [sys.executable, '-m', 'servidor.main',
         ZK, '%s:%d' % (IP, porto), str(num_cert)],
        cwd=PROJ,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    time.sleep(esperar)
    return proc


def znodes():
    from kazoo.client import KazooClient
    zk = KazooClient(ZK)
    zk.start()
    nos = sorted(zk.get_children('/chain'))
    result = []
    for n in nos:
        data, _ = zk.get('/chain/' + n)
        result.append('%s -> %s' % (n, data.decode()))
    zk.stop()
    return result


def limpar_zk():
    from kazoo.client import KazooClient
    zk = KazooClient(ZK)
    zk.start()
    if zk.exists('/chain'):
        for n in zk.get_children('/chain'):
            try:
                zk.delete('/chain/' + n)
            except Exception:
                pass
    zk.stop()


# ------------------------------------------------------------------ #

from cliente.processador import Processador

limpar_zk()
time.sleep(0.5)

titulo('PONTO a) — 1 servidor, operações básicas')

srv1 = iniciar_servidor(PORTOS[0], 1)
print('Servidor 1 iniciado (%s:%d)' % (IP, PORTOS[0]))

# Perfis: 0=anónimo, 1=cliente, 3=admin
p_admin  = Processador(ZK, 3, 0)   # admin  — categorias, produtos, clientes
p_anon   = Processador(ZK, 0, 0)   # anónimo — cria cliente
time.sleep(0.5)

# Admin: criar categorias e produtos
testar(p_admin, 'CRIA_CATEGORIA Fruta')
testar(p_admin, 'CRIA_CATEGORIA Bebidas')
testar(p_admin, 'CRIA_PRODUTO Maca Fruta 1.50 20')
testar(p_admin, 'CRIA_PRODUTO "Agua Mineral" Bebidas 0.95 30')
testar(p_admin, 'LISTA_CATEGORIAS')
testar(p_admin, 'LISTA_PRODUTOS')
testar(p_admin, 'LISTA_CLIENTES')

# Anónimo: criar cliente
testar(p_anon, 'CRIA_CLIENTE "Maria Silva" maria@test.com 1234')

# Cliente: carrinho e encomendas (id_utilizador=1 = Maria Silva)
p_cliente = Processador(ZK, 1, 1)
time.sleep(0.3)
testar(p_cliente, 'ADICIONA_PRODUTO_CARRINHO Maca 3')
testar(p_cliente, 'ADICIONA_PRODUTO_CARRINHO "Agua Mineral" 2')
testar(p_cliente, 'LISTA_CARRINHO')
testar(p_cliente, 'CHECKOUT_CARRINHO')
testar(p_cliente, 'LISTA_ENCOMENDAS 1')

# Erros esperados
testar(p_admin, 'CRIA_CATEGORIA Fruta',            esperado_ok=False)
testar(p_admin, 'CRIA_PRODUTO Maca Fruta 1.50 20', esperado_ok=False)
testar(p_admin, 'LISTA_ENCOMENDAS 99',             esperado_ok=False)

titulo('PONTO b) — 3 servidores, verificar znodes')

srv2 = iniciar_servidor(PORTOS[1], 2)
srv3 = iniciar_servidor(PORTOS[2], 3)
print('Servidores 2 e 3 iniciados')
time.sleep(1.5)

print('Znodes na cadeia:')
for z in znodes():
    print('  ' + z)

testar(p_admin,   'LISTA_PRODUTOS')
testar(p_cliente, 'LISTA_ENCOMENDAS 1')

titulo('PONTO c) — Matar head (servidor 1), cadeia reforma-se')

srv1.terminate()
srv1.wait()
print('Servidor 1 (head) terminado. A aguardar ZooKeeper (15s)...')
time.sleep(15)

print('Znodes após queda do head:')
for z in znodes():
    print('  ' + z)

testar(p_admin,   'LISTA_PRODUTOS')
testar(p_cliente, 'LISTA_ENCOMENDAS 1')
testar(p_admin,   'CRIA_CATEGORIA Legumes')
testar(p_admin,   'LISTA_CATEGORIAS')

titulo('PONTO d) — Novo servidor entra e sincroniza estado')

srv4 = iniciar_servidor(PORTOS[3], 4, esperar=3.0)
print('Servidor 4 iniciado (%s:%d)' % (IP, PORTOS[3]))
time.sleep(1.5)

print('Znodes após entrada do servidor 4:')
for z in znodes():
    print('  ' + z)

testar(p_admin,   'LISTA_CATEGORIAS')
testar(p_cliente, 'LISTA_ENCOMENDAS 1')
testar(p_cliente, 'ADICIONA_PRODUTO_CARRINHO Maca 5')
testar(p_cliente, 'CHECKOUT_CARRINHO')
testar(p_cliente, 'LISTA_ENCOMENDAS 1')

titulo('PONTO e) — Mais operações após reconfiguração')

testar(p_admin,   'CRIA_PRODUTO Laranja Fruta 0.80 50')
testar(p_cliente, 'ADICIONA_PRODUTO_CARRINHO Laranja 4')
testar(p_cliente, 'CHECKOUT_CARRINHO')
testar(p_cliente, 'LISTA_ENCOMENDAS 1')

titulo('PONTO f) — Matar tail, dados preservados')

srv4.terminate()
srv4.wait()
print('Servidor 4 (tail) terminado. A aguardar ZooKeeper (15s)...')
time.sleep(15)

print('Znodes após queda do tail:')
for z in znodes():
    print('  ' + z)

testar(p_cliente, 'LISTA_ENCOMENDAS 1')
testar(p_admin,   'LISTA_PRODUTOS')

# Limpeza
for px in [p_admin, p_anon, p_cliente]:
    px.close()
for s in [srv2, srv3]:
    s.terminate()
    s.wait()

titulo('RESULTADO FINAL')
print('%sPASS: %d%s' % (VERDE, ok_total, RESET))
if fail_total:
    print('%sFAIL: %d%s' % (VERMELHO, fail_total, RESET))
else:
    print('FAIL: 0')
print('')
if fail_total == 0:
    print(VERDE + 'Todos os testes passaram!' + RESET)
else:
    print(VERMELHO + 'Alguns testes falharam.' + RESET)
