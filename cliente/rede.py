"""
AD - Aplicações Distribuídas
Ano Letivo 2025/2026
Projeto - Fase 2

Grupo: 39

Elementos do Grupo:
- Diogo Silva (64143)
- Gustavo Santos (64167)

Descrição:
Camada de transporte do Cliente

Responsabilidades:
  - Criar o socket TCP e ligar ao servidor
  - Enviar pedidos serializados (pickle + prefixo 4 bytes)
  - Receber respostas serializadas (pickle + prefixo 4 bytes)
  - Fechar a ligação

A ligação é persistente: é estabelecida uma vez no arranque e mantida
durante toda a sessão.

Não interpreta respostas, apenas move bytes.
"""

import socket
import pickle
import struct
from shared.socket_utilities import receive_all, PontoAcesso


class TCPSocketCliente:

    def __init__(self, ponto_acesso):
        self.ponto_acesso = ponto_acesso

        # Cria o socket TCP (IPv4, stream)
        self.sock_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def conectar(self):
        """Estabelece a ligação ao servidor. Chamada uma vez no arranque."""
        self.sock_cliente.connect((self.ponto_acesso.endereco_ip, int(self.ponto_acesso.porto)))
        print("CLIENTE> Ligação estabelecida com o servidor.")

    def enviar_pedido(self, pedido):
        """Serializa o pedido e envia-o ao servidor.

        Protocolo:
          1. pickle.dumps(pedido) -> converte a lista para bytes
          2. struct.pack('!I', tamanho) -> 4 bytes big-endian com o tamanho
          3. sendall(4_bytes + payload) -> envia tudo de uma vez"""

        # Serializa a lista pedido para bytes
        dados = pickle.dumps(pedido)

        # Calcula o tamanho e empacota em 4 bytes
        tamanho = struct.pack('!I', len(dados))

        # Envia: cabeçalho de 4 bytes + payload
        self.sock_cliente.sendall(tamanho + dados)

    def receber_resposta(self):
        """Recebe e desserializa a resposta do servidor.

        Protocolo (inverso do enviar):
          1. receive_all(4) -> le 4 bytes de cabeçalho
          2. unpack -> obtem o tamanho do payload
          3. receive_all(tamanho) -> le o payload completo
          4. pickle.loads -> converte bytes -> lista

        Devolve a lista [op_code_resposta, dados], ou None se a
        ligação foi fechada pelo servidor."""

        # Passo 1: le os 4 bytes do cabeçalho
        header = receive_all(self.sock_cliente, 4)
        if not header:
            return None   # liagação fecha

        # Passo 2: extrai o tamanho do payload
        tamanho = struct.unpack('!I', header)[0]

        # Passo 3: lê x tamanho bytes (pode ser fragmentado)
        dados = receive_all(self.sock_cliente, tamanho)
        if not dados:
            return None

        # Passo 4: desserializa e devolve o objecto Python
        return pickle.loads(dados)

    def fechar_ligacao(self):
        """Fecha o socket. Chamada quando o cliente termina."""
        self.sock_cliente.close()
