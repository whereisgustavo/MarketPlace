"""
AD - Aplicações Distribuídas
Ano Letivo 2025/2026
Projeto - Fase 2

Grupo: 39

Elementos do Grupo:
- Diogo Silva (64143)
- Gustavo Santos (64167)

Descrição:
Ponto de entrada do cliente. Segue o padrão do professor (PL03 - SELECT):
  - Processador criado fora do loop (ligação persistente)
  - processa(msg) no loop
  - close() no fim

Uso:
    python -m cliente.main <porto> <id_perfil> <id_utilizador>
"""

import sys
from cliente.processador import Processador
from shared.excepcoes import ExcepcaoConfiguracaoInvalida

HOST = 'localhost'
PORT = 5000
PERFIL = 0
ID_UTILIZADOR = 0


def main():
    global PORT, PERFIL, ID_UTILIZADOR

    if len(sys.argv) != 4:
        print("Uso: python -m cliente.main <porto> <id_perfil> <id_utilizador>")
        sys.exit(1)

    try:
        PORT = int(sys.argv[1])
        PERFIL = int(sys.argv[2])
        ID_UTILIZADOR = int(sys.argv[3])
    except ValueError:
        print("porto, id_perfil e id_utilizador devem ser inteiros.")
        sys.exit(1)

    try:
        processador = Processador(HOST, PORT, PERFIL, ID_UTILIZADOR)
    except ExcepcaoConfiguracaoInvalida as e:
        print(e)
        sys.exit(1)

    print(f"[INFO] Ligado ao servidor. Perfil: {PERFIL} | Utilizador: {ID_UTILIZADOR}")

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
