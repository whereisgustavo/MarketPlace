"""
AD - Aplicações Distribuídas
Ano Letivo 2025/2026
Projeto - Fase 2

Grupo: 39

Elementos do Grupo:
- Diogo Silva (64143)
- Gustavo Santos (64167)

Descrição:
Implementa a lógica de negócio do sistema MarketPlace, incluindo a gestão
de categorias, produtos, clientes, carrinhos de compras e encomendas.
"""



from shared.utilities import normalizar_nome
from servidor.categoria import Categoria
from servidor.excepcoes import ExcepcaoSupermercadoCategoriaJaExistente, ExcepcaoSupermercadoProdutoNaoExistenteNoCarrinho
from servidor.excepcoes import ExcepcaoSupermercadoCategoriaNaoExistente
from servidor.excepcoes import ExcepcaoSupermercadoCategoriaTemProduto
from servidor.produto import Produto
from servidor.excepcoes import ExcepcaoSupermercadoProdutoJaExistente
from servidor.excepcoes import ExcepcaoSupermercadoProdutoNaoExistente
from servidor.excepcoes import ExcepcaoSupermercadoClienteNaoExistente
from servidor.excepcoes import ExcepcaoSupermercadoClienteJaExistente
from servidor.excepcoes import ExcepcaoSupermercadoPrecoInvalido
from servidor.excepcoes import ExcepcaoSupermercadoQuantidadeInvalida
from servidor.excepcoes import ExcepcaoSupermercadoCarrinhoVazio
from servidor.cliente import Cliente
from servidor.excepcoes import ExcepcaoSupermercadoEmailJaExistente
from servidor.encomenda import Encomenda
from datetime import datetime


