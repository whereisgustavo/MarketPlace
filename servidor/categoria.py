"""
AD - Aplicações Distribuídas
Ano Letivo 2025/2026
Projeto - Fase 2

Grupo: 39

Elementos do Grupo:
- Diogo Silva (64143)
- Gustavo Santos (64167)

Descrição:
Define a classe Categoria, responsável por representar uma categoria de
produtos no sistema.
"""

class Categoria:
    _contador_global = 1

    def __init__(self, nome):
        self.id = Categoria._contador_global
        self.nome = nome
        Categoria._contador_global += 1

    def obter_id(self): 
        return self.id
