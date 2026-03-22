"""
AD - Aplicações Distribuídas
Ano Letivo 2025/2026
Projeto - Fase 2

Grupo: 39

Elementos do Grupo:
- Diogo Silva (64143)
- Gustavo Santos (64167)

Descrição:
Contém funções utilitárias utilizadas em várias partes do sistema, como
normalização de nomes e tratamento de strings.
"""


import re

#---------------------------
# Normaliza comando textual
#---------------------------

def normalizar_nome(nome): 
    # remove espaços extremos
    nome = nome.strip()

    nome = nome.replace('"', '').replace("'", '')

    # substitui múltiplos espaços por 1 só
    nome = re.sub(r'\s+', ' ', nome)

    # normaliza capitalização
    return nome.lower().title()