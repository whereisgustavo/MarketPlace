#!/bin/bash
# Gera todos os certificados SSL do projeto MarketCenter.
#
# Estrutura criada:
#   shared/certificados/ca.crt + ca.key         — Autoridade Certificadora partilhada
#   servidor/certificados/server1..10.crt + .key — 10 certificados de servidor
#   cliente/certificados/client.crt + .key       — Certificado do cliente
#
# Executar a partir da raiz do projeto:
#   bash gerar_certificados.sh

set -e

mkdir -p shared/certificados
mkdir -p servidor/certificados
mkdir -p cliente/certificados

echo "==> A gerar a Autoridade Certificadora (CA)..."
openssl genrsa -out shared/certificados/ca.key 2048
openssl req -x509 -new -nodes -key shared/certificados/ca.key -sha256 -days 365 \
    -out shared/certificados/ca.crt \
    -subj "/C=PT/ST=Lisboa/O=FCUL/CN=MarketCenter-CA"

echo "==> A gerar 10 certificados de servidor..."
for i in $(seq 1 10); do
    openssl genrsa -out servidor/certificados/server${i}.key 2048
    openssl req -new -nodes -key servidor/certificados/server${i}.key -sha256 -days 365 \
        -out servidor/certificados/server${i}.csr \
        -subj "/C=PT/ST=Lisboa/O=FCUL/CN=localhost"
    openssl x509 -req -sha256 -days 365 \
        -in  servidor/certificados/server${i}.csr \
        -CA  shared/certificados/ca.crt \
        -CAkey shared/certificados/ca.key \
        -CAcreateserial \
        -out servidor/certificados/server${i}.crt
    rm servidor/certificados/server${i}.csr
    echo "   server${i} criado."
done

echo "==> A gerar certificado do cliente..."
openssl genrsa -out cliente/certificados/client.key 2048
openssl req -new -nodes -key cliente/certificados/client.key -sha256 -days 365 \
    -out cliente/certificados/client.csr \
    -subj "/C=PT/ST=Lisboa/O=FCUL/CN=MarketCenter-Client"
openssl x509 -req -sha256 -days 365 \
    -in  cliente/certificados/client.csr \
    -CA  shared/certificados/ca.crt \
    -CAkey shared/certificados/ca.key \
    -CAcreateserial \
    -out cliente/certificados/client.crt
rm cliente/certificados/client.csr

echo ""
echo "==> Certificados gerados com sucesso:"
echo "    shared/certificados/ca.crt"
echo "    servidor/certificados/server1.crt .. server10.crt"
echo "    cliente/certificados/client.crt"
