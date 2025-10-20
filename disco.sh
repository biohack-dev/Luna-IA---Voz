#!/bin/bash

# Obtém as informações do disco onde está o diretório HOME
INFO_DISCO=$(df -h "$HOME" | tail -n1)

# Extrai cada campo separadamente
DISCO_ATUAL=$(echo "$INFO_DISCO" | awk '{print $1}')
TAMANHO=$(echo "$INFO_DISCO" | awk '{print $2}')
USADO=$(echo "$INFO_DISCO" | awk '{print $3}')
LIVRE=$(echo "$INFO_DISCO" | awk '{print $4}')

# Exibe as informações formatadas
echo "Informações do disco:"
echo "---------------------"
echo "Tamanho total: $TAMANHO"
echo "Espaço usado: $USADO"
echo "Espaço livre: $LIVRE"


termux-tts-speak "informações de disco: Tamanho total: $TAMANHO, Espaço usado: $USADO, Espaço livre: $LIVRE"