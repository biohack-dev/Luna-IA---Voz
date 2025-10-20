#!/data/data/com.termux/files/usr/bin/bash

# Obtém a hora local formatada
hora=$(LC_TIME=pt_BR.UTF-8 date +"%H:%M Minutos ")

# Obtém o status da bateria
bateria=$(termux-battery-status | jq -r ".percentage")

# Cria a string formatada para TTS
clima_string="Agora são $hora. Nível da bateria em $bateria por cento."

#echo "$clima_string"

# Opcional: Fala o texto usando o TTS do Termux
termux-tts-speak "$clima_string"
