from shared.utilities import normalizar_nome
from servidor.categoria import Categoria
from servidor.excepcoes import ExcepcaoSupermercadoCategoriaJaExistente
from servidor.excepcoes import ExcepcaoSupermercadoCategoriaNaoExistente
from servidor.excepcoes import ExcepcaoSupermercadoCategoriaTemProduto
from servidor.produto import Produto
from servidor.excepcoes import ExcepcaoSupermercadoProdutoJaExistente
from servidor.excepcoes import ExcepcaoSupermercadoProdutoNaoExistente
from servidor.excepcoes import ExcepcaoSupermercadoPrecoInvalido
from servidor.excepcoes import ExcepcaoSupermercadoQuantidadeInvalida
from servidor.cliente import Cliente
from servidor.excepcoes import ExcepcaoSupermercadoEmailJaExistente


class Loja:

    def __init__(self):
        self._categorias = {}

        # adicionado
        # ainda n há produtos, mas para usar o REMOVE_CATEGORIA temos de saber se há produtos
        # fica vazio, conta 0   
        self._produtos = {}
        self._clientes = {}

    def reset(): 
        Categoria._contador_global = 1
        Produto._contador_global = 1
        Cliente._contador_global = 1
        # TODO: MUITO IMPORTANTE Completar esta funcao para Testes Unitários puderem executar sem problemas

    # -----------------------------
    # Categorias 
    # -----------------------------
    def criar_categoria(self, nome):
        nome = normalizar_nome(nome)
        if self.obter_id_categoria(nome) is not None:
            raise ExcepcaoSupermercadoCategoriaJaExistente(nome)
        categoria = Categoria(nome)
        self._categorias[categoria.id] = categoria
        return categoria
    
    def obter_id_categoria(self, nome): 
        for c in self._categorias.values(): 
            if nome == c.nome: 
                return c.id
        return None
    
    # adicionado
    # metodo apenas usado em Loja 
    def _numero_produtos_categoria(self, id_categoria):
        total = 0
        for p in self._produtos.values(): 
            if p.id_categoria == id_categoria:
                total += 1
        return total
    
    # adicionado
    def listar_categorias(self):
        if len(self._categorias) == 0:
            return "Sem Categorias."
        
        # total de produtos, nº total de produtos que estão registados
        prod_total = len(self._produtos)

        linhas = []
        linhas.append(f"Total Categorias: {len(self._categorias)}")
        linhas.append(f"Total Produtos: {prod_total}")

        # ordena por id_categoria
        for id_categoria in sorted(self._categorias.keys()):
            categoria = self._categorias[id_categoria]
            n_prod_categoria = self._numero_produtos_categoria(id_categoria)
            linhas.append(f"{categoria.id} - {categoria.nome} ({n_prod_categoria} produtos)")

        return "\n".join(linhas)
    
    # adicionado
    def remover_categoria(self, nome):
        nome_normalizado = normalizar_nome(nome)
        id_categoria = self.obter_id_categoria(nome_normalizado)

        if id_categoria is None:
            raise ExcepcaoSupermercadoCategoriaNaoExistente(nome_normalizado)
        
        # se tem produtos, não pode remover (regra dita pela professora)
        if self._numero_produtos_categoria(id_categoria) > 0:
            raise ExcepcaoSupermercadoCategoriaTemProduto(nome_normalizado)
        
        categoria = self._categorias[id_categoria]
        del self._categorias[id_categoria]
        return categoria
    
    # -----------------------------
    # Produtos 
    # -----------------------------

    # adicionado
    def obter_produto_id(self, nome_produto):
        nome_normalizado = normalizar_nome(nome_produto)
        for p in self._produtos.values():
            if p.nome == nome_normalizado:
                return p.id
        return None
    
    # adicionado
    def criar_produto(self, nome_produto, nome_categoria, preco, quantidade):
        nome_produto_normalizado = normalizar_nome(nome_produto)
        nome_categoria_normalizado = normalizar_nome(nome_categoria)

        if self.obter_produto_id(nome_produto_normalizado) is not None:
            raise ExcepcaoSupermercadoProdutoJaExistente(nome_produto_normalizado)
        
        id_categoria = self.obter_id_categoria(nome_categoria_normalizado)
        if id_categoria is None:
            raise ExcepcaoSupermercadoCategoriaNaoExistente(nome_categoria_normalizado)
        
        # validar preco
        try:
            preco = float(preco)
        except (ValueError, TypeError):
            raise ExcepcaoSupermercadoPrecoInvalido()
        if preco <= 0:
            raise ExcepcaoSupermercadoPrecoInvalido()
        
        # validar quantidade
        try:
            quantidade = int(quantidade)
        except (ValueError, TypeError):
            raise ExcepcaoSupermercadoQuantidadeInvalida()
        if quantidade < 0:
            raise ExcepcaoSupermercadoQuantidadeInvalida()
        
        produto = Produto(nome_produto_normalizado, id_categoria, nome_categoria_normalizado, preco, quantidade)
        self._produtos[produto.id] = produto
        return produto
    
    # adicionado
    def listar_produtos(self):
        if len(self._produtos) == 0:
            return "Sem Produtos."
        
        quantidade_total = 0
        for p in self._produtos.values():
            quantidade_total += p.quantidade

        linhas = []
        linhas.append(f"Total Produtos: {len(self._produtos)}")
        linhas.append(f"Total Quantidade: {quantidade_total}")

        for id_produto in sorted(self._produtos.keys()):
            p = self._produtos[id_produto]
            preco_str = f"{p.preco:.2f}"
            linhas.append(
                f"{p.id} - {p.nome} ({p.nome_categoria}, {preco_str} euros, {p.quantidade} unidades);"
            )
        
        return "\n".join(linhas)
    
    # adicionado
    def aumentar_stock_produto(self, nome_produto, delta_quantidade):
        nome_produto_normalizado = normalizar_nome(nome_produto)

        id_produto = self.obter_produto_id(nome_produto_normalizado)
        if id_produto is None:
            raise ExcepcaoSupermercadoProdutoNaoExistente(nome_produto_normalizado)
        
        try:
            delta_quantidade = int(delta_quantidade)
        except (ValueError, TypeError):
            raise ExcepcaoSupermercadoQuantidadeInvalida()
        if delta_quantidade < 0:
            raise ExcepcaoSupermercadoQuantidadeInvalida()
        
        produto = self._produtos[id_produto]
        produto.quantidade += delta_quantidade
        return f"Stock do produto {produto.nome} aumentado em {delta_quantidade} unidades com sucesso."
    
    # adicionado
    def atualizar_preco(self, nome_produto, preco):
        nome_produto_normalizado = normalizar_nome(nome_produto)

        id_produto = self.obter_produto_id(nome_produto_normalizado)
        if id_produto is None:
            raise ExcepcaoSupermercadoProdutoNaoExistente(nome_produto_normalizado)
        
        try:
            novo_preco = float(preco)
        except (ValueError, TypeError):
            raise ExcepcaoSupermercadoPrecoInvalido()
        
        if novo_preco <= 0:
            raise ExcepcaoSupermercadoPrecoInvalido()
        
        produto = self._produtos[id_produto]    
        produto.preco = round(novo_preco, 2)

        preco_str = f"{produto.preco:.2f}"
        
        return f"O preço do produto {produto.nome} foi atualizado para {preco_str} com sucesso."
    
    # -----------------------------
    # Clientes
    # -----------------------------

    # adicionado
    def criar_cliente(self, nome_cliente, email, password):
        nome_cliente_normalizado = normalizar_nome(nome_cliente)
        
        email = email.strip()
        email_normalizado = email.lower()

        for c in self._clientes.values():
            if c.email.lower() == email_normalizado:
                raise ExcepcaoSupermercadoEmailJaExistente(email)
        
        cliente = Cliente(nome_cliente_normalizado, email_normalizado, password)
        self._clientes[cliente.id] = cliente
        return cliente
    
    # adicionado
    def listar_clientes(self):
        if len(self._clientes) == 0:
            return "Sem Clientes."
        
        linhas = []
        linhas.append(f"Total Clientes: {len(self._clientes)}")
        for id_cliente in sorted(self._clientes.keys()):
            c = self._clientes[id_cliente]
            linhas.append(f"{c.id} - {c.nome} ({c.email})")
        
        return "\n".join(linhas)

    