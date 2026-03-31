"""
AD - Aplicações Distribuídas
Ano Letivo 2025/2026
Projeto - Fase 2

Grupo: 39

Elementos do Grupo:
- Diogo Silva (64143)
- Gustavo Santos (64167)

Descrição:
Funções utilitarias partilhadas entre cliente e servidor.
Inclui a normalização de nomes usada para comparar categorias,
produtos e clientes de forma case insensitive e sem espaços redundantes.
"""

import re

# Garante que dois nomes "equivalentes" 
# são sempre guardados e comparados da mesma forma.
# Passos:
#   1. strip(): remove espaços no inicio e no fim
#   2. replace('"'): remove aspas
#   3. re.sub(\s+): colapsa multiplos espaços internos num so
#   4. lower().title(): converte para title case

def normalizar_nome(nome):
    # 1. Remove espaços nas extremidades
    nome = nome.strip()

    # 2. Remove aspas duplas e simples 
    nome = nome.replace('"', '').replace("'", '')

    # 3. Colapsa multiplos espaços consecutivos num único espaço
    nome = re.sub(r'\s+', ' ', nome)

    # 4. Converte para title case
    return nome.lower().title()
