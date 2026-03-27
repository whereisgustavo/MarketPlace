"""
AD - Aplicações Distribuídas
Ano Letivo 2025/2026
Projeto - Fase 2

Grupo: 39

Elementos do Grupo:
- Diogo Silva (64143)
- Gustavo Santos (64167)

Descrição:
Define a classe Produto. Cada produto pertence a uma categoria e tem
nome, preço e quantidade em stock. O ID é atribuido automaticamente.
"""


class Produto:

    # Contador de classe: atribui IDs unicos e sequenciais a cada produto
    _contador_global = 1

    def __init__(self, nome, id_categoria, nome_categoria, preco, quantidade):
        # ID unico deste produto 
        self.id_produto = Produto._contador_global
        Produto._contador_global += 1

        # Nome normalizado do produto (Title Case)
        self.nome = nome

        # ID numerico da categoria a que este produto pertence
        self.id_categoria = id_categoria

        # Nome da categoria (saved para facilitar a formatação de output
        # sem ter de fazer lookup à Loja)
        self.categoria = nome_categoria

        # Preço arredondado a 2 casas decimais
        self.preco = round(preco, 2)

        # Quantidade atual em stock
        # (é decrementada quando um produto é adicionado ao carrinho
        #  e restaurada quando é removido)
        self.quantidade = quantidade
