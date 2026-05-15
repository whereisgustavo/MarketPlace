"""
AD - Aplicações Distribuídas
Ano Letivo 2025/2026
Projeto - Fase 3

Grupo: 39

Elementos do Grupo:
- Diogo Silva (64143)
- Gustavo Santos (64167)

Descrição:
Processador do cliente - Fase 3.

Novidades em relação à Fase 2:
  - Liga ao ZooKeeper para descobrir o head e tail da cadeia
  - Mantém duas ligações SSL: uma ao head (escritas) e outra ao tail (leituras)
  - Watch no ZooKeeper para atualizar as ligações quando a cadeia muda
  - Operações de escrita → stub_head; operações de leitura → stub_tail

Padrão de uso (igual à Fase 2 da perspetiva do main.py):
  processador = Processador(ZK_ADDR, PERFIL, ID_UTILIZADOR)
  resposta = processador.processa(msg)
  processador.close()
"""

import shlex
import threading

from kazoo.client import KazooClient

from shared.socket_utilities import PontoAcesso
from shared.utilities import normalizar_nome
from shared.zookeeper_utils import (
    CHAIN_PATH, ordenar_nos,
    obter_head, obter_tail, parse_endereco
)
from shared.ssl_utils import criar_contexto_cliente as criar_ssl_context_cliente
from cliente.rede import TCPSocketCliente
from cliente.stub import Stub


# Comandos que modificam o estado — enviados para o HEAD da cadeia
CMDS_ESCRITA = {
    'CRIA_CATEGORIA', 'REMOVE_CATEGORIA',
    'CRIA_PRODUTO', 'AUMENTA_STOCK_PRODUTO', 'ATUALIZA_PRECO_PRODUTO',
    'CRIA_CLIENTE',
    'ADICIONA_PRODUTO_CARRINHO', 'REMOVE_PRODUTO_CARRINHO', 'CHECKOUT_CARRINHO',
}


def _e_sucesso(op_code):
    return 20000 <= op_code <= 29999


def _nok(dados):
    msg = dados[0] if dados else "Erro desconhecido."
    return f"NOK; {msg}"


