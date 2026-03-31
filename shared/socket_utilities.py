"""
AD - Aplicações Distribuídas
Ano Letivo 2025/2026
Projeto - Fase 2

Grupo: 39

Elementos do Grupo:
- Diogo Silva (64143)
- Gustavo Santos (64167)

Descrição:
Utilitarios partilhados de rede:
  - receive_all : garante a leitura completa de N bytes (suporte a mensagens fragmentadas)
  - PontoAcesso : valida e guarda o endereço IP e porto do servidor
"""

import ipaddress
import socket

from shared.excepcoes import ExcepcaoIPInvalido
from shared.excepcoes import ExcepcaoPortoInvalido


# O TCP não garante que sock.recv(n) devolve exatamente n bytes de uma vez.
# A mensagem pode chegar em vários fragmentos. 
# Esta função chama recv() repetidamente até acumular todos os
# bytes pedidos, só retornando quando a mensagem está completa.
# Parâmetros:
#   sock: socket TCP ligado
#   n: número exacto de bytes a ler
#
# Devolve:
#   bytes com exatamente n bytes, ou None se a ligação foi fechada
def receive_all(sock, n):
    dados = b''                         # acumulador de bytes recebidos
    while len(dados) < n:
        # pede apenas os bytes que ainda faltam
        parte = sock.recv(n - len(dados))
        if not parte:
            # recv devolveu b'' -> o outro lado fechou a ligação
            return None
        dados += parte
    return dados


# Representa e valida o par (IP, porto) usado para ligar o cliente ao servidor.
# Lançada ExcepcaoIPInvalido ou ExcepcaoPortoInvalido se os valores forem invalidos.
class PontoAcesso:

    def __init__(self, endereco_ip, porto):
        # Valida primeiro, so guarda se ambos forem validos
        self._validar_endereco_ip(endereco_ip)
        self._validar_porto(porto)
        self.endereco_ip = endereco_ip
        self.porto = porto

    def _validar_porto(self, porto):
        # Porto tem de ser um inteiro entre 1024 e 65535
        try:
            porto = int(porto)
        except (ValueError, TypeError):
            raise ExcepcaoPortoInvalido(porto)

        if not (1024 <= porto <= 65535):
            raise ExcepcaoPortoInvalido(porto)

    def _validar_endereco_ip(self, endereco_ip):
        # Aceita "localhost" directamente, para o resto tenta fazer parse
        # como endereço IPv4 ou IPv6
        try:
            if 'localhost' != endereco_ip:
                ipaddress.ip_address(endereco_ip)
        except ValueError as e:
            raise ExcepcaoIPInvalido(endereco_ip)
