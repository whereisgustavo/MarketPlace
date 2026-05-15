"""
AD - Aplicações Distribuídas
Ano Letivo 2025/2026
Projeto - Fase 3

Grupo: 39

Elementos do Grupo:
- Diogo Silva (64143)
- Gustavo Santos (64167)

Descrição:
Ponto de entrada do Servidor - Fase 3.

Novidades em relação à Fase 2:
  - Registo no ZooKeeper como nó efémero e sequencial em /chain
  - Sincronização de estado com o antecessor na cadeia ao arrancar
  - Ligação ao sucessor para propagação de escritas
  - Watch no ZooKeeper para detetar mudanças na cadeia
  - Comunicação cliente-servidor protegida por SSL/TLS
  - Propagação síncrona de operações de escrita pelo successor

Uso:
    python -m servidor.main <zk_host:zk_port> <ip_proprio:porto_proprio> <num_certificado>
    ex: python -m servidor.main 192.168.1.10:2181 192.168.1.10:5000 1
"""

import sys
import select
import socket
import pickle
import struct
import threading

from kazoo.client import KazooClient

from servidor.loja import Loja
from servidor.skeleton import Skeleton
from servidor.rede import TCPSocketServidor
from shared.socket_utilities import PontoAcesso, receive_all
from shared.excepcoes_shared import OpCodes
from shared.ssl_utils import criar_contexto_servidor
from shared.zookeeper_utils import (
    CHAIN_PATH, ordenar_nos,
    obter_sucessor, obter_antecessor, parse_endereco
)

# Op_codes internos para transferência de estado entre servidores
OP_GET_ESTADO  = 19999
OK_GET_ESTADO  = 29999

# Operações de escrita: executadas localmente e propagadas ao sucessor
OPS_ESCRITA = {
    OpCodes.CRIA_CATEGORIA,
    OpCodes.REMOVE_CATEGORIA,
    OpCodes.CRIA_PRODUTO,
    OpCodes.AUMENTA_STOCK,
    OpCodes.ATUALIZA_PRECO,
    OpCodes.CRIA_CLIENTE,
    OpCodes.ADICIONA_PRODUTO_CARRINHO,
    OpCodes.REMOVE_PRODUTO_CARRINHO,
    OpCodes.CHECKOUT_CARRINHO,
}



def enviar_receber_tcp(host, porto, pedido):
    """Envia um pedido SSL ao antecessor e aguarda resposta.
    Usado para transferência de estado entre servidores."""
    from shared.ssl_utils import criar_contexto_cliente
    ctx = criar_contexto_cliente()
    raw = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    raw.connect((host, int(porto)))
    s = ctx.wrap_socket(raw, server_hostname=host)
    dados = pickle.dumps(pedido)
    s.sendall(struct.pack('!I', len(dados)) + dados)
    header = receive_all(s, 4)
    tamanho = struct.unpack('!I', header)[0]
    resposta = pickle.loads(receive_all(s, tamanho))
    s.close()
    return resposta


def propagar_ao_sucessor(pedido, sock_sucessor):
    """Envia o pedido ao sucessor e aguarda a confirmação (atomicidade da escrita)."""
    dados = pickle.dumps(pedido)
    sock_sucessor.sendall(struct.pack('!I', len(dados)) + dados)
    header = receive_all(sock_sucessor, 4)
    if header:
        tamanho = struct.unpack('!I', header)[0]
        receive_all(sock_sucessor, tamanho)  # confirma receção, descarta resposta


def ligar_ao_sucessor(host, porto):
    """Cria socket SSL persistente para comunicação com o sucessor."""
    from shared.ssl_utils import criar_contexto_cliente
    ctx = criar_contexto_cliente()
    raw = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    raw.connect((host, int(porto)))
    return ctx.wrap_socket(raw, server_hostname=host)