class Processador:

    def __init__(self, zk_addr, id_perfil, id_utilizador):
        self.id_perfil      = id_perfil
        self.id_utilizador  = id_utilizador
        self._lock          = threading.Lock()

        self.ssl_ctx = criar_ssl_context_cliente()

        # Ligar ao ZooKeeper
        self.zk = KazooClient(hosts=zk_addr)
        self.zk.start()
        self.zk.ensure_path(CHAIN_PATH)
        print(f"CLIENTE> Ligado ao ZooKeeper em {zk_addr}")

        # Ligações e stubs (inicializados em _atualizar_chain)
        self._rede_head  = None
        self._rede_tail  = None
        self._stub_head  = None
        self._stub_tail  = None
        self._head_nome  = None
        self._tail_nome  = None

        self._atualizar_chain(self.zk.get_children(CHAIN_PATH))

        # Watch para detetar mudanças na cadeia
        @self.zk.ChildrenWatch(CHAIN_PATH)
        def _watch(children):
            with self._lock:
                self._atualizar_chain(children)

    # ------------------------------------------------------------------
    # Gestão da cadeia
    # ------------------------------------------------------------------

    def _criar_ligacao(self, ip, porto):
        """Cria e estabelece uma ligação SSL a um servidor."""
        rede = TCPSocketCliente(PontoAcesso(endereco_ip=ip, porto=porto), self.ssl_ctx)
        rede.conectar()
        return rede

    def _atualizar_chain(self, children):
        """Obtém head e tail do ZooKeeper e recria as ligações se necessário."""
        nos = ordenar_nos(children)
        if not nos:
            print("CLIENTE> Nenhum servidor disponível na cadeia.")
            return

        novo_head = obter_head(nos)
        novo_tail = obter_tail(nos)

        head_mudou = novo_head != self._head_nome
        tail_mudou = novo_tail != self._tail_nome

        if not head_mudou and not tail_mudou:
            return  # cadeia sem alterações relevantes

        print(f"CLIENTE> Cadeia atualizada — head: {novo_head}, tail: {novo_tail}")

        # Fechar ligações antigas (com cuidado para não fechar a mesma duas vezes)
        if head_mudou and self._rede_head:
            self._rede_head.fechar_ligacao()
            self._rede_head = None
        if tail_mudou and self._rede_tail and self._rede_tail is not self._rede_head:
            self._rede_tail.fechar_ligacao()
            self._rede_tail = None

        # Criar nova ligação ao head (se mudou)
        if head_mudou:
            dados_head, _ = self.zk.get(f'{CHAIN_PATH}/{novo_head}')
            h_ip, h_porto = parse_endereco(dados_head)
            self._rede_head = self._criar_ligacao(h_ip, h_porto)
            self._stub_head = Stub(self._rede_head, self.id_perfil, self.id_utilizador)

        # Criar nova ligação ao tail (se mudou)
        if tail_mudou:
            if novo_tail == novo_head:
                # Servidor único: head e tail são o mesmo
                self._rede_tail = self._rede_head
                self._stub_tail = self._stub_head
            else:
                dados_tail, _ = self.zk.get(f'{CHAIN_PATH}/{novo_tail}')
                t_ip, t_porto = parse_endereco(dados_tail)
                self._rede_tail = self._criar_ligacao(t_ip, t_porto)
                self._stub_tail = Stub(self._rede_tail, self.id_perfil, self.id_utilizador)

        self._head_nome = novo_head
        self._tail_nome = novo_tail

    # ------------------------------------------------------------------
    # Routing: escrita → head, leitura → tail
    # ------------------------------------------------------------------

    def _stub(self, cmd):
        """Devolve o stub correto: head para escritas, tail para leituras."""
        return self._stub_head if cmd in CMDS_ESCRITA else self._stub_tail

    # ------------------------------------------------------------------
    # Processamento de comandos
    # ------------------------------------------------------------------

    def processa(self, msg):
        """Recebe uma linha de texto, envia ao servidor via Stub e devolve a resposta formatada."""
        try:
            partes = shlex.split(msg.strip())
        except ValueError as e:
            return f"NOK; Comando inválido: {e}"

        if not partes:
            return None

        cmd  = partes[0].upper()
        args = partes[1:]

        with self._lock:
            stub = self._stub(cmd)
            if stub is None:
                return "NOK; Sem servidor disponível."
            try:
                return self._executar(cmd, args, stub)
            except TypeError:
                return "NOK; Ligação perdida ao servidor. Tente novamente."
            except Exception as e:
                return f"NOK; Erro inesperado: {e}"

    def _executar(self, cmd, args, stub):
        # ------------------------------------------------------------------
        # Categorias
        # ------------------------------------------------------------------
        if cmd == "CRIA_CATEGORIA":
            if len(args) != 1:
                return "NOK; Uso: CRIA_CATEGORIA <nome>"
            op, dados = stub.cria_categoria(args[0])
            return f"OK; Categoria {dados[0].nome} criada com sucesso." if _e_sucesso(op) else _nok(dados)

        if cmd == "LISTA_CATEGORIAS":
            op, dados = stub.lista_categorias()
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
            op, dados = stub.remove_categoria(args[0])
            return f"OK; Categoria {normalizar_nome(args[0])} removida com sucesso." if _e_sucesso(op) else _nok(dados)

        # ------------------------------------------------------------------
        # Produtos
        # ------------------------------------------------------------------
        if cmd == "CRIA_PRODUTO":
            if len(args) != 4:
                return "NOK; Uso: CRIA_PRODUTO <nome> <categoria> <preco> <quantidade>"
            try:
                op, dados = stub.cria_produto(args[0], args[1], float(args[2]), int(args[3]))
            except ValueError:
                return "NOK; Preço e quantidade devem ser numéricos."
            return f"OK; Produto {dados[0].nome} criado com sucesso." if _e_sucesso(op) else _nok(dados)

        if cmd == "LISTA_PRODUTOS":
            op, dados = stub.lista_produtos()
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
                op, dados = stub.aumenta_stock(args[0], int(args[1]))
            except ValueError:
                return "NOK; Delta deve ser inteiro."
            return f"OK; Stock do produto {dados[0].nome} aumentado em {args[1]} unidades com sucesso." if _e_sucesso(op) else _nok(dados)

        if cmd == "ATUALIZA_PRECO_PRODUTO":
            if len(args) != 2:
                return "NOK; Uso: ATUALIZA_PRECO_PRODUTO <nome> <novo_preco>"
            try:
                op, dados = stub.atualiza_preco(args[0], float(args[1]))
            except ValueError:
                return "NOK; Preço deve ser numérico."
            return f"OK; O preço do produto {dados[0].nome} foi atualizado para {dados[0].preco:.2f} com sucesso." if _e_sucesso(op) else _nok(dados)

        # ------------------------------------------------------------------
        # Clientes
        # ------------------------------------------------------------------
        if cmd == "CRIA_CLIENTE":
            if len(args) != 3:
                return "NOK; Uso: CRIA_CLIENTE <nome> <email> <password>"
            op, dados = stub.cria_cliente(args[0], args[1], args[2])
            return f"OK; Cliente criado com sucesso com identificador único {dados[0].id_cliente}." if _e_sucesso(op) else _nok(dados)

        if cmd == "LISTA_CLIENTES":
            op, dados = stub.lista_clientes()
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
        # Carrinho
        # ------------------------------------------------------------------
        if cmd == "ADICIONA_PRODUTO_CARRINHO":
            if len(args) != 2:
                return "NOK; Uso: ADICIONA_PRODUTO_CARRINHO <nome_produto> <quantidade>"
            try:
                op, dados = stub.adiciona_produto_carrinho(args[0], int(args[1]))
            except ValueError:
                return "NOK; Quantidade deve ser inteira."
            return f"OK; Produto {dados[0].nome} adicionado com sucesso ao carrinho." if _e_sucesso(op) else _nok(dados)

        if cmd == "REMOVE_PRODUTO_CARRINHO":
            if len(args) != 1:
                return "NOK; Uso: REMOVE_PRODUTO_CARRINHO <nome_produto>"
            op, dados = stub.remove_produto_carrinho(args[0])
            return f"OK; Produto {dados[0].nome} removido com sucesso do carrinho de compras." if _e_sucesso(op) else _nok(dados)

        if cmd == "LISTA_CARRINHO":
            op, dados = stub.lista_carrinho()
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
            op, dados = stub.checkout_carrinho()
            return ("OK; Checkout de carrinho de compras efetuado com sucesso. "
                    "Encomenda criada com sucesso a partir do carrinho.") if _e_sucesso(op) else _nok(dados)

        # ------------------------------------------------------------------
        # Encomendas
        # ------------------------------------------------------------------
        if cmd == "LISTA_ENCOMENDAS":
            if len(args) != 1:
                return "NOK; Uso: LISTA_ENCOMENDAS <id_cliente>"
            try:
                op, dados = stub.lista_encomendas(int(args[0]))
            except ValueError:
                return "NOK; id_cliente deve ser inteiro."
            if not _e_sucesso(op):
                return _nok(dados)
            cliente, encomendas, prods_por_encomenda = dados[0], dados[1], dados[2]
            if not encomendas:
                return "OK; Sem Encomendas"
            contagem = {}
            total_quantidade_geral = 0
            for i, enc in enumerate(encomendas):
                for p in prods_por_encomenda[i]:
                    contagem[p.categoria] = contagem.get(p.categoria, 0) + p.quantidade
                    total_quantidade_geral += p.quantidade
            max_q   = max(contagem.values())
            cat_top = ", ".join(sorted(c for c, q in contagem.items() if q == max_q))
            linhas  = [
                f"Cliente: {cliente.nome} {cliente.email}",
                f"Total Encomendas: {len(encomendas)}",
                f"Total Produtos: {total_quantidade_geral}",
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
        """Fecha as ligações ao servidor e ao ZooKeeper."""
        with self._lock:
            if self._rede_head:
                self._rede_head.fechar_ligacao()
            if self._rede_tail and self._rede_tail is not self._rede_head:
                self._rede_tail.fechar_ligacao()
        self.zk.stop()
        self.zk.close()
