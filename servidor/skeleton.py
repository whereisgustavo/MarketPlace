"""
AD - Aplicações Distribuídas
Ano Letivo 2025/2026
Projeto - Fase 2

Grupo: 39

Elementos do Grupo:
- Diogo Silva (64143)
- Gustavo Santos (64167)

Descrição:
Camada Skeleton do servidor — lado servidor do modelo RPC.

O Skeleton é o par complementar do Stub (no cliente).
Recebe pedidos ja desserializados (listas), valida a estrutura,
verifica as permissões do perfil e chama a Loja para executar a operação.
Devolve sempre uma lista [op_code_resposta, [dados]] para ser serializada
e enviada de volta ao cliente.

Formato dos pedidos recebidos:
    [op_code, [arg1, arg2, ...], id_perfil, id_utilizador]

Formato das respostas enviadas:
    Sucesso : [2xxxx, [dado1, dado2, ...]]
    Erro    : [3xxxx, [mensagem_de_erro]]
"""

from shared.excepcoes_shared import OpCodes
from servidor.loja import Loja
from servidor.excepcoes import ExcepcaoSupermercadoCategoriaJaExistente
from servidor.excepcoes import ExcepcaoSupermercadoCategoriaNaoExistente
from servidor.excepcoes import ExcepcaoSupermercadoCategoriaTemProduto
from servidor.excepcoes import ExcepcaoSupermercadoProdutoJaExistente
from servidor.excepcoes import ExcepcaoSupermercadoProdutoNaoExistente
from servidor.excepcoes import ExcepcaoSupermercadoProdutoNaoExistenteNoCarrinho
from servidor.excepcoes import ExcepcaoSupermercadoClienteNaoExistente
from servidor.excepcoes import ExcepcaoSupermercadoEmailJaExistente
from servidor.excepcoes import ExcepcaoSupermercadoPrecoInvalido
from servidor.excepcoes import ExcepcaoSupermercadoQuantidadeInvalida
from servidor.excepcoes import ExcepcaoSupermercadoStockInsuficiente
from servidor.excepcoes import ExcepcaoSupermercadoCarrinhoVazio


# Códigos de perfil (quem está a fazer o pedido)
CLIENTE_ANONIMO = 0
CLIENTE_REGISTADO = 1
FUNCIONARIO = 2
ADMINISTRADOR = 3


# Atalhos locais para OpCodes (de shared.excepcoes_shared)
# Pedidos (1xxxx)
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


# Sucesso (2xxxx)
OK_CRIA_CATEGORIA = OpCodes.OK_CRIA_CATEGORIA
OK_LISTA_CATEGORIAS = OpCodes.OK_LISTA_CATEGORIAS
OK_REMOVE_CATEGORIA = OpCodes.OK_REMOVE_CATEGORIA
OK_CRIA_PRODUTO = OpCodes.OK_CRIA_PRODUTO
OK_LISTA_PRODUTOS = OpCodes.OK_LISTA_PRODUTOS
OK_AUMENTA_STOCK = OpCodes.OK_AUMENTA_STOCK
OK_ATUALIZA_PRECO = OpCodes.OK_ATUALIZA_PRECO
OK_CRIA_CLIENTE = OpCodes.OK_CRIA_CLIENTE
OK_LISTA_CLIENTES = OpCodes.OK_LISTA_CLIENTES
OK_ADICIONA_CARRINHO = OpCodes.OK_ADICIONA_CARRINHO
OK_REMOVE_CARRINHO = OpCodes.OK_REMOVE_CARRINHO
OK_LISTA_CARRINHO = OpCodes.OK_LISTA_CARRINHO
OK_CHECKOUT = OpCodes.OK_CHECKOUT
OK_LISTA_ENCOMENDAS = OpCodes.OK_LISTA_ENCOMENDAS


# Erros genericos (39xxx)
ERR_GENERICO = OpCodes.ERRO_GENERICO
ERR_OP_INVALIDO = OpCodes.OP_CODE_INVALIDO
ERR_MENSAGEM_MAL_FORMADA = OpCodes.MENSAGEM_MAL_FORMADA
ERR_PEDIDO_NAO_LISTA = OpCodes.PEDIDO_NAO_LISTA
ERR_NUMERO_CAMPOS = OpCodes.NUMERO_CAMPOS_INVALIDO
ERR_ARGS_NAO_LISTA = OpCodes.ARGS_NAO_LISTA
ERR_PERFIL_INVALIDO = OpCodes.PERFIL_INVALIDO
ERR_DESSERIALIZACAO = OpCodes.DESSERIALIZACAO
ERR_N_ARGS = OpCodes.NUMERO_ARGUMENTOS_INVALIDO
ERR_TIPO_ARG = OpCodes.TIPO_ARGUMENTO_INVALIDO
ERR_OPERACAO_NAO_AUTORIZADA = OpCodes.OPERACAO_NAO_AUTORIZADA
ERR_INTERNO = OpCodes.ERRO_INTERNO_SERVIDOR


