MarketPlace – 1ª Fase
Descrição

Este projeto implementa um sistema distribuído cliente/servidor denominado MarketCenter, que simula uma plataforma simples de comércio eletrónico.

A aplicação permite gerir:

Categorias de produtos

Produtos

Clientes

Carrinhos de compras

Encomendas

O cliente comunica com o servidor através de sockets TCP, enviando comandos de texto que são interpretados e processados pelo servidor.

Todas as respostas do servidor seguem o protocolo:

    OK; <mensagem>

    ou

    NOK; <mensagem de erro>

Arquitetura do Projeto

    O projeto está dividido em três camadas principais:

    Camada Cliente
        Responsável pela interação com o utilizador e envio de comandos ao servidor.

    Camada Transporte
        Responsável pela comunicação entre cliente e servidor através de sockets TCP.

    Camada Processador
        Responsável por:

            interpretar os comandos recebidos
            validar argumentos
            executar a lógica do sistema
        devolver respostas formatadas

Estrutura do Projeto
MarketPlace
    cliente 
        main.py
        rede.py
    
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
    
    shared
        __init__.py
        excepcoes.py
        socket_utilities.py
        utilities.py

    READ_ME.txt
    testes.py

Requisitos

Para executar o projeto é necessário:

    Python 3.x (Recomendado: Python 3.8 ou superior)

Terminal ou Visual Studio Code

Como Executar o Projeto

Todos os comandos devem ser executados na pasta raiz do projeto.

Iniciar o Servidor

No terminal:

    python -m servidor.main <porto>
    Exemplo:

        python -m servidor.main 5000

O servidor ficará à espera de ligações de clientes.

Iniciar o Cliente

Abrir outro terminal e executar:

    python -m cliente.main <porto>
    Exemplo:

        python -m cliente.main 5000

Depois disso o cliente permitirá introduzir comandos que serão enviados ao servidor.

Exemplos de Comandos
Criar categoria
CRIA_CATEGORIA "Bebids"

Nota:
Se o nome contiver espaços, deve ser colocado entre aspas.

Criar produto
CRIA_PRODUTO "Agua Mineral" Bebidas 0.95 30
Listar produtos
LISTA_PRODUTOS
Criar cliente
CRIA_CLIENTE "Maria Silva" maria@email.com 1234
Adicionar produto ao carrinho
ADICIONA_PRODUTO_CARRINHO 1 "Agua Mineral" 2
Listar carrinho
LISTA_CARRINHO 1
Checkout do carrinho
CHECKOUT_CARRINHO 1
Listar encomendas
LISTA_ENCOMENDAS 1
Testes Automáticos

O projeto inclui um ficheiro de testes unitários.

Para executar os testes:

    python -m unittest testes.py

Nota importante:
O ficheiro testes.py não deve ser alterado, pois é utilizado para validação automática.

Notas Importantes

Os dados são mantidos apenas em memória.

O servidor assume apenas um cliente de cada vez.

Não existe persistência de dados nesta fase.

A comunicação entre cliente e servidor é feita através de TCP sockets.

Recomendações

Execute sempre os comandos a partir da pasta raiz do projeto.

Utilize o formato:

python -m ...

para evitar problemas com imports entre módulos.

Autores

Projeto desenvolvido no âmbito da unidade curricular Aplicações Distribuídas.