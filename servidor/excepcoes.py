"""
AD - Aplicações Distribuídas
Ano Letivo 2025/2026
Projeto - Fase 2

Grupo: 39

Elementos do Grupo:
- Diogo Silva (64143)
- Gustavo Santos (64167)

Descrição:
Define todas as exceções utilizadas no sistema, incluindo exceções de
comandos inválidos, validações e regras de negócio do supermercado.
"""


# -----------------------------------
#   Excepções de Comando inválido
# -----------------------------------

class ExcepcaoComandoInvalido(Exception):

    def __init__(self, msg):
        super().__init__(msg)

class ExcepcaoArgumentoFloatInvalido(ExcepcaoComandoInvalido):

    def __init__(self, nome_argumento):
        super().__init__(f"O argumento \'{nome_argumento}'\ não é um float válido.")    
class ExcepcaoArgumentoNaoInteiro(ExcepcaoComandoInvalido):

    def __init__(self, nome_argumento):
        super().__init__(f"O argumento \'{nome_argumento}'\ não é um inteiro válido.")    

class ExcepcaoComandoNaoInterpretavel(ExcepcaoComandoInvalido):

    def __init__(self, comando):
        super().__init__(f"Não foi possível interpretar o comando \'{comando}\'. ")

class ExcepcaoComandoVazio(ExcepcaoComandoInvalido):

    def __init__(self):
        super().__init__(f"Não é possível correr um comando vazio. ")

class ExcepcaoComandoDesconhecido(ExcepcaoComandoInvalido):

    def __init__(self, nome_comando):
        super().__init__(f"O comando {nome_comando} não é conhecido. ")

class ExcepcaoComandoNumeroArgumentosIncorreto(ExcepcaoComandoInvalido):

    def __init__(self, nr_argumentos_esperado, nr_argumentos_fornecido):
        super().__init__(f"O número de argumentos é inválido. O esperado é {nr_argumentos_esperado} e não {nr_argumentos_fornecido}. ")


# ----------------------------------
#   Excepções de Regras de Negócio
# ----------------------------------
class ExcepcaoSupermercado(Exception):
    
    def __init__(self, msg):
        super().__init__(msg)

class ExcepcaoSupermercadoCategoriaJaExistente(ExcepcaoSupermercado):

    def __init__(self, nome_categoria):
        super().__init__(f"A categoria {nome_categoria} já existe. ")
 
# CATEGORIA 
# adicionado 
class ExcepcaoSupermercadoCategoriaNaoExistente(ExcepcaoSupermercado):

    def __init__(self, nome_categoria):
        super().__init__(f"A categoria {nome_categoria} não existe. ")

# adicionado
class ExcepcaoSupermercadoCategoriaTemProduto(ExcepcaoSupermercado):
    def __init__(self, nome_categoria):
        super().__init__(f"A categoria {nome_categoria} tem produtos associados. ")

# PRODUTO
# adicionado
class ExcepcaoSupermercadoProdutoJaExistente(ExcepcaoSupermercado):

    def __init__(self, nome_produto):
        super().__init__(f"O produto {nome_produto} já existe. ")

# adicionado
class ExcepcaoSupermercadoProdutoNaoExistente(ExcepcaoSupermercado):

    def __init__(self, nome_produto):
        super().__init__(f"O produto {nome_produto} não existe. ")

# adicionado
class ExcepcaoSupermercadoPrecoInvalido(ExcepcaoSupermercado):

    def __init__(self):
        super().__init__(f"O preço é inválido. ")

# adicionado
class ExcepcaoSupermercadoQuantidadeInvalida(ExcepcaoSupermercado):

    def __init__(self):
        super().__init__(f"A quantidade é inválida. ")

# CLIENTE
# adicionado
class ExcepcaoSupermercadoProdutoNaoExistenteNoCarrinho(ExcepcaoSupermercado):

    def __init__(self):
        super().__init__(f"Produto não encontrado no carrinho. ")

class ExcepcaoSupermercadoEmailJaExistente(ExcepcaoSupermercado):

    def __init__(self, email):
        super().__init__(f"O email {email} já existe. ")

class ExcepcaoSupermercadoClienteNaoExistente(ExcepcaoSupermercado):

    def __init__(self):
        super().__init__(f"O cliente não existe. ")

class ExcepcaoSupermercadoClienteJaExistente(ExcepcaoSupermercado):

    def __init__(self):
        super().__init__(f"O cliente já existe. ")

class ExcepcaoSupermercadoCarrinhoVazio(ExcepcaoSupermercado):

    def __init__(self):
        super().__init__(f"Carrinho vazio. ")
