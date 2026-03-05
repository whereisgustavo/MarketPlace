class Cliente:
    _contador_global = 1

    def __init__(self, nome, email, password):
        self.id = Cliente._contador_global
        Cliente._contador_global += 1

        self.nome = nome
        self.email = email
        self.password = password