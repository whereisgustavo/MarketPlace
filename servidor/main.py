"""
AD - Aplicações Distribuídas
Ano Letivo 2025/2026
Projeto - Fase 2

Grupo: 39

Elementos do Grupo:
- Diogo Silva (64143)
- Gustavo Santos (64167)

Descrição:
Ponto de entrada do Servidor.

Inicia o servidor TCP, cria a Loja e o Skeleton, e entra num ciclo
select() que monitoriza simultaneamente:
  - O socket de escuta (para novas ligações)
  - Os sockets de clientes ja ligados (para pedidos)
  - stdin (para o comando exit/quit na consola do servidor)

Desta forma suporta multiplos clientes em simultaneo sem usar threads,
apenas com multiplexação de I/O.

Uso:
    python -m servidor.main <porto>
    ex: python -m servidor.main 5000
"""

import sys
import select
from servidor.loja import Loja
from servidor.skeleton import Skeleton
from servidor.rede import TCPSocketServidor
from shared.excepcoes import ExcepcaoConfiguracaoInvalida
from shared.socket_utilities import PontoAcesso


def main():
    if len(sys.argv) != 2:
        print("SERVIDOR> Uso: python -m servidor.main <porto>")
        sys.exit(1)

    # Valida o porto
    try:
        ponto_acesso = PontoAcesso(endereco_ip='localhost', porto=sys.argv[1])
        print("SERVIDOR> Configuracao do servidor válida.")
    except ExcepcaoConfiguracaoInvalida as e:
        print("SERVIDOR>", e)
        sys.exit(1)

    # Cria a loja (base de dados em memória) e o skeleton (camada RPC)
    loja = Loja()
    skeleton = Skeleton(loja)      # skeleton tem referancia a loja
    servidor = TCPSocketServidor(ponto_acesso)

    print(f"SERVIDOR> À escuta no porto {sys.argv[1]}. Escreva 'exit' ou 'quit' para terminar.")

    # Lista de sockets a monitorizar com select().
    # Começa com o socket servidor + stdin.
    # À medida que chegam clientes, os seus sockets são adicionados.
    sockets_lista = [servidor.obter_socket_servidor(), sys.stdin]

    a_correr = True
    while a_correr:
        # select() bloqueia até haver atividade num dos sockets.
        # Devolve listas de sockets prontos.
        # So usamos a lista de leitura (prontos).
        try:
            prontos, _, _ = select.select(sockets_lista, [], [])
        except KeyboardInterrupt:
            break  

        for s in prontos:

            if s == servidor.obter_socket_servidor():
                # Novo cliente a ligar-se
                conn_sock = servidor.aceitar_cliente()
                # Adiciona o socket do novo cliente à lista
                sockets_lista.append(conn_sock)

            elif s == sys.stdin:
                # Comando introduzido na consola do servidor
                linha = sys.stdin.readline().strip()
                if linha.lower() in ('exit', 'quit'):
                    print("SERVIDOR> A terminar...")
                    a_correr = False
                    break   # sai do for, o while verifica a_correr

            else:
                # Pedido de um cliente ja ligado
                pedido = servidor.receber_pedido(s)

                if pedido is None:
                    # recv devolveu None -> cliente fechou a ligação
                    print("SERVIDOR> Cliente desligou.")
                    sockets_lista.remove(s)   # remove da lista de monitorização
                    servidor.fechar_ligacao(s)
                else:
                    # Processa o pedido no Skeleton e envia a resposta
                    resposta = skeleton.processar_pedido(pedido)
                    servidor.enviar_resposta(s, resposta)

    # Limpeza final
    # Fecha todos os sockets de clientes ainda abertos
    for s in sockets_lista:
        if s not in (servidor.obter_socket_servidor(), sys.stdin):
            servidor.fechar_ligacao(s)
    # Fecha o socket servidor
    servidor.fechar_servidor()


if __name__ == "__main__":
    main()
