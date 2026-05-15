"""
AD - Aplicações Distribuídas
Ano Letivo 2025/2026
Projeto - Fase 3

Grupo: 39

Elementos do Grupo:
- Diogo Silva (64143)
- Gustavo Santos (64167)

Descrição:
Camada de transporte do Cliente - Fase 3.

Novidades em relação à Fase 2:
  - Comunicação protegida por SSL/TLS
  - Suporte para ligação a dois servidores em simultâneo (head e tail)

A classe TCPSocketCliente mantém a mesma interface da Fase 2, com um
parâmetro opcional ssl_context. O processador cria duas instâncias:
uma para o servidor head (escritas) e outra para o servidor tail (leituras).
"""

import socket
import pickle
import struct
from shared.socket_utilities import receive_all


class TCPSocketCliente:

    def __init__(self, ponto_acesso, ssl_context=None):
        self.ponto_acesso  = ponto_acesso
        self.ssl_context   = ssl_context
        self.sock_cliente  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def conectar(self):
        """Estabelece a ligação ao servidor. Se houver contexto SSL, envolve o socket com TLS."""
        self.sock_cliente.connect(
            (self.ponto_acesso.endereco_ip, int(self.ponto_acesso.porto))
        )
        if self.ssl_context: 
            self.sock_cliente = self.ssl_context.wrap_socket(
                self.sock_cliente,
                server_hostname=self.ponto_acesso.endereco_ip
            )
        print(f"CLIENTE> Ligação estabelecida com {self.ponto_acesso.endereco_ip}:{self.ponto_acesso.porto}")

    def enviar_pedido(self, pedido):
        """Serializa o pedido e envia-o ao servidor (pickle + prefixo 4 bytes)."""
        dados   = pickle.dumps(pedido)
        tamanho = struct.pack('!I', len(dados))
        self.sock_cliente.sendall(tamanho + dados)

    def receber_resposta(self):
        """Recebe e desserializa a resposta do servidor."""
        header = receive_all(self.sock_cliente, 4)
        if not header:
            return None
        tamanho = struct.unpack('!I', header)[0]
        dados   = receive_all(self.sock_cliente, tamanho)
        if not dados:
            return None
        return pickle.loads(dados)

    def fechar_ligacao(self):
        """Fecha o socket."""
        try:
            self.sock_cliente.close()
        except Exception:
            pass
