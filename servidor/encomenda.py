"""
AD - Aplicações Distribuídas
Ano Letivo 2025/2026
Projeto - Fase 2

Grupo: 39

Elementos do Grupo:
- Diogo Silva (64143)
- Gustavo Santos (64167)

Descrição:
Define a classe Encomenda. 
Uma encomenda é criada quando um cliente faz checkout do carrinho. 
Guarda o estado dos produtos no momento da compra (preço e quantidade) 
para não ser afetada por alterações futuras.
"""

class Encomenda:

    # Contador de classe: IDs unicos e sequenciais para encomendas
    _contador_global = 1

    def __init__(self, id_cliente, produtos_carrinho, total_preco, data, categoria_top):
        # ID unico desta encomenda
        self.id_encomenda = Encomenda._contador_global
        Encomenda._contador_global += 1

        # ID do cliente que fez a encomenda
        self.id_cliente = id_cliente

        # Dicionario {id_produto: quantidade}
        # As quantidades guardadas são as que foram compradas.
        self.produtos = produtos_carrinho

        # Preço total da encomenda (soma de preço × quantidade de cada produto)
        # 2 casas decimais
        self.total_preco = total_preco

        # Data e hora do checkout (YYYY-MM-DD HH:MM:SS)
        self.data = data

        # Categoria com mais unidades vendidas nesta encomenda
        # caso de empate, uma virgula a dividir
        self.categoria_top = categoria_top