# Permissões: para cada op_code, lista dos perfis autorizados
PERMISSOES = {
    OP_CRIA_CATEGORIA: [ADMINISTRADOR],
    OP_LISTA_CATEGORIAS: [CLIENTE_ANONIMO, CLIENTE_REGISTADO, FUNCIONARIO, ADMINISTRADOR],
    OP_REMOVE_CATEGORIA: [ADMINISTRADOR],
    OP_CRIA_PRODUTO: [ADMINISTRADOR, FUNCIONARIO],
    OP_LISTA_PRODUTOS: [CLIENTE_ANONIMO, CLIENTE_REGISTADO, FUNCIONARIO, ADMINISTRADOR],
    OP_AUMENTA_STOCK: [ADMINISTRADOR, FUNCIONARIO],
    OP_ATUALIZA_PRECO: [ADMINISTRADOR, FUNCIONARIO],
    OP_CRIA_CLIENTE: [CLIENTE_ANONIMO],
    OP_LISTA_CLIENTES: [ADMINISTRADOR, FUNCIONARIO],
    OP_ADICIONA_CARRINHO: [CLIENTE_REGISTADO],
    OP_REMOVE_CARRINHO: [CLIENTE_REGISTADO],
    OP_LISTA_CARRINHO: [CLIENTE_REGISTADO],
    OP_CHECKOUT: [CLIENTE_REGISTADO],
    OP_LISTA_ENCOMENDAS: [CLIENTE_REGISTADO, FUNCIONARIO, ADMINISTRADOR],
}


# Numero de argumentos esperados por operação
N_ARGS = {
    OP_CRIA_CATEGORIA: 1, # [nome]
    OP_LISTA_CATEGORIAS: 0, # []
    OP_REMOVE_CATEGORIA: 1, # [nome]
    OP_CRIA_PRODUTO: 4, # [nome, categoria, preco, quantidade]
    OP_LISTA_PRODUTOS: 0, # []
    OP_AUMENTA_STOCK: 2, # [nome, delta]
    OP_ATUALIZA_PRECO: 2, # [nome, novo_preco]
    OP_CRIA_CLIENTE: 3, # [nome, email, password]
    OP_LISTA_CLIENTES: 0, # []
    OP_ADICIONA_CARRINHO: 2, # [nome_produto, quantidade]
    OP_REMOVE_CARRINHO: 1, # [nome_produto]
    OP_LISTA_CARRINHO: 0, # []
    OP_CHECKOUT: 0, # []
    OP_LISTA_ENCOMENDAS: 1, # [id_cliente]
}


def _erro(code, msg=""):
    """Constroi uma resposta de erro no formato padrão [code, mensagem]."""
    return [code, [msg]]


