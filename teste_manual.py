from servidor.processador import Processador


def testar():
    p = Processador()
    p.reset()

    comandos = [
        # -----------------------------
        # CATEGORIAS
        # -----------------------------
        "LISTA_CATEGORIAS",
        'CRIA_CATEGORIA Fruta',
        'CRIA_CATEGORIA "Electrodomésticos Pequenos"',
        'CRIA_CATEGORIA fruta',   # duplicada por normalização
        "LISTA_CATEGORIAS",
        'REMOVE_CATEGORIA Bebidas',   # inexistente

        # -----------------------------
        # PRODUTOS
        # -----------------------------
        'CRIA_CATEGORIA Bebidas',
        'CRIA_PRODUTO "Agua Mineral" Bebidas 0.95 30',
        'CRIA_PRODUTO "Arroz Basmati" Fruta 2.49 15',
        'CRIA_PRODUTO "agua mineral" Bebidas 1.00 10',   # duplicado
        'CRIA_PRODUTO "Coca Cola" Refrigerantes 1.50 10',  # categoria inexistente
        'CRIA_PRODUTO "Leite" Bebidas -1 10',   # preço inválido
        'CRIA_PRODUTO "Sumo" Bebidas 1.20 -5',  # quantidade inválida
        "LISTA_PRODUTOS",

        # -----------------------------
        # STOCK / PREÇO
        # -----------------------------
        'AUMENTA_STOCK_PRODUTO "Agua Mineral" 5',
        'AUMENTA_STOCK_PRODUTO "Agua Mineral" -3',
        'AUMENTA_STOCK_PRODUTO "Produto Inexistente" 2',
        'ATUALIZA_PRECO_PRODUTO "Agua Mineral" 1.10',
        'ATUALIZA_PRECO_PRODUTO "Agua Mineral" -1',
        'ATUALIZA_PRECO_PRODUTO "Produto Inexistente" 2.50',
        "LISTA_PRODUTOS",

        # -----------------------------
        # CLIENTES
        # -----------------------------
        "LISTA_CLIENTES",
        'CRIA_CLIENTE "Maria Silva" maria@email.com 1234',
        'CRIA_CLIENTE "Ana Silva" ana@email.com pass',
        'CRIA_CLIENTE "Outra Pessoa" ANA@email.com abc',  # email duplicado
        "LISTA_CLIENTES",

        # -----------------------------
        # CARRINHO
        # -----------------------------
        'LISTA_CARRINHO 1',
        'ADICIONA_PRODUTO_CARRINHO 1 "Agua Mineral" 2',
        'ADICIONA_PRODUTO_CARRINHO 1 "Agua Mineral" 1',
        'ADICIONA_PRODUTO_CARRINHO 1 "Produto Inexistente" 1',
        'ADICIONA_PRODUTO_CARRINHO 99 "Agua Mineral" 1',
        'ADICIONA_PRODUTO_CARRINHO 1 "Agua Mineral" -1',
        'LISTA_CARRINHO 1',
        'LISTA_CARRINHO 2',

        # -----------------------------
        # REMOVER DO CARRINHO
        # -----------------------------
        'REMOVE_PRODUTO_CARRINHO 1 "Agua Mineral"',
        'REMOVE_PRODUTO_CARRINHO 1 "Agua Mineral"',  # já não está no carrinho
        'LISTA_CARRINHO 1',

        # -----------------------------
        # CHECKOUT
        # -----------------------------
        'ADICIONA_PRODUTO_CARRINHO 1 "Agua Mineral" 2',
        'LISTA_CARRINHO 1',
        'CHECKOUT_CARRINHO 1',
        'CHECKOUT_CARRINHO 1',  # carrinho vazio
        'LISTA_CARRINHO 1',
        "LISTA_PRODUTOS",

        # -----------------------------
        # ENCOMENDAS
        # -----------------------------
        'LISTA_ENCOMENDAS 1',
        'LISTA_ENCOMENDAS 2',
        'LISTA_ENCOMENDAS 99',

        # -----------------------------
        # TESTE REMOVE_CATEGORIA COM PRODUTOS
        # -----------------------------
        'REMOVE_CATEGORIA Bebidas',
        'REMOVE_CATEGORIA "Electrodomésticos Pequenos"',
        "LISTA_CATEGORIAS",
    ]

    for i, comando in enumerate(comandos, start=1):
        print("=" * 80)
        print(f"TESTE {i}")
        print("COMANDO:", comando)
        try:
            resposta = p.processar_comando(comando)
            print("RESPOSTA:")
            print(resposta)
        except Exception as e:
            print("EXCEÇÃO NÃO TRATADA:")
            print(type(e).__name__, "-", e)


if __name__ == "__main__":
    testar()