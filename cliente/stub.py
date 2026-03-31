"""
AD - Aplicações Distribuídas
Ano Letivo 2025/2026
Projeto - Fase 2

Grupo: 39

Elementos do Grupo:
- Diogo Silva (64143)
- Gustavo Santos (64167)

Descrição:
Stub do cliente, proxy RPC fino.

Cada metodo serializa o pedido [op_code, args, id_perfil, id_utilizador],
envia pela rede e devolve a resposta bruta [op_code_resp, dados].
Não formata texto, essa responsabilidade é do ProcessadorCliente.
"""

from shared.excepcoes_shared import OpCodes

# op_codes (série 1xxxx)
OP_CRIA_CATEGORIA = OpCodes.CRIA_CATEGORIA
OP_LISTA_CATEGORIAS = OpCodes.LISTA_CATEGORIAS
OP_REMOVE_CATEGORIA = OpCodes.REMOVE_CATEGORIA
OP_CRIA_PRODUTO = OpCodes.CRIA_PRODUTO
OP_LISTA_PRODUTOS = OpCodes.LISTA_PRODUTOS
OP_AUMENTA_STOCK = OpCodes.AUMENTA_STOCK
OP_ATUALIZA_PRECO = OpCodes.ATUALIZA_PRECO
OP_CRIA_CLIENTE = OpCodes.CRIA_CLIENTE
OP_LISTA_CLIENTES = OpCodes.LISTA_CLIENTES
OP_ADICIONA_CARRINHO = OpCodes.ADICIONA_PRODUTO_CARRINHO
OP_REMOVE_CARRINHO = OpCodes.REMOVE_PRODUTO_CARRINHO
OP_LISTA_CARRINHO = OpCodes.LISTA_CARRINHO
OP_CHECKOUT = OpCodes.CHECKOUT_CARRINHO
OP_LISTA_ENCOMENDAS = OpCodes.LISTA_ENCOMENDAS


class Stub:

    def __init__(self, rede, id_perfil, id_utilizador):
        self.rede = rede
        self.id_perfil = id_perfil
        self.id_utilizador = id_utilizador

    def _enviar(self, op_code, args):
        """Constrói o pedido, envia e devolve a resposta bruta [op_code, [dados]]."""
        pedido = [op_code, args, self.id_perfil, self.id_utilizador]
        self.rede.enviar_pedido(pedido)
        return self.rede.receber_resposta()

    # Categorias
    def cria_categoria(self, nome):         
        return self._enviar(OP_CRIA_CATEGORIA, [nome])
    def lista_categorias(self):             
        return self._enviar(OP_LISTA_CATEGORIAS, [])
    def remove_categoria(self, nome):       
        return self._enviar(OP_REMOVE_CATEGORIA, [nome])

    # Produtos
    def cria_produto(self, nome, cat, preco, qtd): 
        return self._enviar(OP_CRIA_PRODUTO, [nome, cat, float(preco), int(qtd)])
    def lista_produtos(self):               
        return self._enviar(OP_LISTA_PRODUTOS, [])
    def aumenta_stock(self, nome, delta):   
        return self._enviar(OP_AUMENTA_STOCK, [nome, int(delta)])
    def atualiza_preco(self, nome, preco):  
        return self._enviar(OP_ATUALIZA_PRECO, [nome, float(preco)])

    # Clientes
    def cria_cliente(self, nome, email, pw): 
        return self._enviar(OP_CRIA_CLIENTE, [nome, email, pw])
    def lista_clientes(self):               
        return self._enviar(OP_LISTA_CLIENTES, [])

    # Carrinho (id_cliente vem de id_utilizador)
    def adiciona_produto_carrinho(self, nome, qtd): 
        return self._enviar(OP_ADICIONA_CARRINHO, [nome, int(qtd)])
    def remove_produto_carrinho(self, nome):        
        return self._enviar(OP_REMOVE_CARRINHO, [nome])
    def lista_carrinho(self):               
        return self._enviar(OP_LISTA_CARRINHO, [])
    def checkout_carrinho(self):            
        return self._enviar(OP_CHECKOUT, [])

    # Encomendas (admins podem ver qualquer cliente)
    def lista_encomendas(self, id_cliente): 
        return self._enviar(OP_LISTA_ENCOMENDAS, [int(id_cliente)])