class Skeleton:

    def __init__(self, loja):
        # Referencia à loja partilhada por todos os clientes
        self.loja = loja

    def processar_pedido(self, pedido):
        """Ponto de entrada do Skeleton.

        Recebe um pedido já desserializado (lista),
        valida a estrutura, verifica perfil e envia para o handler.

        Devolve sempre [op_code_resposta, dados] para ser serializado
        e enviado ao cliente."""


        # Validações de estrutura

        # O pedido tem de ser uma lista
        if not isinstance(pedido, list):
            return _erro(ERR_PEDIDO_NAO_LISTA, "Pedido não é uma lista.")

        # O pedido tem 4 campos: [op_code, args, id_perfil, id_utilizador]
        if len(pedido) != 4:
            return _erro(ERR_NUMERO_CAMPOS, f"Pedido deve ter 4 campos, tem {len(pedido)}.")

        op_code, args, id_perfil, id_utilizador = pedido

        # Os argumentos tem de ser uma lista
        if not isinstance(args, list):
            return _erro(ERR_ARGS_NAO_LISTA, "Argumentos devem ser uma lista.")

        # O perfil tem de ser um dos 4 validos
        if id_perfil not in [CLIENTE_ANONIMO, CLIENTE_REGISTADO, FUNCIONARIO, ADMINISTRADOR]:
            return _erro(ERR_PERFIL_INVALIDO, f"Perfil {id_perfil} inválido.")

        # O op_code tem de existir na tabela de permissões
        if op_code not in PERMISSOES:
            return _erro(ERR_OP_INVALIDO, f"OpCode {op_code} desconhecido.")

        # Verificação de autorização 
        if id_perfil not in PERMISSOES[op_code]:
            return _erro(ERR_OPERACAO_NAO_AUTORIZADA, "Operação não autorizada para este perfil.")

        # Verificação do numero de argumentos
        if len(args) != N_ARGS[op_code]:
            return _erro(ERR_N_ARGS, f"Esperado {N_ARGS[op_code]} argumentos, recebido {len(args)}.")

        # Execução
        try:
            return self._dispatch(op_code, args, id_perfil, id_utilizador)
        except Exception as e:
            # Captura qualquer exceção inesperada para não bloquear o servidor
            return _erro(ERR_INTERNO, str(e))

    def _dispatch(self, op_code, args, id_perfil, id_utilizador):
        """Encaminha o pedido para o handler correcto com base no op_code."""
        if op_code == OP_CRIA_CATEGORIA:
            return self._cria_categoria(args)
        if op_code == OP_LISTA_CATEGORIAS:
            return self._lista_categorias()
        if op_code == OP_REMOVE_CATEGORIA:
            return self._remove_categoria(args)
        if op_code == OP_CRIA_PRODUTO:
            return self._cria_produto(args)
        if op_code == OP_LISTA_PRODUTOS:
            return self._lista_produtos()
        if op_code == OP_AUMENTA_STOCK:
            return self._aumenta_stock(args)
        if op_code == OP_ATUALIZA_PRECO:
            return self._atualiza_preco(args)
        if op_code == OP_CRIA_CLIENTE:
            return self._cria_cliente(args)
        if op_code == OP_LISTA_CLIENTES:
            return self._lista_clientes()
        if op_code == OP_ADICIONA_CARRINHO:
            # id_utilizador identifica o cliente dono do carrinho (sem passar id_cliente nos args)
            return self._adiciona_carrinho(args, id_utilizador)
        if op_code == OP_REMOVE_CARRINHO:
            return self._remove_carrinho(args, id_utilizador)
        if op_code == OP_LISTA_CARRINHO:
            return self._lista_carrinho(id_utilizador)
        if op_code == OP_CHECKOUT:
            return self._checkout(id_utilizador)
        if op_code == OP_LISTA_ENCOMENDAS:
            # id_cliente vem nos args (admins podem ver encomendas de qualquer cliente)
            return self._lista_encomendas(args)
        return _erro(ERR_OP_INVALIDO, "OpCode não tratado.")

    # Handlers individuais (chamam a Loja e traduzem exceções em erros)

    def _cria_categoria(self, args):
        try:
            categoria = self.loja.criar_categoria(args[0])
            return [OK_CRIA_CATEGORIA, [categoria]]
        except ExcepcaoSupermercadoCategoriaJaExistente as e:
            return _erro(30110, str(e))   # categoria já existe
        except Exception as e:
            return _erro(30101, str(e))   # erro geral

    def _lista_categorias(self):
        try:
            categorias, produtos = self.loja.listar_categorias()
            # Devolve as duas listas para o stub formatar o output
            return [OK_LISTA_CATEGORIAS, [categorias, produtos]]
        except Exception as e:
            return _erro(30201, str(e))

    def _remove_categoria(self, args):
        try:
            self.loja.remover_categoria(args[0])
            return [OK_REMOVE_CATEGORIA, []]
        except ExcepcaoSupermercadoCategoriaNaoExistente as e:
            return _erro(30310, str(e))   # categoria não existe
        except ExcepcaoSupermercadoCategoriaTemProduto as e:
            return _erro(30311, str(e))   # categoria tem produtos com stock
        except Exception as e:
            return _erro(30301, str(e))

    def _cria_produto(self, args):
        try:
            produto = self.loja.criar_produto(args[0], args[1], args[2], args[3])
            return [OK_CRIA_PRODUTO, [produto]]
        except ExcepcaoSupermercadoProdutoJaExistente as e:
            return _erro(30410, str(e))
        except ExcepcaoSupermercadoCategoriaNaoExistente as e:
            return _erro(30411, str(e))
        except ExcepcaoSupermercadoPrecoInvalido as e:
            return _erro(30412, str(e))
        except ExcepcaoSupermercadoQuantidadeInvalida as e:
            return _erro(30413, str(e))
        except Exception as e:
            return _erro(30401, str(e))

    def _lista_produtos(self):
        try:
            categorias, produtos = self.loja.listar_produtos()
            return [OK_LISTA_PRODUTOS, [categorias, produtos]]
        except Exception as e:
            return _erro(30501, str(e))

    def _aumenta_stock(self, args):
        try:
            produto = self.loja.aumentar_stock_produto(args[0], args[1])
            return [OK_AUMENTA_STOCK, [produto]]
        except ExcepcaoSupermercadoProdutoNaoExistente as e:
            return _erro(30610, str(e))
        except ExcepcaoSupermercadoQuantidadeInvalida as e:
            return _erro(30611, str(e))
        except Exception as e:
            return _erro(30601, str(e))

    def _atualiza_preco(self, args):
        try:
            produto = self.loja.atualizar_preco(args[0], args[1])
            return [OK_ATUALIZA_PRECO, [produto]]
        except ExcepcaoSupermercadoProdutoNaoExistente as e:
            return _erro(30710, str(e))
        except ExcepcaoSupermercadoPrecoInvalido as e:
            return _erro(30711, str(e))
        except Exception as e:
            return _erro(30701, str(e))

    def _cria_cliente(self, args):
        try:
            cliente = self.loja.criar_cliente(args[0], args[1], args[2])
            return [OK_CRIA_CLIENTE, [cliente]]
        except ExcepcaoSupermercadoEmailJaExistente as e:
            return _erro(30810, str(e))
        except Exception as e:
            return _erro(30801, str(e))

    def _lista_clientes(self):
        try:
            clientes = self.loja.listar_clientes()
            return [OK_LISTA_CLIENTES, [clientes]]
        except Exception as e:
            return _erro(30901, str(e))

    def _adiciona_carrinho(self, args, id_utilizador):
        # id_cliente é o id_utilizador da sessão (não vem nos args)
        try:
            produto = self.loja.adiciona_produto_carrinho(id_utilizador, args[0], args[1])
            return [OK_ADICIONA_CARRINHO, [produto]]
        except ExcepcaoSupermercadoClienteNaoExistente as e:
            return _erro(31010, str(e))
        except ExcepcaoSupermercadoProdutoNaoExistente as e:
            return _erro(31011, str(e))
        except ExcepcaoSupermercadoQuantidadeInvalida as e:
            return _erro(31012, str(e))
        except ExcepcaoSupermercadoStockInsuficiente as e:
            return _erro(31013, str(e))
        except Exception as e:
            return _erro(31001, str(e))

    def _remove_carrinho(self, args, id_utilizador):
        try:
            produto = self.loja.remover_produto_carrinho(id_utilizador, args[0])
            return [OK_REMOVE_CARRINHO, [produto]]
        except ExcepcaoSupermercadoClienteNaoExistente as e:
            return _erro(31110, str(e))
        except ExcepcaoSupermercadoProdutoNaoExistente as e:
            return _erro(31111, str(e))
        except ExcepcaoSupermercadoProdutoNaoExistenteNoCarrinho as e:
            return _erro(31112, str(e))
        except Exception as e:
            return _erro(31101, str(e))

    def _lista_carrinho(self, id_utilizador):
        try:
            categorias, produtos = self.loja.listar_carrinho(id_utilizador)
            return [OK_LISTA_CARRINHO, [categorias, produtos]]
        except ExcepcaoSupermercadoClienteNaoExistente as e:
            return _erro(31210, str(e))
        except Exception as e:
            return _erro(31201, str(e))

    def _checkout(self, id_utilizador):
        try:
            encomenda = self.loja.checkout_carrinho(id_utilizador)
            return [OK_CHECKOUT, [encomenda]]
        except ExcepcaoSupermercadoClienteNaoExistente as e:
            return _erro(31310, str(e))
        except ExcepcaoSupermercadoCarrinhoVazio as e:
            return _erro(31311, str(e))
        except Exception as e:
            return _erro(31301, str(e))

    def _lista_encomendas(self, args):
        try:
            id_cliente = int(args[0])
            cliente, encomendas, prods_por_encomenda = self.loja.listar_encomendas_cliente(id_cliente)
            # Devolve os 3 elementos para o stub formatar o cabeçalho e as linhas
            return [OK_LISTA_ENCOMENDAS, [cliente, encomendas, prods_por_encomenda]]
        except ExcepcaoSupermercadoClienteNaoExistente as e:
            return _erro(31410, str(e))
        except Exception as e:
            return _erro(31401, str(e))
