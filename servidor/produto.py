class Produto:
    _contador_global = 1

    def __init__(self, nome, id_categoria, nome_categoria, preco, quantidade):
        self.id = Produto._contador_global
        Produto._contador_global += 1

        self.nome = nome
        self.id_categoria = id_categoria
        self.nome_categoria = nome_categoria

        self.preco = round(preco, 2) # preco com 2 casas decimais
        self.quantidade = quantidade