"""
AD - Aplicações Distribuídas
Ano Letivo 2025/2026
Projeto - Fase 2

Grupo: 39

Elementos do Grupo:
- Diogo Silva (64143)
- Gustavo Santos (64167)

Descrição:
Define a classe Encomenda, que representa uma encomenda realizada por um
cliente após o checkout do carrinho de compras.
"""



# Criação da class Encomenda - GS 06/03
class Encomenda:
    _contador_global = 1

    def __init__(self, id_cliente, produtos_carrinho, valor_total, data_hora, categoria_top):
        self.id = Encomenda._contador_global
        Encomenda._contador_global += 1
        self.id_cliente = id_cliente
        self.produtos = produtos_carrinho 
        self.valor_total = valor_total
        self.data_hora = data_hora
        self.categoria_top = categoria_top