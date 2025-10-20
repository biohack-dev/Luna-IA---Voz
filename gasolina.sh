#!/bin/bash

# URL da página
url="https://precos.petrobras.com.br/w/gasolina/sp"

# Baixa o conteúdo da página e extrai o valor do campo <p id="telafinal-precofinal">
preco=$(curl -s "$url" | grep -oP '(?<=<p class="h4 real-value" data-lfr-editable-type="text" data-lfr-editable-id="telafinal-precofinal" id="telafinal-precofinal">)[^<]+')

# Exibe o resultado
if [ -n "$preco" ]; then
    echo "Gasolina SP: R$ $preco"
else
    echo "Não foi possível obter o preço da gasolina."
fi
