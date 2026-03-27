"""
AD - Aplicações Distribuídas
Ano Letivo 2025/2026
Projeto - Fase 2

Grupo: 39

Elementos do Grupo:
- Diogo Silva (64143)
- Gustavo Santos (64167)

Descrição:
Processador do cliente.

Padrão:
  processador = Processador(HOST, PORT, PERFIL, ID_UTILIZADOR)
  resposta = processador.processa(msg)
  processador.close()

Internamente:
  1. Gere a ligação TCP (via TCPSocketCliente)
  2. Cria o Stub (proxy RPC)
  3. processa(msg) — parse da string -> routing -> chamada ao Stub -> formatação
"""

import shlex
from shared.socket_utilities import PontoAcesso
from shared.utilities import normalizar_nome
from cliente.rede import TCPSocketCliente
from cliente.stub import Stub


def _e_sucesso(op_code):
    return 20000 <= op_code <= 29999


def _nok(dados):
    msg = dados[0] if dados else "Erro desconhecido."
    return f"NOK; {msg}"


class Processador:

    def __init__(self, host, porto, id_perfil, id_utilizador):
        """Liga ao servidor e cria o Stub para esta sessão."""
        ponto_acesso = PontoAcesso(endereco_ip=host, porto=porto)
        self.rede = TCPSocketCliente(ponto_acesso)
        self.rede.conectar()
        self.stub = Stub(self.rede, id_perfil, id_utilizador)

    def processa(self, msg):
        """Recebe uma linha de texto, envia ao servidor via Stub e devolve a resposta formatada."""
        try:
            partes = shlex.split(msg.strip())
        except ValueError as e:
            return f"NOK; Comando inválido: {e}"

        if not partes:
            return None

        cmd = partes[0].upper()
        args = partes[1:]

        # ------------------------------------------------------------------
        # Categorias
        # ------------------------------------------------------------------
        if cmd == "CRIA_CATEGORIA":
            if len(args) != 1:
                return "NOK; Uso: CRIA_CATEGORIA <nome>"
            op, dados = self.stub.cria_categoria(args[0])
            return f"OK; Categoria {dados[0].nome} criada com sucesso." if _e_sucesso(op) else _nok(dados)

        if cmd == "LISTA_CATEGORIAS":
            op, dados = self.stub.lista_categorias()
            if not _e_sucesso(op):
                return _nok(dados)
            categorias, produtos = dados[0], dados[1]
            if not categorias:
                return "OK; Sem Categorias"
            linhas = [f"Total Categorias: {len(categorias)}", f"Total Produtos: {len(produtos)}"]
            for cat in sorted(categorias, key=lambda c: c.id_categoria):
                n = sum(1 for p in produtos if p.id_categoria == cat.id_categoria)
                linhas.append(f"{cat.id_categoria} - {cat.nome} ({n} produtos);")
            return "OK; " + "\n".join(linhas)

        if cmd == "REMOVE_CATEGORIA":
            if len(args) != 1:
                return "NOK; Uso: REMOVE_CATEGORIA <nome>"
            op, dados = self.stub.remove_categoria(args[0])
            return f"OK; Categoria {normalizar_nome(args[0])} removida com sucesso." if _e_sucesso(op) else _nok(dados)

        # ------------------------------------------------------------------
        # Produtos
        # ------------------------------------------------------------------
        if cmd == "CRIA_PRODUTO":
            if len(args) != 4:
                return "NOK; Uso: CRIA_PRODUTO <nome> <categoria> <preco> <quantidade>"
            try:
                op, dados = self.stub.cria_produto(args[0], args[1], float(args[2]), int(args[3]))
            except ValueError:
                return "NOK; Preço e quantidade devem ser numéricos."
            return f"OK; Produto {dados[0].nome} criado com sucesso." if _e_sucesso(op) else _nok(dados)

        if cmd == "LISTA_PRODUTOS":
            op, dados = self.stub.lista_produtos()
            if not _e_sucesso(op):
                return _nok(dados)
            _, produtos = dados[0], dados[1]
            if not produtos:
                return "OK; Sem Produtos."
            linhas = [f"Total Produtos: {len(produtos)}", f"Total Quantidade: {sum(p.quantidade for p in produtos)}"]
            for p in sorted(produtos, key=lambda x: x.id_produto):
                linhas.append(f"{p.id_produto} - {p.nome} ({p.categoria}, {p.preco:.2f} euros, {p.quantidade} unidades);")
            return "OK; " + "\n".join(linhas)

        if cmd == "AUMENTA_STOCK_PRODUTO":
            if len(args) != 2:
                return "NOK; Uso: AUMENTA_STOCK_PRODUTO <nome> <delta>"
            try:
                op, dados = self.stub.aumenta_stock(args[0], int(args[1]))
            except ValueError:
                return "NOK; Delta deve ser inteiro."
            return f"OK; Stock do produto {dados[0].nome} aumentado em {args[1]} unidades com sucesso." if _e_sucesso(op) else _nok(dados)

        if cmd == "ATUALIZA_PRECO_PRODUTO":
            if len(args) != 2:
                return "NOK; Uso: ATUALIZA_PRECO_PRODUTO <nome> <novo_preco>"
            try:
                op, dados = self.stub.atualiza_preco(args[0], float(args[1]))
            except ValueError:
                return "NOK; Preço deve ser numérico."
            return f"OK; O preço do produto {dados[0].nome} foi atualizado para {dados[0].preco:.2f} com sucesso." if _e_sucesso(op) else _nok(dados)

        # ------------------------------------------------------------------
        # Clientes
        # ------------------------------------------------------------------
        if cmd == "CRIA_CLIENTE":
            if len(args) != 3:
                return "NOK; Uso: CRIA_CLIENTE <nome> <email> <password>"
            op, dados = self.stub.cria_cliente(args[0], args[1], args[2])
            return f"OK; Cliente criado com sucesso com identificador único {dados[0].id_cliente}." if _e_sucesso(op) else _nok(dados)

        if cmd == "LISTA_CLIENTES":
            op, dados = self.stub.lista_clientes()
            if not _e_sucesso(op):
                return _nok(dados)
            clientes = dados[0]
            if not clientes:
                return "OK; Sem Clientes"
            linhas = [f"Total Clientes: {len(clientes)}"]
            for c in sorted(clientes, key=lambda x: x.id_cliente):
                linhas.append(f"{c.id_cliente} - {c.nome} ({c.email});")
            return "OK; " + "\n".join(linhas)

        # ------------------------------------------------------------------
        # Carrinho (id_cliente vem da sessão, não dos args)
        # ------------------------------------------------------------------
        if cmd == "ADICIONA_PRODUTO_CARRINHO":
            if len(args) != 2:
                return "NOK; Uso: ADICIONA_PRODUTO_CARRINHO <nome_produto> <quantidade>"
            try:
                op, dados = self.stub.adiciona_produto_carrinho(args[0], int(args[1]))
            except ValueError:
                return "NOK; Quantidade deve ser inteira."
            return f"OK; Produto {dados[0].nome} adicionado com sucesso ao carrinho." if _e_sucesso(op) else _nok(dados)

        if cmd == "REMOVE_PRODUTO_CARRINHO":
            if len(args) != 1:
                return "NOK; Uso: REMOVE_PRODUTO_CARRINHO <nome_produto>"
            op, dados = self.stub.remove_produto_carrinho(args[0])
            return f"OK; Produto {dados[0].nome} removido com sucesso do carrinho de compras." if _e_sucesso(op) else _nok(dados)

        if cmd == "LISTA_CARRINHO":
            op, dados = self.stub.lista_carrinho()
            if not _e_sucesso(op):
                return _nok(dados)
            _, produtos = dados[0], dados[1]
            if not produtos:
                return "OK; Carrinho Vazio"
            total_preco = sum(round(p.preco, 2) * p.quantidade for p in produtos)
            linhas = [
                f"Total Produtos: {len(produtos)}",
                f"Total Quantidade: {sum(p.quantidade for p in produtos)}",
                f"Total Preço: {round(total_preco, 2):.2f} euros",
            ]
            for p in sorted(produtos, key=lambda x: x.id_produto):
                linhas.append(f"{p.id_produto} - {p.nome} ({p.id_categoria}-{p.categoria}, {p.preco:.2f} euros, {p.quantidade} unidades);")
            return "OK; " + "\n".join(linhas)

        if cmd == "CHECKOUT_CARRINHO":
            op, dados = self.stub.checkout_carrinho()
            return ("OK; Checkout de carrinho de compras efetuado com sucesso. "
                    "Encomenda criada com sucesso a partir do carrinho.") if _e_sucesso(op) else _nok(dados)

        # ------------------------------------------------------------------
        # Encomendas
        # ------------------------------------------------------------------
        if cmd == "LISTA_ENCOMENDAS":
            if len(args) != 1:
                return "NOK; Uso: LISTA_ENCOMENDAS <id_cliente>"
            try:
                op, dados = self.stub.lista_encomendas(int(args[0]))
            except ValueError:
                return "NOK; id_cliente deve ser inteiro."
            if not _e_sucesso(op):
                return _nok(dados)
            cliente, encomendas, prods_por_encomenda = dados[0], dados[1], dados[2]
            if not encomendas:
                return "OK; Sem Encomendas"
            produtos_distintos = set()
            for enc in encomendas:
                produtos_distintos.update(enc.produtos.keys())
            contagem = {}
            for i, enc in enumerate(encomendas):
                for p in prods_por_encomenda[i]:
                    contagem[p.categoria] = contagem.get(p.categoria, 0) + p.quantidade
            max_q = max(contagem.values())
            cat_top = ", ".join(sorted(c for c, q in contagem.items() if q == max_q))
            linhas = [
                f"Cliente: {cliente.nome} {cliente.email}",
                f"Total Encomendas: {len(encomendas)}",
                f"Total Produtos: {len(produtos_distintos)}",
                f"Total Preço: {round(sum(e.total_preco for e in encomendas), 2):.2f} euros",
                f"Categoria Top: {cat_top}",
                "-" * 74,
            ]
            for i, enc in enumerate(encomendas):
                prods = prods_por_encomenda[i]
                linhas += [
                    f"ID Encomenda: {enc.id_encomenda}",
                    f"Data Encomenda: {enc.data}",
                    f"Total Produtos: {len(prods)}",
                    f"Total Quantidade: {sum(p.quantidade for p in prods)}",
                    f"Total Preço: {enc.total_preco:.2f} euros",
                ]
                for p in prods:
                    linhas.append(f"{p.id_produto} - {p.nome} ({p.categoria}, {p.preco:.2f} euros, {p.quantidade} unidades);")
            return "OK; " + "\n".join(linhas)

        return f"NOK; Comando desconhecido: {cmd}"

    def close(self):
        """Fecha a ligação ao servidor."""
        self.rede.fechar_ligacao()
