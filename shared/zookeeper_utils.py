"""
AD - Aplicações Distribuídas
Ano Letivo 2025/2026
Projeto - Fase 3

Grupo: 39

Elementos do Grupo:
- Diogo Silva (64143)
- Gustavo Santos (64167)

Descrição:
Utilitários partilhados para interação com o ZooKeeper.
Usados tanto pelo servidor como pelo cliente para navegar na cadeia de replicação.

Estrutura no ZooKeeper:
  /chain/node-0000000001  (valor = b'localhost:5000')
  /chain/node-0000000002  (valor = b'localhost:6000')
  ...

Os nós são efémeros e sequenciais. Ordenados lexicograficamente:
  - o primeiro é a cabeça (head)
  - o último é a cauda (tail)
"""

CHAIN_PATH = '/chain'


def ordenar_nos(nos):
    """Ordena os nós da cadeia por ordem lexicográfica (equivale a ordem de sequência)."""
    return sorted(nos)


def obter_head(nos_ordenados):
    """Devolve o nome do nó cabeça (menor sequência), ou None se a cadeia estiver vazia."""
    return nos_ordenados[0] if nos_ordenados else None


def obter_tail(nos_ordenados):
    """Devolve o nome do nó cauda (maior sequência), ou None se a cadeia estiver vazia."""
    return nos_ordenados[-1] if nos_ordenados else None


def obter_sucessor(nos_ordenados, meu_no_nome):
    """Devolve o primeiro nó com sequência maior que meu_no_nome, ou None se não existir.
    Usa comparação de strings (funciona para nomes com zero-padding do ZooKeeper)."""
    posteriores = [n for n in nos_ordenados if n > meu_no_nome]
    return posteriores[0] if posteriores else None


def obter_antecessor(nos_ordenados, meu_no_nome):
    """Devolve o último nó com sequência menor que meu_no_nome, ou None se não existir.
    Usa comparação de strings (funciona para nomes com zero-padding do ZooKeeper)."""
    anteriores = [n for n in nos_ordenados if n < meu_no_nome]
    return anteriores[-1] if anteriores else None


def parse_endereco(dados_bytes):
    """Converte os bytes do ZNode (ip:porto) para um tuplo (ip, porto)."""
    partes = dados_bytes.decode().split(':')
    return partes[0], int(partes[1])
