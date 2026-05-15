"""
AD - Aplicações Distribuídas
Ano Letivo 2025/2026
Projeto - Fase 3

Grupo: 39

Elementos do Grupo:
- Diogo Silva (64143)
- Gustavo Santos (64167)

Descrição:
Ficheiro centralizado para configuração SSL/TLS do projeto.

Estrutura dos certificados:
  shared/certificados/ca.crt          — certificado da CA (partilhado por cliente e servidor)
  servidor/certificados/serverN.crt   — certificado do servidor N (N = 1 a 10)
  servidor/certificados/serverN.key   — chave privada do servidor N
  cliente/certificados/client.crt     — certificado do cliente (criado mas não usado na fase 3)
  cliente/certificados/client.key     — chave privada do cliente
"""

import ssl

CA_CERT          = 'shared/certificados/ca.crt'
SERVER_CERTS_DIR = 'servidor/certificados'
CLIENT_CERTS_DIR = 'cliente/certificados'


def criar_contexto_servidor(num_cert=1):
    """
    Cria o contexto SSL para o lado servidor.
    Carrega o certificado e a chave privada do servidor N.
    """
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(
        certfile=f'{SERVER_CERTS_DIR}/server{num_cert}.crt',
        keyfile=f'{SERVER_CERTS_DIR}/server{num_cert}.key'
    )
    return context


def criar_contexto_cliente():
    """
    Cria o contexto SSL para o lado cliente.
    Carrega o certificado da CA para verificar o servidor.

    Nota: check_hostname está desativado para compatibilidade com o ambiente
    de laboratório, onde o nome da máquina pode não coincidir com o CN do
    certificado. O professor confirmou que isto é esperado durante a demonstração.
    """
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.load_verify_locations(cafile=CA_CERT)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_REQUIRED
    return context
