#!/bin/bash
# Script de inicialização da Luna

PYTHON_SCRIPT="/etc/luna/luna.py"

if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "Erro: Arquivo principal $PYTHON_SCRIPT não encontrado!"
    echo "Arquivos disponíveis em /etc/luna/:"
    ls -la /etc/luna/
    exit 1
fi

# Executar o programa Python
cd /etc/luna
python3 "$PYTHON_SCRIPT" "$@"