class Loja:

    def __init__(self):
        self._categorias = {}
        self._produtos = {}
        self._clientes = {}
        self._carrinhos = {}
        self._encomendas = {}

    def reset(): 
        Categoria._contador_global = 1
        Produto._contador_global = 1
        Cliente._contador_global = 1
        Encomenda._contador_global = 1
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
            return "Sem Categorias"
        
        # total de produtos, nº total de produtos que estão registados
        prod_total = len(self._produtos)

        linhas = []
        linhas.append(f"Total Categorias: {len(self._categorias)}")
        linhas.append(f"Total Produtos: {prod_total}")

        # ordena por id_categoria
        for id_categoria in sorted(self._categorias.keys()):
            categoria = self._categorias[id_categoria]
            n_prod_categoria = self._numero_produtos_categoria(id_categoria)
            linhas.append(f"{categoria.id} - {categoria.nome} ({n_prod_categoria} produtos);")

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
        if quantidade <= 0:
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
        if delta_quantidade <= 0:
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
            return "Sem Clientes"
        
        linhas = []
        linhas.append(f"Total Clientes: {len(self._clientes)}")
        for id_cliente in sorted(self._clientes.keys()):
            c = self._clientes[id_cliente]
            linhas.append(f"{c.id} - {c.nome} ({c.email});")
        
        return "\n".join(linhas)
    
    # -----------------------------
    # Carrinho
    # -----------------------------

    def adiciona_produto_carrinho(self, id_cliente, nome_produto, quantidade):
        if id_cliente not in self._clientes:
            raise ExcepcaoSupermercadoClienteNaoExistente()

        id_produto = self.obter_produto_id(nome_produto)
        if id_produto is None:
            raise ExcepcaoSupermercadoProdutoNaoExistente(nome_produto)
        
        produto = self._produtos[id_produto]

        try:
            quantidade = int(quantidade)
        except (ValueError, TypeError):
            raise ExcepcaoSupermercadoQuantidadeInvalida()

        if quantidade <= 0:
            raise ExcepcaoSupermercadoQuantidadeInvalida()
        
        if produto.quantidade < quantidade:
            raise ExcepcaoSupermercadoQuantidadeInvalida()
        
        produto.quantidade -= quantidade

        if id_cliente not in self._carrinhos:
            self._carrinhos[id_cliente] = {}
        
        self._carrinhos[id_cliente][id_produto] = self._carrinhos[id_cliente].get(id_produto, 0) + quantidade
        return f"Produto {produto.nome} adicionado ao carrinho."

    def remover_produto_carrinho(self, id_cliente, nome_produto):
        if id_cliente not in self._clientes:
            raise ExcepcaoSupermercadoClienteNaoExistente

        id_produto = self.obter_produto_id(nome_produto)
        if id_produto is None or id_produto not in self._carrinhos.get(id_cliente, {}):
            raise ExcepcaoSupermercadoProdutoNaoExistenteNoCarrinho()

        # Devolver stock
        qtd_no_carrinho = self._carrinhos[id_cliente][id_produto]
        self._produtos[id_produto].quantidade += qtd_no_carrinho
        
        del self._carrinhos[id_cliente][id_produto]
        return f"Produto {nome_produto} removido do carrinho."

    def listar_carrinho(self, id_cliente):
        if id_cliente not in self._clientes:
            raise ExcepcaoSupermercadoClienteNaoExistente
        
        if id_cliente not in self._carrinhos or not self._carrinhos[id_cliente]:
            return "Carrinho Vazio"

        carrinho = self._carrinhos[id_cliente]
        valor_total = 0
        linhas = []
        
        for id_prod in sorted(carrinho.keys()):
            prod = self._produtos[id_prod]
            qtd = carrinho[id_prod]
            subtotal = prod.preco * qtd
            valor_total += subtotal
            
            linhas.append(f"{id_prod} - {prod.nome} ({prod.id_categoria}-{prod.nome_categoria}, {prod.preco:.2f} euros, {qtd} unidades);")

        resultado = [f"Total Produtos: {len(carrinho)}\n" f"Total Quantidade: {sum(carrinho.values())}\n" f"Total Preço: {valor_total:.2f} euros\n"]
        resultado.extend(linhas)
        
        return "\n".join(resultado)

    def checkout_carrinho(self, id_cliente):
        if id_cliente not in self._carrinhos or not self._carrinhos[id_cliente]:
            raise ExcepcaoSupermercadoCarrinhoVazio
        
        carrinho = self._carrinhos[id_cliente]
        valor_total = 0
        contagem_categorias = {}

        for id_prod, qtd in carrinho.items():
            prod = self._produtos[id_prod]
            valor_total += prod.preco * qtd
            contagem_categorias[prod.nome_categoria] = contagem_categorias.get(prod.nome_categoria, 0) + qtd

        max_qtd = max(contagem_categorias.values())
        tops = sorted([cat for cat, q in contagem_categorias.items() if q == max_qtd])
        categoria_top = ", ".join(tops)

        data_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        nova_encomenda = Encomenda(id_cliente, carrinho.copy(), round(valor_total, 2), data_atual, categoria_top)
        
        self._encomendas[nova_encomenda.id] = nova_encomenda
        self._carrinhos[id_cliente] = {}
        
        return f"Checkout de carrinho de compras efetuado com sucesso. Encomenda criada com sucesso a partir do carrinho."
    
    def listar_encomendas_cliente(self, id_cliente):
        if id_cliente not in self._clientes:
            raise ExcepcaoSupermercadoClienteNaoExistente

        encomendas_do_cliente = []
        for enc in self._encomendas.values():
            if enc.id_cliente == id_cliente:
                encomendas_do_cliente.append(enc)

        if not encomendas_do_cliente:
            return "Sem Encomendas"

        cliente = self._clientes[id_cliente]
        total_gasto = sum(enc.valor_total for enc in encomendas_do_cliente)
        
        produtos_distintos = set()
        for enc in encomendas_do_cliente:
            produtos_distintos.update(enc.produtos.keys())

        linhas = []
        linhas.append(f"Cliente: {cliente.nome} {cliente.email}")
        linhas.append(f"Total Encomendas: {len(encomendas_do_cliente)}")
        linhas.append(f"Total Produtos: {len(produtos_distintos)}")
        linhas.append(f"Total Preço: {total_gasto:.2f} euros")
        linhas.append(f"Categorias Top: {encomendas_do_cliente[0].categoria_top}")
        linhas.append("-" * 30)

        for enc in sorted(encomendas_do_cliente, key=lambda x: x.id):

            total_quantidade = sum(enc.produtos.values())

            linhas.append(f"ID Encomenda: {enc.id}")
            linhas.append(f"Total Produtos: {len(enc.produtos)}")
            linhas.append(f"Total Quantidade: {total_quantidade}")
            linhas.append(f"Total Preço: {enc.valor_total:.2f} euros")
            
            for p_id, qtd in sorted(enc.produtos.items()):
                p = self._produtos[p_id]
                linhas.append(f"{p.id} - {p.nome} ({p.nome_categoria}, {p.preco:.2f} euros, {qtd} unidades);")
            linhas.append("-" * 10)

        return "\n".join(linhas)
    
    

    