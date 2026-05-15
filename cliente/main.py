"""
AD - Aplicações Distribuídas
Ano Letivo 2025/2026
Projeto - Fase 3

Grupo: 39

Elementos do Grupo:
- Diogo Silva (64143)
- Gustavo Santos (64167)

Descrição:
Ponto de entrada do cliente - Fase 3.

O cliente passa a receber o endereço do ZooKeeper em vez do servidor diretamente.
O Processador descobre automaticamente o head e tail da cadeia via ZooKeeper.

Uso:
    python -m cliente.main <zk_host:zk_port> <id_perfil> <id_utilizador>
    ex: python -m cliente.main localhost:2181 3 0
"""

import sys
from cliente.processador import Processador

ZK_ADDR       = 'localhost:2181'
PERFIL        = 0
ID_UTILIZADOR = 0


def main():
    global ZK_ADDR, PERFIL, ID_UTILIZADOR

    if len(sys.argv) != 4:
        print("Uso: python -m cliente.main <zk_host:zk_port> <id_perfil> <id_utilizador>")
        sys.exit(1)

    ZK_ADDR = sys.argv[1]

    try:
        PERFIL        = int(sys.argv[2])
        ID_UTILIZADOR = int(sys.argv[3])
    except ValueError:
        print("id_perfil e id_utilizador devem ser inteiros.")
        sys.exit(1)

    try:
        processador = Processador(ZK_ADDR, PERFIL, ID_UTILIZADOR)
    except Exception as e:
        print(f"Erro ao iniciar cliente: {e}")
        sys.exit(1)

    print(f"CLIENTE> Perfil: {PERFIL} | Utilizador: {ID_UTILIZADOR}")

    while True:
        try:
            msg = input('Mensagem: ')
        except (EOFError, KeyboardInterrupt):
            break

        if msg.strip().upper() == 'EXIT':
            break

        resposta = processador.processa(msg)
        if resposta is not None:
            print('Recebi: %s' % resposta)

    processador.close()


if __name__ == "__main__":
    main()
