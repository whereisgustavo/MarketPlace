"""
AD - Aplicações Distribuídas
Ano Letivo 2025/2026
Projeto - Fase 2

Grupo: 39

Elementos do Grupo:
- Diogo Silva (64143)
- Gustavo Santos (64167)

Descrição:
Funções utilitárias partilhadas entre cliente e servidor.
Inclui a normalização de nomes usada para comparar categorias,
produtos e clientes de forma case-insensitive e sem espaços redundantes.
"""

import re


# -----------------------------------------------------------------------
# normalizar_nome
# -----------------------------------------------------------------------
# Garante que dois nomes "equivalentes" (ex: "fruta", "  Fruta ", "FRUTA")
# são sempre guardados e comparados da mesma forma.
#
# Passos aplicados:
#   1. strip()        – remove espaços no início e no fim
#   2. replace('"')   – remove aspas que possam ter chegado do shlex
#   3. re.sub(\s+)    – colapsa múltiplos espaços internos num só
#   4. lower().title()– converte para Title Case  (ex: "fruta" → "Fruta")
#
# Exemplos:
#   "  oCeAn pOlluTion  " → "Ocean Pollution"
#   '"Electrodomésticos  Pequenos"' → "Electrodomésticos Pequenos"
# -----------------------------------------------------------------------
def normalizar_nome(nome):
    # 1. Remove espaços nas extremidades
    nome = nome.strip()

    # 2. Remove aspas duplas e simples (podem vir do parsing shlex)
    nome = nome.replace('"', '').replace("'", '')

    # 3. Colapsa múltiplos espaços consecutivos num único espaço
    nome = re.sub(r'\s+', ' ', nome)

    # 4. Converte para Title Case: primeira letra de cada palavra em maiúscula
    return nome.lower().title()
