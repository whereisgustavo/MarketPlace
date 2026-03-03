from sys import argv
import sys
from  shared.socket_utilities import PontoAcesso
from shared.excepcoes import ExcepcaoConfiguracaoInvalida
from cliente.rede import TCPSocketCliente

def main():
    if len(argv) != 2:
        print("CLIENTE> Uso: python -m cliente.main <porto>")
        sys.exit(1)

    try: 
        # valida endereco_ip e porto (se erro ExcepcaoIPInvalido ou ExcepcaoPortoInvalido)
        ponto_acesso = PontoAcesso(endereco_ip = 'localhost', porto = argv[1])
        print("CLIENTE> Configuracao do servidor válida. ")
        print("CLIENTE> Iniciando aplicação do lado do cliente. ")
    except ExcepcaoConfiguracaoInvalida  as e: 
        print("CLIENTE>", e)
        sys.exit(1) 

    # TODO: chama funcoes no cliente para contactar o servidor e enviar mensagens
    cliente = TCPSocketCliente(ponto_acesso)
    cliente.conectar()
    while True:
        comando = input("CLIENTE> ") # 1. Lê o que o utilizador quer
        
        if comando.upper() == "EXIT":
            break
            
        cliente.enviar_mensagem(comando)      # 2. Envia (Função A)
        resposta = cliente.receber_mensagem() # 3. Recebe (Função B)
        
        print(resposta) # 4. Mostra o resultado (OK; ou NOK;)

    cliente.fechar_ligacao()


if __name__ == "__main__":
    main()