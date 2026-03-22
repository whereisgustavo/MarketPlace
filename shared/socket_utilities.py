"""
AD - Aplicações Distribuídas
Ano Letivo 2025/2026
Projeto - Fase 2

Grupo: 39

Elementos do Grupo:
- Diogo Silva (64143)
- Gustavo Santos (64167)

Descrição:
Contém a classe PontoAcesso responsável por validar e representar um endereço IP e porto.
"""

import ipaddress
import socket #GS - 03/03/2026

from shared.excepcoes import ExcepcaoIPInvalido
from shared.excepcoes import ExcepcaoPortoInvalido

class PontoAcesso:
    def __init__(self, endereco_ip, porto):
        # Validar IP e porto
        # Lança ExcepcaoIPInvalido e ExcepcaoPortoInvalido
        self._validar_endereco_ip(endereco_ip)
        self._validar_porto(porto)

        self.endereco_ip = endereco_ip
        self.porto = porto

    def _validar_porto(self, porto):
        try:
            porto = int(porto)
        except (ValueError, TypeError):
            raise ExcepcaoPortoInvalido(porto)

        if not (1024 <= porto <= 65535):
            raise ExcepcaoPortoInvalido(porto)

    def _validar_endereco_ip(self, endereco_ip):
        # Validar IP (IPv4 ou IPv6)
        try:
            if 'localhost' != endereco_ip:
                ipaddress.ip_address(endereco_ip)
        except ValueError as e:
            raise ExcepcaoIPInvalido(endereco_ip)