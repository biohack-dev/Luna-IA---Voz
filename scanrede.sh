#!/bin/bash

function relatorio_disp() {

  local dispositivos=`nmap -sP 192.168.0.1/24 | tail -n1 | awk '{print $6}' | tr -d '()' `

  numero_dispositivos="Atualmente existem $dispositivos dispositivos conectados a sua rede."

  combina=$(echo $numero_dispositivos | tr -d '""')

  TXT_DISPOSITIVOS="$combina"
  
	echo "$combina"


}

relatorio_disp
