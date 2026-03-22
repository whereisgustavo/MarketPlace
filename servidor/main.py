"""
AD - Aplicações Distribuídas
Ano Letivo 2025/2026
Projeto - Fase 2

Grupo: 39

Elementos do Grupo:
- Diogo Silva (64143)
- Gustavo Santos (64167)

Descrição:
Ficheiro principal do servidor. Responsável por iniciar o servidor TCP,
aceitar ligações de clientes e encaminhar os comandos recebidos para o
processador de comandos.
"""


import sys
from servidor.processador import Processador
from servidor.rede import TCPSocketServidor
from shared.excepcoes import ExcepcaoConfiguracaoInvalida
from shared.socket_utilities import PontoAcesso

def main():

    if len(sys.argv) != 2:
        print("SERVIDOR> Uso: python -m servidor.main <porto>")
        sys.exit(1)

    processador = Processador()
    try:
        ponto_acesso = PontoAcesso(endereco_ip='localhost', porto = sys.argv[1])  
        print("SERVIDOR> Configuracao do servidor válida. ")

    except ExcepcaoConfiguracaoInvalida as e:
        print("SERVIDOR>", e)
        sys.exit(1)

    servidor = TCPSocketServidor(ponto_acesso)
    #TODO: chamar funcoes de rede do servidor ...
    #TODO: apagar e substituir código abaixo por código de sockets
    
    while True: 
        print("SERVIDOR> Servidor pronto para receber comandos simulado. ")
        """
        comando = servidor.simula_cliente()
        resposta = processador.processar_comando(comando)
        print(resposta)
        if comando == 'EXIT': 
            break
        """
        # GS 03/03
        servidor.aceitar_ligacao()
        while True:
            comando = servidor.receber_comando()
            if not comando or comando == 'EXIT':
                break
            resposta = processador.processar_comando(comando)
            servidor.enviar_resposta(resposta)

if __name__ == "__main__":
    main()