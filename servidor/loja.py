"""
AD - Aplicações Distribuídas
Ano Letivo 2025/2026
Projeto - Fase 2

Grupo: 39

Elementos do Grupo:
- Diogo Silva (64143)
- Gustavo Santos (64167)

Descrição:
Camada de logica de negócio do MarketPlace. 
A classe Loja é o coração do sistema, gere: 
    - categorias 
    - produtos
    - clientes 
    - carrinhos
    - encomendas
Não sabe nada de rede, só recebe dados Python e devolve objectos Python.
"""

import copy
from shared.utilities import normalizar_nome
from servidor.categoria import Categoria
from servidor.produto import Produto
from servidor.cliente import Cliente
from servidor.encomenda import Encomenda
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
from datetime import datetime


class Loja:

    def __init__(self):
        # Dicionarios que funcionam como base de dados em memoria.
        # Chave = ID, Valor = objeto correspondente.
        self._categorias = {} # {id_categoria: Categoria}
        self._produtos = {} # {id_produto: Produto}
        self._clientes = {} # {id_cliente: Cliente}
        self._carrinhos = {} # {id_cliente: {id_produto: quantidade}}
        self._encomendas = {} # {id_encomenda: Encomenda}

    def reset(self):
        """Limpa todo o estado da loja e reinicia os contadores.
        Usado pelos testes unitarios para garantir isolamento entre testes."""
        # Repõe os contadores de ID de todas as classes de dominio
        Categoria._contador_global = 1
        Produto._contador_global = 1
        Cliente._contador_global = 1
        Encomenda._contador_global = 1
        # Limpa dicionarios
        self._categorias = {}
        self._produtos = {}
        self._clientes = {}
        self._carrinhos = {}
        self._encomendas = {}

    # ----------------------------------------------------------
    # CATEGORIAS
    # ----------------------------------------------------------

    def criar_categoria(self, nome):
        """Cria e regista uma nova categoria.
        Lança excepção se já existir uma categoria com o mesmo nome
        (comparação feita após normalização)."""
        nome = normalizar_nome(nome)  # garante Title Case e sem espaços extra

        # Verifica unicidade antes de criar
        if self.obter_id_categoria(nome) is not None:
            raise ExcepcaoSupermercadoCategoriaJaExistente(nome)

        categoria = Categoria(nome)
        # Guarda no dicionario com o seu proprio ID como chave
        self._categorias[categoria.id_categoria] = categoria
        return categoria

    def obter_id_categoria(self, nome):
        """Procura uma categoria pelo nome normalizado.
        Devolve o seu ID se existir, ou None caso contrario."""
        for c in self._categorias.values():
            if nome == c.nome:
                return c.id_categoria
        return None

    def _numero_produtos_categoria(self, id_categoria):
        """(Metodo interno) Conta quantos produtos estão associados
        a uma dada categoria. Usado em LISTA_CATEGORIAS e REMOVE_CATEGORIA."""
        total = 0
        for p in self._produtos.values():
            if p.id_categoria == id_categoria:
                total += 1
        return total

    def listar_categorias(self):
        """Devolve todas as categorias e todos os produtos ordenados por ID.
        O Processador/Stub usa estas listas para o output."""
        categorias = sorted(self._categorias.values(), key=lambda c: c.id_categoria)
        produtos = sorted(self._produtos.values(), key=lambda p: p.id_produto)
        return (categorias, produtos)

    def remover_categoria(self, nome):
        """Remove uma categoria do sistema.
        Regra: a categoria tem de existir e não pode ter produtos com stock > 0."""
        nome_normalizado = normalizar_nome(nome)
        id_categoria = self.obter_id_categoria(nome_normalizado)

        if id_categoria is None:
            raise ExcepcaoSupermercadoCategoriaNaoExistente(nome_normalizado)

        # Não permite remover se existirem produtos associados com stock
        if self._numero_produtos_categoria(id_categoria) > 0:
            raise ExcepcaoSupermercadoCategoriaTemProduto(nome_normalizado)

        categoria = self._categorias[id_categoria]
        del self._categorias[id_categoria]
        return categoria

    # ----------------------------------------------------------
    # PRODUTOS
    # ----------------------------------------------------------

    def obter_produto_id(self, nome_produto):
        """Procura um produto pelo nome normalizado.
        Devolve o seu ID se existir, ou None caso contrario."""
        nome_normalizado = normalizar_nome(nome_produto)
        for p in self._produtos.values():
            if p.nome == nome_normalizado:
                return p.id_produto
        return None

    def criar_produto(self, nome_produto, nome_categoria, preco, quantidade):
        """Cria e regista um novo produto associado a uma categoria existente.
        Valida: nome unico, categoria existente, preço > 0, quantidade >= 0."""
        nome_produto_normalizado = normalizar_nome(nome_produto)
        nome_categoria_normalizado = normalizar_nome(nome_categoria)

        if self.obter_produto_id(nome_produto_normalizado) is not None:
            raise ExcepcaoSupermercadoProdutoJaExistente(nome_produto_normalizado)

        id_categoria = self.obter_id_categoria(nome_categoria_normalizado)
        if id_categoria is None:
            raise ExcepcaoSupermercadoCategoriaNaoExistente(nome_categoria_normalizado)

        # Validação do preço: tem de ser numerico e positivo
        try:
            preco = float(preco)
        except (ValueError, TypeError):
            raise ExcepcaoSupermercadoPrecoInvalido()
        if preco <= 0:
            raise ExcepcaoSupermercadoPrecoInvalido()

        # Validação da quantidade: tem de ser inteiro e positivo
        try:
            quantidade = int(quantidade)
        except (ValueError, TypeError):
            raise ExcepcaoSupermercadoQuantidadeInvalida()
        if quantidade < 0:
            raise ExcepcaoSupermercadoQuantidadeInvalida()

        produto = Produto(nome_produto_normalizado, id_categoria, nome_categoria_normalizado, preco, quantidade)
        self._produtos[produto.id_produto] = produto
        return produto

    def listar_produtos(self):
        """Devolve todas as categorias e todos os produtos ordenados por ID."""
        categorias = sorted(self._categorias.values(), key=lambda c: c.id_categoria)
        produtos = sorted(self._produtos.values(), key=lambda p: p.id_produto)
        return (categorias, produtos)

    def aumentar_stock_produto(self, nome_produto, delta_quantidade):
        """Aumenta o stock de um produto em delta_quantidade unidades.
        delta_quantidade tem de ser > 0."""
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
        return produto

    def atualizar_preco(self, nome_produto, preco):
        """Atualiza o preço de um produto existente.
        O novo preço tem de ser numerico e maior que zero."""
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
        return produto

    # ----------------------------------------------------------
    # CLIENTES
    # ----------------------------------------------------------

    def criar_cliente(self, nome_cliente, email, password):
        """Regista um novo cliente. O email tem de ser unico no sistema
        (comparação case-insensitive)."""
        nome_cliente_normalizado = normalizar_nome(nome_cliente)

        # Normaliza o email para minusculas antes de verificar unicidade
        email = email.strip()
        email_normalizado = email.lower()

        # Verifica se ja existe um cliente com este email
        for c in self._clientes.values():
            if c.email.lower() == email_normalizado:
                raise ExcepcaoSupermercadoEmailJaExistente(email)

        cliente = Cliente(nome_cliente_normalizado, email_normalizado, password)
        self._clientes[cliente.id_cliente] = cliente
        return cliente

    def listar_clientes(self):
        """Devolve lista de clientes ordenada por ID crescente."""
        return sorted(self._clientes.values(), key=lambda c: c.id_cliente)

    def obter_cliente(self, id_cliente):
        """Devolve o objeto Cliente com o ID dado, ou None se não existir."""
        return self._clientes.get(id_cliente, None)

    # ----------------------------------------------------------
    # CARRINHO
    # ----------------------------------------------------------

    def adiciona_produto_carrinho(self, id_cliente, nome_produto, quantidade):
        """Adiciona um produto ao carrinho de um cliente.

        Regras:
        - O cliente tem de existir
        - O produto tem de existir
        - A quantidade tem de ser inteira e positiva
        - Tem de haver stock suficiente

        Depois:
        - Stock do produto é reduzido imediatamente (fica reservado para este cliente).
        - Se o produto já estava no carrinho, a quantidade é somada."""
        if id_cliente not in self._clientes:
            raise ExcepcaoSupermercadoClienteNaoExistente()

        nome_normalizado = normalizar_nome(nome_produto)
        id_produto = self.obter_produto_id(nome_normalizado)
        if id_produto is None:
            raise ExcepcaoSupermercadoProdutoNaoExistente(nome_normalizado)

        produto = self._produtos[id_produto]

        try:
            quantidade = int(quantidade)
        except (ValueError, TypeError):
            raise ExcepcaoSupermercadoQuantidadeInvalida()
        if quantidade <= 0:
            raise ExcepcaoSupermercadoQuantidadeInvalida()

        # Verifica se ha stock suficiente para esta quantidade
        if produto.quantidade < quantidade:
            raise ExcepcaoSupermercadoStockInsuficiente()

        # Reserva o stock: decrementa o produto em stock
        produto.quantidade -= quantidade

        # Cria o carrinho do cliente se ainda não existir
        if id_cliente not in self._carrinhos:
            self._carrinhos[id_cliente] = {}

        # Adiciona ou acumula a quantidade no carrinho
        self._carrinhos[id_cliente][id_produto] = (
            self._carrinhos[id_cliente].get(id_produto, 0) + quantidade
        )
        return produto

    def remover_produto_carrinho(self, id_cliente, nome_produto):
        """Remove um produto do carrinho e devolve o stock ao produto.

        O produto é removido na totalidade (não é possível remover
        parcialmente). O stock é reposto."""
        if id_cliente not in self._clientes:
            raise ExcepcaoSupermercadoClienteNaoExistente()

        nome_normalizado = normalizar_nome(nome_produto)
        id_produto = self.obter_produto_id(nome_normalizado)

        if id_produto is None:
            raise ExcepcaoSupermercadoProdutoNaoExistente(nome_normalizado)

        # Verifica se o produto está no carrinho do cliente
        if id_cliente not in self._carrinhos or id_produto not in self._carrinhos[id_cliente]:
            raise ExcepcaoSupermercadoProdutoNaoExistenteNoCarrinho()

        # Devolve ao stock a quantidade que estava reservada no carrinho
        qtd_no_carrinho = self._carrinhos[id_cliente][id_produto]
        self._produtos[id_produto].quantidade += qtd_no_carrinho

        # Remove o produto do carrinho
        del self._carrinhos[id_cliente][id_produto]
        return self._produtos[id_produto]

    def listar_carrinho(self, id_cliente):
        """Lista o conteudo do carrinho de um cliente.

        Devolve ([], []) se o carrinho estiver vazio.
        Caso contrario, devolve (categorias, produtos_snapshot) onde
        cada produto_snapshot tem a quantidade do Carrinho (não do stock),
        feito via copy.copy() para não alterar os dados reais."""
        if id_cliente not in self._clientes:
            raise ExcepcaoSupermercadoClienteNaoExistente()

        if id_cliente not in self._carrinhos or not self._carrinhos[id_cliente]:
            return ([], [])

        carrinho = self._carrinhos[id_cliente]

        ids_categorias = set()
        produtos_snapshot = []

        for id_prod in sorted(carrinho.keys()):
            prod = self._produtos[id_prod]
            qtd = carrinho[id_prod]
            ids_categorias.add(prod.id_categoria)

            # copy.copy cria uma copia superficial do produto
            # (todos os campos são imutaveis: int, float, str)
            # Assim podemos alterar a quantidade sem modificar o stock real
            snap = copy.copy(prod)
            snap.quantidade = qtd          # quantidade no carrinho, não no stock
            produtos_snapshot.append(snap)

        # Recolhe os objetos Categoria necessarios para o output
        categorias = []
        for id_cat in sorted(ids_categorias):
            categorias.append(self._categorias[id_cat])

        return (categorias, produtos_snapshot)

    def checkout_carrinho(self, id_cliente):
        """Transforma o carrinho numa Encomenda.

        Passos:
        1. Valida cliente e carrinho não vazio
        2. Calcula o total e a categoria top
        3. Cria a Encomenda com snapshot do carrinho
        4. Esvazia o carrinho
        (O stock não é alterado aqui, ja foi decrementado em adiciona_produto_carrinho)"""
        if id_cliente not in self._clientes:
            raise ExcepcaoSupermercadoClienteNaoExistente()

        if id_cliente not in self._carrinhos or not self._carrinhos[id_cliente]:
            raise ExcepcaoSupermercadoCarrinhoVazio()

        carrinho = self._carrinhos[id_cliente]
        valor_total = 0
        contagem_categorias = {}  # {nome_categoria: total_unidades}

        for id_prod, qtd in carrinho.items():
            prod = self._produtos[id_prod]
            valor_total += round(prod.preco, 2) * qtd
            contagem_categorias[prod.categoria] = (
                contagem_categorias.get(prod.categoria, 0) + qtd
            )

        # Determina a categoria com mais unidades vendidas
        max_qtd = max(contagem_categorias.values())
        tops = sorted([cat for cat, q in contagem_categorias.items() if q == max_qtd])
        categoria_top = ", ".join(tops)  # em casp de empate, ficam separados por virgula

        data_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        nova_encomenda = Encomenda(
            id_cliente,
            carrinho.copy(),           # copia do dicionario para snapshot
            round(valor_total, 2),
            data_atual,
            categoria_top
        )

        self._encomendas[nova_encomenda.id_encomenda] = nova_encomenda

        # Esvazia o carrinho (mas não repoe stock, ja foi reservado)
        self._carrinhos[id_cliente] = {}

        return nova_encomenda

    def listar_encomendas_cliente(self, id_cliente):
        """Lista todas as encomendas de um cliente.

        Devolve um triplo (cliente, encomendas, prods_por_encomenda) onde:
        - cliente : objeto Cliente
        - encomendas : lista de Encomenda ordenada por ID
        - prods_por_encomenda : lista de listas

        Se não houver encomendas, devolve (cliente, [], [])."""
        if id_cliente not in self._clientes:
            raise ExcepcaoSupermercadoClienteNaoExistente()

        encomendas_do_cliente = []
        for enc in self._encomendas.values():
            if enc.id_cliente == id_cliente:
                encomendas_do_cliente.append(enc)

        if not encomendas_do_cliente:
            return (self._clientes[id_cliente], [], [])

        encomendas_ordenadas = sorted(encomendas_do_cliente, key=lambda e: e.id_encomenda)

        # Para cada encomenda, constroi uma lista de snapshots de produto
        # com a quantidade comprada (não o stock atual)
        prods_por_encomenda = []
        for enc in encomendas_ordenadas:
            prods = []
            for p_id, qtd in sorted(enc.produtos.items()):
                snap = copy.copy(self._produtos[p_id])
                snap.quantidade = qtd   # quantidade comprada nesta encomenda
                prods.append(snap)
            prods_por_encomenda.append(prods)

        return (self._clientes[id_cliente], encomendas_ordenadas, prods_por_encomenda)
