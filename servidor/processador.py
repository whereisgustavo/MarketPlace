"""
AD - Aplicações Distribuídas
Ano Letivo 2025/2026
Projeto - Fase 2

Grupo: 39

Elementos do Grupo:
- Diogo Silva (64143)
- Gustavo Santos (64167)

Descrição:
Camada de interpretação de comandos em protocolo TEXTO.
Usada diretamente pelos testes unitários.
"""

import shlex
from servidor.excepcoes import ExcepcaoComandoInvalido
from servidor.excepcoes import ExcepcaoComandoDesconhecido
from servidor.excepcoes import ExcepcaoComandoNumeroArgumentosIncorreto
from servidor.excepcoes import ExcepcaoSupermercado
from servidor.excepcoes import ExcepcaoComandoNaoInterpretavel
from servidor.excepcoes import ExcepcaoComandoVazio
from servidor.loja import Loja
from servidor.categoria import Categoria
from servidor.produto import Produto
from servidor.cliente import Cliente
from servidor.encomenda import Encomenda


class Processador:

    def __init__(self):
        self.loja = Loja()

        # Tabela de despacho: mapeia nome do comando -> metodo handler
        # Permite adicionar novos comandos sem alterar processar_comando()
        self.HANDLERS = {
            "CRIA_CATEGORIA": self._cmd_cria_categoria,
            "LISTA_CATEGORIAS": self._cmd_lista_categorias,
            "REMOVE_CATEGORIA": self._cmd_remove_categoria,
            "CRIA_PRODUTO": self._cmd_cria_produto,
            "LISTA_PRODUTOS": self._cmd_lista_produtos,
            "AUMENTA_STOCK_PRODUTO": self._cmd_aumenta_stock_produto,
            "ATUALIZA_PRECO_PRODUTO": self._cmd_atualiza_preco_produto,
            "CRIA_CLIENTE": self._cmd_cria_cliente,
            "LISTA_CLIENTES": self._cmd_lista_clientes,
            "ADICIONA_PRODUTO_CARRINHO": self._cmd_adiciona_carrinho,
            "REMOVE_PRODUTO_CARRINHO": self._cmd_remove_carrinho,
            "LISTA_CARRINHO": self._cmd_lista_carrinho,
            "CHECKOUT_CARRINHO": self._cmd_checkout,
            "LISTA_ENCOMENDAS": self._cmd_lista_encomendas,
            "EXIT": self._cmd_sai_aplicacao,
        }

    def reset(self):
        """Repõe o estado da loja para zero. Usado pelos testes unitarios."""
        self.loja.reset()

    # ------------------------------------------------------------------
    # Parsing do protocolo texto
    # ------------------------------------------------------------------

    def _dividir_comando(self, comando):
        """Divide a string de comando em nome + lista de argumentos.
        Usa shlex.split para respeitar argumentos entre aspas
        Lança exceção se o comando estiver vazio ou for não for possivel interpretar."""
        try:
            partes = shlex.split(comando)
        except ValueError:
            raise ExcepcaoComandoNaoInterpretavel(comando)

        if len(partes) == 0:
            raise ExcepcaoComandoVazio()
        elif len(partes) == 1:
            return partes[0].upper(), []   # comando sem argumentos
        else:
            return partes[0].upper(), partes[1:]

    def _validar_n_args(self, args, n):
        """Verifica que foram fornecidos n argumentos.
        Lança excepção com o numero esperado e o recebido."""
        if len(args) != n:
            raise ExcepcaoComandoNumeroArgumentosIncorreto(n, len(args))

    def _obter_handler(self, nome):
        """Procura o handler para um dado nome de comando.
        Lança ExcepcaoComandoDesconhecido se o comando não existir."""
        try:
            return self.HANDLERS[nome]
        except KeyError:
            raise ExcepcaoComandoDesconhecido(nome)

    # ------------------------------------------------------------------
    # Ponto de entrada principal
    # ------------------------------------------------------------------

    def processar_comando(self, comando):
        """Recebe uma string de comando, processa-a e devolve a resposta
        no formato protocolo texto:
          "OK; <mensagem>"   em caso de sucesso
          "NOK; <mensagem>"  em caso de erro"""
        try:
            nome_comando, args = self._dividir_comando(comando)
            handler = self._obter_handler(nome_comando)
            resultado = handler(args)
            return f"OK; {resultado}"
        except (ExcepcaoSupermercado, ExcepcaoComandoInvalido) as e:
            return f"NOK; {e}"

    # ------------------------------------------------------------------
    # Handlers - Categorias
    # ------------------------------------------------------------------

    def _cmd_cria_categoria(self, args):
        self._validar_n_args(args, 1)
        categoria = self.loja.criar_categoria(args[0])
        return f"Categoria {categoria.nome} criada com sucesso."

    def _cmd_lista_categorias(self, args):
        self._validar_n_args(args, 0)
        categorias, produtos = self.loja.listar_categorias()
        if not categorias:
            return "Sem Categorias"
        linhas = []
        linhas.append(f"Total Categorias: {len(categorias)}")
        linhas.append(f"Total Produtos: {len(produtos)}")
        for cat in categorias:
            n_prod = self.loja._numero_produtos_categoria(cat.id_categoria)
            linhas.append(f"{cat.id_categoria} - {cat.nome} ({n_prod} produtos);")
        return "\n".join(linhas)

    def _cmd_remove_categoria(self, args):
        self._validar_n_args(args, 1)
        categoria = self.loja.remover_categoria(args[0])
        return f"Categoria {categoria.nome} removida com sucesso."

    # ------------------------------------------------------------------
    # Handlers - Produtos
    # ------------------------------------------------------------------

    def _cmd_cria_produto(self, args):
        self._validar_n_args(args, 4)
        produto = self.loja.criar_produto(args[0], args[1], args[2], args[3])
        return f"Produto {produto.nome} criado com sucesso."

    def _cmd_lista_produtos(self, args):
        self._validar_n_args(args, 0)
        categorias, produtos = self.loja.listar_produtos()
        if not produtos:
            return "Sem Produtos."
        quantidade_total = sum(p.quantidade for p in produtos)
        linhas = []
        linhas.append(f"Total Produtos: {len(produtos)}")
        linhas.append(f"Total Quantidade: {quantidade_total}")
        for p in produtos:
            linhas.append(
                f"{p.id_produto} - {p.nome} ({p.categoria}, {p.preco:.2f} euros, {p.quantidade} unidades);"
            )
        return "\n".join(linhas)

    def _cmd_aumenta_stock_produto(self, args):
        self._validar_n_args(args, 2)
        delta   = args[1]
        produto = self.loja.aumentar_stock_produto(args[0], delta)
        return f"Stock do produto {produto.nome} aumentado em {delta} unidades com sucesso."

    def _cmd_atualiza_preco_produto(self, args):
        self._validar_n_args(args, 2)
        produto = self.loja.atualizar_preco(args[0], args[1])
        return f"O preço do produto {produto.nome} foi atualizado para {produto.preco:.2f} com sucesso."

    # ------------------------------------------------------------------
    # Handlers - Clientes
    # ------------------------------------------------------------------

    def _cmd_cria_cliente(self, args):
        self._validar_n_args(args, 3)
        cliente = self.loja.criar_cliente(args[0], args[1], args[2])
        return f"Cliente criado com sucesso com identificador único {cliente.id_cliente}."

    def _cmd_lista_clientes(self, args):
        self._validar_n_args(args, 0)
        clientes = self.loja.listar_clientes()
        if not clientes:
            return "Sem Clientes"
        linhas = [f"Total Clientes: {len(clientes)}"]
        for c in clientes:
            linhas.append(f"{c.id_cliente} - {c.nome} ({c.email});")
        return "\n".join(linhas)

    # ------------------------------------------------------------------
    # Handlers - Carrinho (id_cliente é arg explicito)
    # ------------------------------------------------------------------

    def _cmd_adiciona_carrinho(self, args):
        # No protocolo texto o id_cliente vem no comando
        self._validar_n_args(args, 3)
        produto = self.loja.adiciona_produto_carrinho(int(args[0]), args[1], int(args[2]))
        return f"Produto {produto.nome} adicionado com sucesso ao carrinho."

    def _cmd_remove_carrinho(self, args):
        self._validar_n_args(args, 2)
        produto = self.loja.remover_produto_carrinho(int(args[0]), args[1])
        return f"Produto {produto.nome} removido com sucesso do carrinho de compras."

    def _cmd_lista_carrinho(self, args):
        self._validar_n_args(args, 1)
        categorias, produtos = self.loja.listar_carrinho(int(args[0]))
        if not produtos:
            return "Carrinho Vazio"
        total_qtd = sum(p.quantidade for p in produtos)
        total_preco = sum(round(p.preco, 2) * p.quantidade for p in produtos)
        linhas = []
        linhas.append(f"Total Produtos: {len(produtos)}")
        linhas.append(f"Total Quantidade: {total_qtd}")
        linhas.append(f"Total Preço: {round(total_preco, 2):.2f} euros")
        for p in produtos:
            linhas.append(
                f"{p.id_produto} - {p.nome} ({p.id_categoria}-{p.categoria}, "
                f"{p.preco:.2f} euros, {p.quantidade} unidades);"
            )
        return "\n".join(linhas)

    def _cmd_checkout(self, args):
        self._validar_n_args(args, 1)
        self.loja.checkout_carrinho(int(args[0]))
        return ("Checkout de carrinho de compras efetuado com sucesso. "
                "Encomenda criada com sucesso a partir do carrinho.")

    # ------------------------------------------------------------------
    # Handlers - Encomendas
    # ------------------------------------------------------------------

    def _cmd_lista_encomendas(self, args):
        self._validar_n_args(args, 1)
        cliente, encomendas, prods_por_encomenda = self.loja.listar_encomendas_cliente(int(args[0]))

        if not encomendas:
            return "Sem Encomendas"

        total_gasto = sum(enc.total_preco for enc in encomendas)
        produtos_distintos = set()
        for enc in encomendas:
            produtos_distintos.update(enc.produtos.keys())

        # Calcula a categoria top global (todas as encomendas do cliente)
        contagem = {}
        for enc in encomendas:
            for p_id, qtd in enc.produtos.items():
                cat = self.loja._produtos[p_id].categoria
                contagem[cat] = contagem.get(cat, 0) + qtd
        max_q = max(contagem.values())
        tops = sorted([c for c, q in contagem.items() if q == max_q])
        cat_top_str = ", ".join(tops)

        linhas = []
        linhas.append(f"Cliente: {cliente.nome} {cliente.email}")
        linhas.append(f"Total Encomendas: {len(encomendas)}")
        linhas.append(f"Total Produtos: {len(produtos_distintos)}")
        linhas.append(f"Total Preço: {round(total_gasto, 2):.2f} euros")
        linhas.append(f"Categoria Top: {cat_top_str}")
        linhas.append("-" * 74)

        for i, enc in enumerate(encomendas):
            prods = prods_por_encomenda[i]
            total_qtd = sum(p.quantidade for p in prods)
            linhas.append(f"ID Encomenda: {enc.id_encomenda}")
            linhas.append(f"Data Encomenda: {enc.data}")
            linhas.append(f"Total Produtos: {len(prods)}")
            linhas.append(f"Total Quantidade: {total_qtd}")
            linhas.append(f"Total Preço: {enc.total_preco:.2f} euros")
            for p in prods:
                linhas.append(
                    f"{p.id_produto} - {p.nome} ({p.categoria}, "
                    f"{p.preco:.2f} euros, {p.quantidade} unidades);"
                )

        return "\n".join(linhas)

    def _cmd_sai_aplicacao(self, args):
        self._validar_n_args(args, 0)
        return "A fechar."