def main():
    if len(sys.argv) != 4:
        print("Uso: python -m servidor.main <zk_host:zk_port> <ip_proprio:porto_proprio> <num_certificado>")
        sys.exit(1)

    zk_addr          = sys.argv[1]
    endereco_proprio = sys.argv[2]
    num_cert         = int(sys.argv[3])
    meu_ip, porto    = endereco_proprio.split(':')

    loja = Loja()

    # Criar o servidor TCP com SSL ANTES de registar no ZooKeeper.
    # Isto é essencial: quando o antecessor recebe a notificação do ZooKeeper de que
    # este nó entrou na cadeia, tenta ligar-se imediatamente a esta porta para estabelecer
    # o canal de propagação. Se o socket ainda não existir, a ligação falha e a propagação
    # fica quebrada. Ao abrir o porto primeiro garantimos que o antecessor consegue ligar-se
    # enquanto este nó está ainda a sincronizar o estado.
    ssl_ctx = criar_contexto_servidor(num_cert)
    servidor = TCPSocketServidor(PontoAcesso(meu_ip, porto), ssl_context=ssl_ctx)
    print(f"SERVIDOR> À escuta no porto {porto} (SSL). Escreva 'exit' para terminar.")

    # Ligar ao ZooKeeper
    zk = KazooClient(hosts=zk_addr)
    zk.start()
    zk.ensure_path(CHAIN_PATH)
    print(f"SERVIDOR> Ligado ao ZooKeeper em {zk_addr}")

    # Registar-me como nó efémero e sequencial na cadeia
    meu_endereco  = f'{meu_ip}:{porto}'.encode()
    meu_no_path   = zk.create(f'{CHAIN_PATH}/node-', value=meu_endereco,
                               ephemeral=True, sequence=True)
    meu_no_nome   = meu_no_path.split('/')[-1]
    print(f"SERVIDOR> Registado como {meu_no_nome} ({meu_ip}:{porto})")

    # Obter a cadeia atual e determinar antecessor e sucessor
    nos = ordenar_nos(zk.get_children(CHAIN_PATH))

    # Se existe antecessor, obter uma cópia do estado da loja
    antecessor_nome = obter_antecessor(nos, meu_no_nome)
    if antecessor_nome:
        dados_ant, _ = zk.get(f'{CHAIN_PATH}/{antecessor_nome}')
        ant_ip, ant_porto = parse_endereco(dados_ant)
        print(f"SERVIDOR> A sincronizar estado com {antecessor_nome} ({ant_ip}:{ant_porto})...")
        resp = enviar_receber_tcp(ant_ip, ant_porto, [OP_GET_ESTADO, [], 3, 0])
        if resp and resp[0] == OK_GET_ESTADO:
            loja.importar_estado(resp[1][0])
            print("SERVIDOR> Estado importado com sucesso.")

    # Estrutura partilhada entre a thread principal e os callbacks do ZooKeeper
    # O lock protege o acesso concorrente ao socket do sucessor
    lock = threading.Lock()
    successor_info = {'socket': None, 'nome': None}

    # Configurar ligação ao sucessor inicial (se existir)
    sucessor_nome = obter_sucessor(nos, meu_no_nome)
    if sucessor_nome:
        dados_suc, _ = zk.get(f'{CHAIN_PATH}/{sucessor_nome}')
        suc_ip, suc_porto = parse_endereco(dados_suc)
        successor_info['socket'] = ligar_ao_sucessor(suc_ip, suc_porto)
        successor_info['nome']   = sucessor_nome
        print(f"SERVIDOR> Sucessor: {sucessor_nome} ({suc_ip}:{suc_porto})")
    else:
        print("SERVIDOR> Sou a cauda da cadeia (sem sucessor).")

    skeleton = Skeleton(loja)

    # Watch na cadeia: chamado sempre que um nó é adicionado ou removido
    @zk.ChildrenWatch(CHAIN_PATH)
    def watch_chain(children):
        nos_atuais      = ordenar_nos(children)
        novo_suc_nome   = obter_sucessor(nos_atuais, meu_no_nome)
        with lock:
            if novo_suc_nome == successor_info['nome']:
                return  # sem alteração ao sucessor
            # Fecha ligação ao sucessor anterior
            if successor_info['socket']:
                try:
                    successor_info['socket'].close()
                except Exception:
                    pass
            # Liga ao novo sucessor (se existir)
            if novo_suc_nome:
                dados_suc, _ = zk.get(f'{CHAIN_PATH}/{novo_suc_nome}')
                suc_ip, suc_porto = parse_endereco(dados_suc)
                successor_info['socket'] = ligar_ao_sucessor(suc_ip, suc_porto)
                print(f"SERVIDOR> Novo sucessor: {novo_suc_nome} ({suc_ip}:{suc_porto})")
            else:
                successor_info['socket'] = None
                print("SERVIDOR> Passei a ser a cauda da cadeia.")
            successor_info['nome'] = novo_suc_nome

    sockets_lista = [servidor.obter_socket_servidor(), sys.stdin]
    a_correr = True

    while a_correr:
        try:
            prontos, _, _ = select.select(sockets_lista, [], [])
        except KeyboardInterrupt:
            break

        for s in prontos:

            if s == servidor.obter_socket_servidor():
                conn_sock = servidor.aceitar_cliente()
                sockets_lista.append(conn_sock)

            elif s == sys.stdin:
                linha = sys.stdin.readline().strip()
                if linha.lower() in ('exit', 'quit'):
                    a_correr = False
                    break

            else:
                pedido = servidor.receber_pedido(s)

                if pedido is None:
                    print("SERVIDOR> Cliente desligou.")
                    sockets_lista.remove(s)
                    servidor.fechar_ligacao(s)
                    continue

                # Pedido interno de transferência de estado (de um novo servidor da cadeia)
                if isinstance(pedido, list) and pedido and pedido[0] == OP_GET_ESTADO:
                    estado = loja.exportar_estado()
                    servidor.enviar_resposta(s, [OK_GET_ESTADO, [estado]])
                    continue

                # Processamento normal do pedido no skeleton
                resposta = skeleton.processar_pedido(pedido)

                # Propagação síncrona ao sucessor para operações de escrita
                if isinstance(pedido, list) and pedido and pedido[0] in OPS_ESCRITA:
                    with lock:
                        suc_sock = successor_info['socket']
                    if suc_sock:
                        try:
                            propagar_ao_sucessor(pedido, suc_sock)
                        except Exception as e:
                            print(f"SERVIDOR> Erro ao propagar para sucessor: {e}")

                servidor.enviar_resposta(s, resposta)

    # Limpeza final
    for s in sockets_lista:
        if s not in (servidor.obter_socket_servidor(), sys.stdin):
            servidor.fechar_ligacao(s)
    servidor.fechar_servidor()
    zk.stop()
    print("SERVIDOR> Terminado.")


if __name__ == "__main__":
    main()
