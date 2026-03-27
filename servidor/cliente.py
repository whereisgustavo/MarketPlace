"""
AD - Aplicações Distribuídas
Ano Letivo 2025/2026
Projeto - Fase 2

Grupo: 39

Elementos do Grupo:
- Diogo Silva (64143)
- Gustavo Santos (64167)

Descrição:
Define a classe Cliente. Representa um utilizador registado no sistema.
O ID é atribuido automaticamente. O email é guardado em minusculas para
garantir comparações case-insensitive. A password é guardada em texto
limpo.
"""


class Cliente:

    # Contador de classe: garante IDs unicos e sequenciais para clientes
    _contador_global = 1

    def __init__(self, nome, email, password):
        # ID único deste cliente
        self.id_cliente = Cliente._contador_global
        Cliente._contador_global += 1

        # Nome normalizado (Title Case, sem espaços redundantes)
        self.nome = nome

        # Email em minúsculas (normalizado para comparações unicas)
        self.email = email

        # Password em texto limpo (sem hash nesta fase do projeto)
        self.password = password
