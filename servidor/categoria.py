"""
AD - Aplicações Distribuídas
Ano Letivo 2025/2026
Projeto - Fase 2

Grupo: 39

Elementos do Grupo:
- Diogo Silva (64143)
- Gustavo Santos (64167)

Descrição:
Define a classe Categoria. Cada categoria agrupa um conjunto de produtos
na loja (ex: "Fruta", "Laticínios"). O ID é atribuído automaticamente
pelo contador de classe e nunca é reutilizado.
"""


class Categoria:

    # Contador de classe: partilhado por todas as instâncias.
    # Começa em 1 e incrementa a cada nova categoria criada.
    # Nunca é decrementado, mesmo que uma categoria seja removida.
    _contador_global = 1

    def __init__(self, nome):
        # Atribui o próximo ID disponivel a esta categoria
        self.id_categoria = Categoria._contador_global

        # Nome normalizado (Title Case, sem espaços redundantes)
        self.nome = nome

        # Avança o contador para a proxima categoria
        Categoria._contador_global += 1
