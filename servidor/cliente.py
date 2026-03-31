"""
AD - Aplicações Distribuídas
Ano Letivo 2025/2026
Projeto - Fase 2

Grupo: 39

Elementos do Grupo:
- Diogo Silva (64143)
- Gustavo Santos (64167)

Descrição:
Define a classe Cliente. 
Representa um utilizador registado no sistema.
O ID é atribuido automaticamente. 
"""


class Cliente:

    # Contador de classe: garante IDs unicos e sequenciais para clientes
    _contador_global = 1

    def __init__(self, nome, email, password):
        # ID unico deste cliente
        self.id_cliente = Cliente._contador_global
        Cliente._contador_global += 1

        # Nome normalizado (Title Case, sem espaços)
        self.nome = nome

        # Email em minusculas (normalizado para comparações unicas)
        self.email = email

        # Password em texto limpo
        self.password = password
