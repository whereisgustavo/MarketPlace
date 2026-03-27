"""
AD - Aplicações Distribuídas
Ano Letivo 2025/2026
Projeto - Fase 2

Grupo: 39

Elementos do Grupo:
- Diogo Silva (64143)
- Gustavo Santos (64167)

Descrição:
Camada de transporte do Servidor.

Responsabilidades:
  - Criar e configurar o socket de escuta
  - Aceitar novas ligações de clientes
  - Receber pedidos serializados (pickle + prefixo 4 bytes)
  - Enviar respostas serializadas (pickle + prefixo 4 bytes)
  - Fechar ligações individuais e o socket servidor

Não interpreta comandos nem chama a Loja, apenas move bytes.
"""

import socket
import pickle
import struct
from shared.socket_utilities import receive_all


class TCPSocketServidor:

    def __init__(self, ponto_acesso):
        self.ponto_acesso = ponto_acesso

        # Cria o socket TCP (AF_INET = IPv4, SOCK_STREAM = TCP)
        self.sock_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # SO_REUSEADDR permite reutilizar o porto imediatamente apos reiniciar
        # o servidor (evita o erro "Address already in use")
        self.sock_servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Associa o socket ao endereço e porto configurados
        self.sock_servidor.bind((self.ponto_acesso.endereco_ip, int(self.ponto_acesso.porto)))

        # Coloca o socket em modo de escuta, backlog=5 permite ate 5 ligações
        # pendentes em fila enquanto o servidor está ocupado
        self.sock_servidor.listen(5)

    def obter_socket_servidor(self):
        """Devolve o socket de escuta para ser monitorizado pelo select()."""
        return self.sock_servidor

    def aceitar_cliente(self):
        """Aceita uma nova ligação e devolve o socket da conexão.
        Chamado quando select() indica atividade no socket servidor."""
        conn_sock, (addr, port) = self.sock_servidor.accept()
        print(f"SERVIDOR> Nova ligação de {addr}:{port}")
        return conn_sock  # socket dedicado a este cliente

    def receber_pedido(self, conn_sock):
        """Recebe um pedido serializado de um cliente.

        Protocolo:
          1. Le 4 bytes -> tamanho da mensagem (big-endian unsigned int)
          2. Le x bytes -> mensagem pickle

        Devolve o objecto Python desserializado, ou None se o cliente
        fechou a ligação."""

        # Passo 1: le o cabeçalho de 4 bytes com o tamanho
        header = receive_all(conn_sock, 4)
        if not header:
            return None   # cliente desligou

        # Desempacota os 4 bytes como inteiro sem sinal (big-endian)
        tamanho = struct.unpack('!I', header)[0]

        # Passo 2: le x bytes de payload
        dados = receive_all(conn_sock, tamanho)
        if not dados:
            return None

        # Desserializa o payload pickle -> lista
        return pickle.loads(dados)

    def enviar_resposta(self, conn_sock, resposta):
        """Envia uma resposta serializada para um cliente.

        Protocolo:
          1. Serializa o objecto Python com pickle
          2. Envia: 4 bytes de tamanho + bytes serializados"""

        # Serializa a resposta (lista)
        dados = pickle.dumps(resposta)

        # Empacota o tamanho como inteiro de 4 bytes big-endian
        tamanho = struct.pack('!I', len(dados))

        # Envia tudo de uma vez (header + payload)
        conn_sock.sendall(tamanho + dados)

    def fechar_ligacao(self, conn_sock):
        """Fecha o socket de uma ligação individual com um cliente."""
        try:
            conn_sock.close()
        except Exception:
            pass   # ignora erros se o socket ja estiver fechado

    def fechar_servidor(self):
        """Fecha o socket de escuta principal do servidor."""
        try:
            self.sock_servidor.close()
        except Exception:
            pass
