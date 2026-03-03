import socket
from shared.socket_utilities import PontoAcesso


class TCPSocketCliente:
    """
    Camada Transporte:
    - move strings 
    - não conhece regras de negócio
    - não interpreta comandos
    """

    def __init__(self, ponto_acesso):
        self.ponto_acesso = ponto_acesso

        # Criação do socket cliente - GS 03/03
        self.sock_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


    # TODO: A completar
    def conectar(self):
        self.sock_cliente.connect((self.ponto_acesso.endereco_ip, int(self.ponto_acesso.porto)))
        print("Cliente conectado com sucesso")
    def enviar_mensagem(self, mensagem):
        # Envio de mensagem para o servidor - GS 03/03
        self.sock_cliente.sendall(mensagem.encode())
    def receber_mensagem(self):
        # Receção de mensagem enviada pelo servidor -GS 03/03
        self.resposta = self.sock_cliente.recv(1024)
        return self.resposta.decode('utf-8').strip()
    def fechar_ligacao(self):
        # Fechar ligação do cliente com o servidor - GS 03/03
        self.sock_cliente.close()