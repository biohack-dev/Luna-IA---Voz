#!/data/data/com.termux/files/usr/bin/bash

# Baixa os dados do clima
curl -s "http://apiadvisor.climatempo.com.br/api/v1/weather/locale/4290/current?token=32e6ad73da4248ca01a2d358d796b5dc" -o ~/clima.json

# Obtém a hora local formatada
hora=$(LC_TIME=pt_BR.UTF-8 date +"%H horas e %M minutos")

# Obtém o status da bateria
bateria=$(termux-battery-status | jq -r ".percentage")

# Extrai os dados do clima
cidade=$(cat ~/clima.json | jq -r ".name")
temperatura=$(cat ~/clima.json | jq -r ".data.temperature")
vento_vel=$(cat ~/clima.json | jq -r ".data.wind_velocity")
vento_dir=$(cat ~/clima.json | jq -r ".data.wind_direction")
umidade=$(cat ~/clima.json | jq -r ".data.humidity")
pressao_hpa=$(cat ~/clima.json | jq -r ".data.pressure")

# Converte pressão para bares (1 hPa = 0.001 bar)
pressao_bar=$(echo "scale=3; $pressao_hpa / 1000" | bc | sed 's/^\./0./')

# Mapeamento completo das direções do vento
declare -A direcoes_vento=(
    ["N"]="Norte"
    ["NNE"]="Norte-Nordeste"
    ["NE"]="Nordeste"
    ["ENE"]="Leste-Nordeste"
    ["E"]="Leste"
    ["ESE"]="Leste-Sudeste"
    ["SE"]="Sudeste"
    ["SSE"]="Sul-Sudeste"
    ["S"]="Sul"
    ["SSW"]="Sul-Sudoeste"
    ["SW"]="Sudoeste"
    ["WSW"]="Oeste-Sudoeste"
    ["W"]="Oeste"
    ["WNW"]="Oeste-Noroeste"
    ["NW"]="Noroeste"
    ["NNW"]="Norte-Noroeste"
)

# Converte direção do vento para texto completo
vento_dir_texto=${direcoes_vento[$vento_dir]}
if [ -z "$vento_dir_texto" ]; then
    vento_dir_texto="$vento_dir" # Usa a sigla se não encontrar no mapeamento
fi

# Cria a string formatada para TTS
clima_string="Agora são $hora. Clima em $cidade: Temperatura de $temperatura graus. Vento $vento_dir_texto a $vento_vel quilômetros por hora. Umidade do ar em $umidade por cento. Pressão atmosférica de $pressao_hpa Bares. Nível da bateria em $bateria por cento."

echo "$clima_string"

# Opcional: Fala o texto usando o TTS do Termux
termux-tts-speak "$clima_string"