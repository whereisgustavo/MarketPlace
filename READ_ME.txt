MarketPlace – 2ª Fase
Descrição

Este projeto implementa um sistema distribuído cliente/servidor denominado MarketCenter, que simula uma plataforma simples de comércio eletrónico.

A aplicação permite gerir:

Categorias de produtos

Produtos

Clientes

Carrinhos de compras

Encomendas

O cliente comunica com o servidor através de sockets TCP usando um protocolo RPC binário (pickle + prefixo de 4 bytes).
As mensagens trocadas seguem o formato: [op_code, args, id_perfil, id_utilizador] (pedido) e [op_code_resp, dados] (resposta).

Arquitetura do Projeto

    O projeto está dividido em três camadas principais:

    Camada Cliente
        main.py: Ponto de entrada; cria o Processador e faz o loop de input
        processador.py: Parse da mensagem, routing, formatação da resposta
        stub.py: Proxy RPC; serializa e envia cada pedido ao servidor
        rede.py: TCPSocketCliente; envia/recebe mensagens pela rede

    Camada Servidor
        main.py: Servidor TCP com select(); aceita múltiplos clientes em simultâneo
        skeleton.py: Desserializa o pedido, valida, chama a Loja, devolve resposta
        loja.py: Lógica de negócio (categorias, produtos, clientes, carrinho, encomendas)
        rede.py: TCPSocketServidor; envia/recebe mensagens pela rede

    Camada Partilhada (shared)
        excepcoes_shared.py: OpCodes (1xxxx pedido, 2xxxx sucesso, 3xxxx erro negócio, 39xxx erro protocolo)
        socket_utilities.py: PontoAcesso, receive_all
        utilities.py: normalizar_nome

Estrutura do Projeto
MarketPlace
    cliente
        __init__.py
        main.py
        processador.py
        rede.py
        stub.py

    servidor
        __init__.py
        categorias.py
        cliente.py
        encomenda.py
        excepcoes.py
        loja.py
        main.py
        processador.py
        produto.py
        rede.py
        skeleton.py

    shared
        __init__.py
        excepcoes_shared.py
        excepcoes.py
        socket_utilities.py
        utilities.py

    READ_ME.txt
    testes.py

Requisitos

Para executar o projeto é necessário:

    Python 3.x (Recomendado: Python 3.8 ou superior)

Terminal (Linux recomendado; servidor usa select() com sys.stdin)

Como Executar o Projeto

Todos os comandos devem ser executados na pasta raiz do projeto.

Iniciar o Servidor

No terminal:

    python -m servidor.main <porto>
    Exemplo:

        python -m servidor.main 5000

O servidor ficará à espera de ligações de clientes. Para terminar, escreva EXIT no terminal do servidor.

Iniciar o Cliente

Abrir outro terminal e executar:

    python -m cliente.main <porto> <id_perfil> <id_utilizador>
    Exemplos:

        # Administrador (perfil 3, utilizador 0)
        python -m cliente.main 5000 3 0

        # Anónimo (perfil 0, utilizador 0) para criar cliente
        python -m cliente.main 5000 0 0

        # Cliente registado (perfil 1, utilizador <id_cliente>)
        python -m cliente.main 5000 1 1

Perfis de Acesso

    0 – Anónimo (pode: CRIA_CLIENTE)
    1 – Registado (pode: carrinho, encomendas)
    2 – Funcionário (pode: categorias, produtos, clientes)
    3 – Administrador (acesso total)

Exemplos de Comandos

Criar categoria (perfil >= 2):
    CRIA_CATEGORIA Bebidas

Criar produto (perfil >= 2):
    CRIA_PRODUTO "Agua Mineral" Bebidas 0.95 30

Listar produtos:
    LISTA_PRODUTOS

Criar cliente (perfil = 0):
    CRIA_CLIENTE "Maria Silva" maria@email.com 1234

Listar clientes (perfil >= 2):
    LISTA_CLIENTES

Adicionar produto ao carrinho (perfil >= 1):
    ADICIONA_PRODUTO_CARRINHO "Agua Mineral" 2

Listar carrinho (perfil >= 1):
    LISTA_CARRINHO

Checkout do carrinho (perfil >= 1):
    CHECKOUT_CARRINHO

Listar encomendas (perfil >= 1):
    LISTA_ENCOMENDAS <id_cliente>

Testes Automáticos

O projeto inclui um ficheiro de testes unitários.

Para executar os testes:

    python -m pytest testes.py -v

ou

    python -m unittest testes.py

Notas Importantes

Os dados são mantidos apenas em memória (sem persistência).

O servidor suporta múltiplos clientes em simultâneo via select().

A comunicação usa pickle com prefixo de 4 bytes (big-endian unsigned int).

O servidor no Linux aceita EXIT via stdin; no Windows esta funcionalidade não está disponível (WinError 10038).

Autores

Diogo Silva (64143)
Gustavo Santos (64167)

Grupo 39 – AD 2025/2026
Projeto desenvolvido no âmbito da unidade curricular Aplicações Distribuídas.