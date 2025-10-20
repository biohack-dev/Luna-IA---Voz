#!/bin/bash

# Verifica se está rodando no Termux
if [ ! -d "/data/data/com.termux/files" ]; then
    echo "Este script foi desenvolvido para rodar no Termux."
    exit 1
fi

echo "=== Espaço em disco no Termux ==="

# Mostra informações do armazenamento do Termux (partição $HOME)
echo -e "\n[Armazenamento do Termux]"
df -h "$HOME" | awk 'NR==2 {print "Dispositivo: "$1"\nTamanho: "$2"\nUsado: "$3"\nLivre: "$4"\nUso: "$5}'

# Mostra informações do armazenamento interno (se configurado)
if [ -d "$HOME/storage/shared" ]; then
    echo -e "\n[Armazenamento Interno]"
    df -h "$HOME/storage/shared" | awk 'NR==2 {print "Dispositivo: "$1"\nTamanho: "$2"\nUsado: "$3"\nLivre: "$4"\nUso: "$5}'
else
    echo -e "\n[!] Armazenamento interno não configurado."
    echo "Execute 'termux-setup-storage' para configurar o acesso."
fi

# Mostra informações resumidas de todos os dispositivos
echo -e "\n[Resumo Geral]"
df -h | grep -v "tmpfs\|squashfs" | awk 'NR==1 {print $0} NR>1 {print $1,$2,$3,$4,$5,$6}'