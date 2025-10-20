#!/bin/bash
#
#===============================================================================
#
# File...........: myip.sh
# Title..........: MyIP
# Program........: Shell Code -  GNU/Linux
#
# Description....: Pega o IP publico da rede
#
# Copyright......: Copyright(c) 2024 / @Diego.Casagranda - HackLab
# License........: GNU GENERAL PUBLIC LICENSE - Version 3, 29 June 2007
#
# Author.........: Diego Casagranda
# E-Mail.........: diego.casagranda@mail.ru
#
# Dependency.....: curl
#
# Date...........: 05/06/2024
# Update.........: None
#
# Version........: 0.1.0
#
#===============================================================================
#
# ###########
# # History #
# ###########
#
#     05/06/2024 : Criação do do codigo
#
#===============================================================================

# Pega o IP publico no site checkip.dyndns.org
myip="$(curl -s checkip.dyndns.org | sed -e 's/.*Current IP Address: //' -e 's/<.*$//')"

# Exibe na tela o IP
echo "$myip"
