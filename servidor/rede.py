"""
AD - Aplicações Distribuídas
Ano Letivo 2025/2026
Projeto - Fase 2

Grupo: 39

Elementos do Grupo:
- Diogo Silva (64143)
- Gustavo Santos (64167)

Descrição:
Implementa a camada de comunicação do servidor utilizando sockets TCP.
Responsável por aceitar ligações de clientes, receber comandos e enviar
respostas processadas pelo servidor.
"""


import socket
from shared.socket_utilities import PontoAcesso
from servidor.processador import Processador


class TCPSocketServidor:
    """
    Camada Transporte:
    - não interpreta comandos
    - não chama Loja
    - não faz validações de negócio
    - só move strings
    """

    def __init__(self, ponto_acesso):
        self.ponto_acesso = ponto_acesso
        # Criação do Socket - GS 03/03
        self.sock_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Permite reutilizar o endereço - GS 03/03
        self.sock_servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        #A Agarrar o endereço e o porto pretendido (que vêm do sys.argv) - GS 03/03
        self.sock_servidor.bind((self.ponto_acesso.endereco_ip, int(self.ponto_acesso.porto)))
        # Após agarrar o endereço, faz listen (com backlog de 1) - GS 03/03
        self.sock_servidor.listen(1)

        # Definimos uma variavel para guardar a ligação ativa com o cliente - GS 03/03
        self.conn_sock = None


    # TODO: A eliminar (código auxiliar)
    def simula_cliente(self):
        return input("SERVIDOR> Escreva mensagem>")

    # TODO: A completar
    def aceitar_ligacao(self):
        # Aceitamos a ligação - GS 03/03
        (self.conn_sock, (addr, port)) = self.sock_servidor.accept()
        print(f"Ligação efetuada a {addr}:{port}")
    
    def receber_comando(self):
        # Se houver uma ligação ativa, recebe os bytes e decodifica a mensagem -  GS 03/03
        if self.conn_sock:
            mensagem_bytes = self.conn_sock.recv(1024)
            if not mensagem_bytes:
                return None
            return mensagem_bytes.decode('utf-8').strip()
        return None
    
    def enviar_resposta(self, resposta):
        # Envia a resposta de volta para o cliente - GS 03/03
        if self.conn_sock:
            self.conn_sock.sendall(resposta.encode('utf-8'))
    
    def fechar_ligacao(self):
        # Fecha a ligação com o cliente atual -  GS 03/03
        if self.conn_sock:
            self.conn_sock.close()
            self.conn_sock = None